"""
AI Academic Advisor Service for EduGrade AI.
Provides intelligent academic recommendations, customized study plans,
and CGPA improvement guidance using student's actual performance data.
Supports Groq Cloud (primary LLM), OpenAI (secondary fallback), and a
built-in deterministic academic intelligence fallback (English & Tamil).
"""

import os
import json
import logging
import urllib.request
import urllib.error
from .academic_service import plan_target_cgpa, check_placement_eligibility

logger = logging.getLogger(__name__)


def call_chat_completion(base_url: str, api_key: str, model: str, messages: list, timeout: int = 15) -> str:
    """
    Executes an OpenAI-compatible chat completion HTTP request via urllib.
    Used for both Groq Cloud and OpenAI providers without external SDK dependencies.
    """
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 600
    }).encode('utf-8')

    req = urllib.request.Request(
        base_url,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode('utf-8')
        data = json.loads(body)
        choices = data.get('choices', [])
        if not choices:
            raise ValueError("Invalid completion response: 'choices' list missing or empty")
        content = choices[0].get('message', {}).get('content', '')
        content_clean = content.strip() if isinstance(content, str) else ''
        if not content_clean:
            raise ValueError("Empty completion content received from provider")
        return content_clean


def generate_ai_advice(student_profile, user_message: str) -> dict:
    """
    Generates academic guidance grounded in student records.
    Provider Order:
      1. Groq Cloud (if GROQ_API_KEY is set)
      2. OpenAI (if OPENAI_API_KEY is set)
      3. Built-in deterministic academic advisor (fallback)
    """
    msg_clean = user_message.strip()
    msg_lower = msg_clean.lower()

    # Detect Tamil query
    is_tamil = any('\u0b80' <= char <= '\u0bff' for char in msg_clean) or 'tamil' in msg_lower

    # Check if student has published results
    has_results = False
    weakest_courses = []
    weak_subjects = []
    strong_subjects = []
    company_eligibility_notes = []
    dept = student_profile.department if student_profile and student_profile.department else 'Engineering'
    curr_sem = student_profile.current_semester if student_profile and student_profile.current_semester else 1
    cgpa = float(student_profile.current_cgpa) if student_profile and student_profile.current_cgpa else 0.0
    target_cgpa = float(student_profile.target_cgpa) if student_profile and student_profile.target_cgpa else 8.50
    completed_cr = float(student_profile.credits_earned) if student_profile and student_profile.credits_earned else 0.0
    backlogs = int(student_profile.backlogs_count) if student_profile and student_profile.backlogs_count else 0

    if student_profile:
        from core.models import CourseResult, CompanyPlacementCriteria
        courses_qs = CourseResult.objects.filter(student=student_profile)
        if courses_qs.exists():
            weak_qs = courses_qs.order_by('grade_point', 'credits')[:3]
            for c in weak_qs:
                weakest_courses.append(f"{c.course_code}: {c.course_name} (Grade: {c.grade})")
                weak_subjects.append(c.course_name)

        if hasattr(student_profile, 'subject_insights'):
            for insight in student_profile.subject_insights.all():
                if insight.status_label == 'Needs attention' or float(insight.grade_point) < 7.0:
                    weak_subjects.append(insight.subject_name)
                    if not weakest_courses:
                        weakest_courses.append(insight.subject_name)
                elif insight.status_label == 'Strong' or float(insight.grade_point) >= 8.5:
                    strong_subjects.append(insight.subject_name)

        has_results = bool(
            courses_qs.exists()
            or (hasattr(student_profile, 'subject_insights') and student_profile.subject_insights.exists())
            or (float(student_profile.current_cgpa) > 0 or float(student_profile.credits_earned) > 0)
        )

        active_companies = list(CompanyPlacementCriteria.objects.filter(is_active=True).order_by('-package_lpa'))
        if active_companies and has_results:
            evaluated = check_placement_eligibility(student_profile, active_companies)
            for comp in evaluated[:5]:
                status_lbl = "Eligible" if comp['is_eligible'] else "Not Eligible"
                company_eligibility_notes.append(f"{comp['company_name']}: {status_lbl}")

        top_next_move_sentence = ""
        try:
            from core.services.twin_service import rank_next_moves
            moves = rank_next_moves(student_profile, assumed_grade="B")
            if moves and len(moves) > 0:
                top_next_move_sentence = moves[0].get("sentence", "")
        except Exception:
            top_next_move_sentence = ""

    # Build student academic context block for AI advisor prompt.
    # Data privacy: personal fields (name, roll number, email, username) are not sent to Groq/OpenAI.
    # Note: the student's own chat text is sent as typed.
    if has_results:
        student_data_text = (
            f"Department: {dept}\n"
            f"Current Semester: {curr_sem}\n"
            f"Current CGPA: {cgpa:.2f}\n"
            f"Target CGPA: {target_cgpa:.2f}\n"
            f"Total Credits Earned: {int(completed_cr)}\n"
            f"Active Backlogs: {backlogs}\n"
            f"Weakest Courses: {', '.join(weakest_courses) if weakest_courses else 'None'}\n"
            f"Top Next Move: {top_next_move_sentence if top_next_move_sentence else 'None'}\n"
            f"Recruiter Eligibility: {', '.join(company_eligibility_notes) if company_eligibility_notes else 'Pending verification'}"
        )
    else:
        student_data_text = (
            f"Department: {dept}\n"
            f"Current Semester: {curr_sem}\n"
            f"Academic Performance: No results available yet."
        )

    # Build system instructions
    lang_instruction = "Reply in Tamil if the student's latest message is in Tamil (Unicode range U+0B80-U+0BFF) or asks for Tamil, otherwise reply in English."
    system_instruction = (
        "You are an academic advisor for an engineering student. "
        "Use ONLY the student data given below. Never invent marks, credits, rules, or criteria. "
        "Do not recalculate CGPA/SGPA (use the given values). "
        "Answer in simple language in under 120 words with clear steps. "
        "AI advice is guidance, not an official decision. "
        f"{lang_instruction}\n"
        "If the student asks for a study plan for their weakest subject, provide a 4-week structured plan "
        "(Week 1, Week 2, Week 3, Week 4) in 4 short lines.\n\n"
        f"--- STUDENT DATA ---\n{student_data_text}"
    )

    # Construct chat payload with role separation
    llm_messages = [{"role": "system", "content": system_instruction}]

    if student_profile and getattr(student_profile, 'user', None):
        from core.models import AdvisorChatMessage
        recent_chats = list(AdvisorChatMessage.objects.filter(user=student_profile.user).order_by('-timestamp')[:6])
        recent_chats.reverse()
        for c in recent_chats:
            role = "user" if c.sender == 'user' else "assistant"
            llm_messages.append({"role": role, "content": c.message})

    llm_messages.append({"role": "user", "content": msg_clean})

    # Provider 1: Groq Cloud
    groq_key = os.getenv('GROQ_API_KEY', '').strip()
    groq_model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile').strip()
    try:
        groq_timeout = int(os.getenv('GROQ_TIMEOUT_SECONDS', '15'))
    except (ValueError, TypeError):
        groq_timeout = 15

    if groq_key:
        try:
            content = call_chat_completion(
                base_url="https://api.groq.com/openai/v1/chat/completions",
                api_key=groq_key,
                model=groq_model,
                messages=llm_messages,
                timeout=groq_timeout
            )
            return {'response': content, 'source': 'groq', 'context_used': True}
        except urllib.error.HTTPError as err:
            logger.warning(f"Groq API call failed: HTTP {err.code} {err.reason}")
        except urllib.error.URLError as err:
            reason_name = type(err.reason).__name__ if hasattr(err, 'reason') else type(err).__name__
            logger.warning(f"Groq API call failed: Connection error {reason_name}")
        except Exception as err:
            logger.warning(f"Groq API call failed: {type(err).__name__}")

    # Provider 2: OpenAI (optional secondary)
    openai_key = os.getenv('OPENAI_API_KEY', '').strip()
    if openai_key:
        try:
            content = call_chat_completion(
                base_url="https://api.openai.com/v1/chat/completions",
                api_key=openai_key,
                model="gpt-4o-mini",
                messages=llm_messages,
                timeout=groq_timeout
            )
            return {'response': content, 'source': 'openai', 'context_used': True}
        except urllib.error.HTTPError as err:
            logger.warning(f"OpenAI API call failed: HTTP {err.code} {err.reason}")
        except urllib.error.URLError as err:
            reason_name = type(err.reason).__name__ if hasattr(err, 'reason') else type(err).__name__
            logger.warning(f"OpenAI API call failed: Connection error {reason_name}")
        except Exception as err:
            logger.warning(f"OpenAI API call failed: {type(err).__name__}")

    # Provider 3: Built-in deterministic academic advisor fallback
    # If no results published yet:
    if not has_results:
        if is_tamil:
            reply = "தேர்வு முடிவுகள் இன்னும் வெளியிடப்படவில்லை. முடிவுகள் வந்ததும் வழிகாட்டுதல் கிடைக்கும்."
        else:
            reply = "Exam results have not been published yet. Guidance will appear once results are available."
        return {'response': reply, 'source': 'rule_based', 'context_used': False, 'language': 'ta' if is_tamil else 'en'}

    # Weakest Subject Study Plan Request Handling
    weakest_name = weak_subjects[0] if weak_subjects else (weakest_courses[0] if weakest_courses else "Core Fundamentals")
    is_weak_plan_request = (
        'weakest' in msg_lower
        or 'weak subject' in msg_lower
        or 'பலவீனமான' in msg_clean
        or ('study plan' in msg_lower and ('weak' in msg_lower or 'subject' in msg_lower or 'lowest' in msg_lower))
        or 'படிப்புத் திட்டம்' in msg_clean
    )
    if is_weak_plan_request:
        if is_tamil:
            plan_text = (
                f"{weakest_name} 4 வார திட்டம்:\n"
                f"• வாரம் 1: அடிப்படை கருத்துகள் மற்றும் சூத்திரங்கள்.\n"
                f"• வாரம் 2: கணக்கீடுகள் மற்றும் வரைபட பயிற்சி.\n"
                f"• வாரம் 3: முந்தைய ஆண்டு வினாத்தாள்கள் பயிற்சி.\n"
                f"• வாரம் 4: மாதிரி தேர்வுகள் மற்றும் திருப்புதல்."
            )
        else:
            plan_text = (
                f"4-Week Study Plan for {weakest_name}:\n"
                f"• Week 1: Fundamentals and definitions.\n"
                f"• Week 2: Analytical problem solving.\n"
                f"• Week 3: Previous exam paper practice.\n"
                f"• Week 4: Mock tests and final revision."
            )
        return {'response': plan_text, 'source': 'rule_based', 'context_used': True, 'language': 'ta' if is_tamil else 'en'}

    # Calculate real target plan
    plan = plan_target_cgpa(
        current_cgpa=cgpa,
        completed_credits=completed_cr,
        target_cgpa=target_cgpa,
        remaining_semesters=max(1, 8 - (curr_sem or 1))
    )

    weak_msg = f" Focus on {', '.join(weak_subjects)}." if weak_subjects else (f" Focus on {weakest_courses[0]}." if weakest_courses else "")

    if is_tamil:
        if 'cgpa' in msg_lower or 'mark' in msg_lower or 'மதிப்பெண்' in msg_lower:
            next_line = f" அடுத்த நடவடிக்கை: {top_next_move_sentence}" if top_next_move_sentence else ""
            reply = f"CGPA: {cgpa:.2f}, இலக்கு: {target_cgpa:.2f}. {plan['message']}{weak_msg}{next_line}"
        elif 'placement' in msg_lower or 'வேலை' in msg_lower:
            reply = f"வேலைவாய்ப்பு தகுதி: CGPA {cgpa:.2f}, {backlogs} அரியர்ஸ். {'தகுதி உண்டு.' if backlogs == 0 and cgpa >= 7.0 else 'அரியர்களை கிளியர் செய்யவும்.'}"
        else:
            reply = f"செமஸ்டர் {curr_sem}: CGPA {cgpa:.2f}. CGPA மற்றும் வேலைவாய்ப்பு ஆலோசனைகளை கேட்கலாம்."
        return {'response': reply, 'source': 'rule_based', 'language': 'ta', 'context_used': True}

    # English Responses
    if 'plan' in msg_lower or 'study' in msg_lower or 'schedule' in msg_lower:
        reply = f"Semester {curr_sem} Plan: {plan['message']}{weak_msg}"
    elif 'cgpa' in msg_lower or 'grade' in msg_lower or 'target' in msg_lower:
        next_move_line = f" Next Move: {top_next_move_sentence}." if top_next_move_sentence else ""
        reply = f"Current CGPA: {cgpa:.2f}, Target: {target_cgpa:.2f}. {plan['message']}{next_move_line}{weak_msg}"
    elif 'placement' in msg_lower or 'job' in msg_lower or 'company' in msg_lower or 'interview' in msg_lower:
        status_txt = "Eligible for tier-1 drives." if backlogs == 0 and cgpa >= 7.0 else f"{backlogs} active backlogs. Clear arrears to qualify."
        reply = f"Placement: CGPA {cgpa:.2f}, {backlogs} backlogs. {status_txt}"
    elif 'hello' in msg_lower or 'hi' in msg_lower or 'hey' in msg_lower:
        reply = f"Hello! Semester {curr_sem} records loaded (CGPA: {cgpa:.2f}). Ask about CGPA, study plans, or placements."
    else:
        reply = f"Semester {curr_sem} (CGPA {cgpa:.2f}): {plan['message']}{weak_msg}"

    return {'response': reply, 'source': 'rule_based', 'context_used': True, 'language': 'en'}

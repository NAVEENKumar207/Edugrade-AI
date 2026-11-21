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
        "You are a friendly academic advisor for an engineering college student. "
        "Use ONLY the student data given below. Never invent marks, credits, rules, company criteria or policies. "
        "Do not recalculate CGPA/SGPA (use the given values). "
        "Answer in simple language in under 200 words with clear steps. "
        f"{lang_instruction}\n"
        "If the student asks for a study plan for their weakest subject, provide a 4-week structured plan "
        "(Week 1: Fundamentals, Week 2: Core Concepts, Week 3: Practice, Week 4: Mock Tests & Revision) "
        "tailored to that course.\n\n"
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
            reply = (
                "வணக்கம்! உங்கள் தேர்வு முடிவுகள் இன்னும் வெளியிடப்படவில்லை. "
                "முடிவுகள் வெளியிடப்பட்டவுடன் உங்கள் CGPA மற்றும் பாடவாரியான ஆலோசனை வழங்கப்படும்."
            )
        else:
            reply = (
                "Hello! Your semester examination results have not been published yet. "
                "Once results are published, personalized CGPA planning and academic guidance will be available here."
            )
        return {'response': reply, 'source': 'rule_based', 'context_used': False, 'language': 'ta' if is_tamil else 'en'}

    # Weakest Subject Study Plan Request Handling
    weakest_name = weak_subjects[0] if weak_subjects else (weakest_courses[0] if weakest_courses else "Core Engineering Fundamentals")
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
                f"### {weakest_name} பாடத்திற்கான 4 வார சிறப்பு படிப்புத் திட்டம்\n\n"
                f"**வாரம் 1 — அடிப்படை கோட்பாடுகள் மற்றும் அறிமுகம்**\n"
                f"• அலகு 1 மற்றும் 2-ன் முக்கிய கோட்பாடுகள், அடிப்படை வரையறைகள் மற்றும் சூத்திரங்களை ஆழமாக படிக்கவும்.\n"
                f"• தினமும் 90 நிமிடங்கள் ஒதுக்கி முக்கிய குறிப்புகளை (Short Notes) எழுதி பழகவும்.\n\n"
                f"**வாரம் 2 — பகுப்பாய்வு மற்றும் சிக்கல் தீர்க்கும் பயிற்சி**\n"
                f"• அலகு 3 மற்றும் 4-ல் உள்ள கணக்குகள், வரைபடங்கள் மற்றும் அல்காரிதம்களை வரைந்து பயிற்சி பெறவும்.\n"
                f"• முந்தைய அசைன்மென்ட் வினாக்களை சுயமாக தீர்க்க முயற்சி செய்யவும்.\n\n"
                f"**வாரம் 3 — முந்தைய ஆண்டு தேர்வு வினாத்தாள்கள் பயிற்சி**\n"
                f"• கடந்த 5 ஆண்டுகால பல்கலைக்கழக வினாத்தாள்களை ஆராய்ந்து, அடிக்கடி கேட்கப்படும் 13 மற்றும் 16 மதிப்பெண் வினாக்களை பயிற்சி செய்யவும்.\n"
                f"• நேரக் கட்டுப்பாட்டுடன் மாதிரி வினாக்களுக்கு விடையளித்துப் பழகவும்.\n\n"
                f"**வாரம் 4 — இறுதி திருப்புதல் மற்றும் மாதிரித் தேர்வுகள்**\n"
                f"• அனைத்து 5 அலகுகளையும் முழுமையாக திருப்புதல் (Revision) செய்து மாதிரித் தேர்வுகள் எழுதவும்.\n"
                f"• சூத்திரங்கள் மற்றும் வரைபடங்களை நினைவுகூர்ந்து தேர்வுக்கு முழுமையாக தயாராகுங்கள்."
            )
        else:
            plan_text = (
                f"### 4-Week Targeted Study Plan for {weakest_name}\n\n"
                f"**Week 1 — Core Fundamentals & Foundation Review**\n"
                f"• Review syllabus Units 1 & 2; master fundamental definitions and core concepts.\n"
                f"• Dedicate 90 minutes daily to reading standard textbook chapters and making formula flashcards.\n\n"
                f"**Week 2 — Analytical Problem Solving & Assignments**\n"
                f"• Focus on Units 3 & 4 with emphasis on derivations, numerical problems, and architectural diagrams.\n"
                f"• Solve end-of-chapter practice problems and write out step-by-step algorithms.\n\n"
                f"**Week 3 — Past University Papers & Exam Simulation**\n"
                f"• Work through 5 previous years' university examination papers; prioritize high-weightage 13-mark questions.\n"
                f"• Practice writing answers under timed exam conditions (45 minutes per section).\n\n"
                f"**Week 4 — Final Revision & Rapid Recall Drills**\n"
                f"• Conduct 2 complete mock tests covering all 5 syllabus units; identify remaining weak spots.\n"
                f"• Review formula cheat sheets and key diagrams for confident exam execution."
            )
        return {'response': plan_text, 'source': 'rule_based', 'context_used': True, 'language': 'ta' if is_tamil else 'en'}

    # Calculate real target plan
    plan = plan_target_cgpa(
        current_cgpa=cgpa,
        completed_credits=completed_cr,
        target_cgpa=target_cgpa,
        remaining_semesters=max(1, 8 - (curr_sem or 1))
    )

    weak_msg = f" Specifically focus on {', '.join(weak_subjects)} where your grade points were lower." if weak_subjects else (f" Specifically focus on {weakest_courses[0]}." if weakest_courses else "")

    if is_tamil:
        if 'cgpa' in msg_lower or 'mark' in msg_lower or 'மதிப்பெண்' in msg_lower:
            reply = (
                f"வணக்கம்! உங்கள் தற்போதைய CGPA {cgpa:.2f} ஆகும். இலக்கு CGPA {target_cgpa:.2f} அடைய "
                f"{plan['message']} அடுத்த செமஸ்டர்களில் கடின உழைப்புடன் படியுங்கள்.{weak_msg}"
            )
        elif 'placement' in msg_lower or 'வேலை' in msg_lower:
            reply = (
                f"கேம்பஸ் வேலைவாய்ப்பு (Placement): உங்கள் தற்போதைய CGPA {cgpa:.2f}. "
                f"{'அரியர்ஸ் இல்லாததால் நீங்கள் பெரும்பாலான முன்னணி நிறுவனங்களுக்கு தகுதி பெற்றுள்ளீர்கள்!' if backlogs == 0 else f'தற்போது {backlogs} அரியர் உள்ளது, உடனடியாக கிளியர் செய்யவும்.'} "
                f"LeetCode, DSA மற்றும் பைதான்/SQL பயிற்சிகளில் கவனம் செலுத்துங்கள்."
            )
        else:
            reply = (
                "வணக்கம்! நான் உங்கள் EduGrade AI கல்வி ஆலோசகர். உங்கள் கல்வி முன்னேற்றம், CGPA திட்டமிடல் "
                "மற்றும் வேலைவாய்ப்பு தகுதிகளுக்கு உதவ நான் தயாராக உள்ளேன். எதைப் பற்றி அறிய விரும்புகிறீர்கள்?"
            )
        return {'response': reply, 'source': 'rule_based', 'language': 'ta', 'context_used': True}

    # English Responses
    if 'plan' in msg_lower or 'study' in msg_lower or 'schedule' in msg_lower:
        reply = (
            f"Here is your personalized academic action plan for Semester {curr_sem}:\n\n"
            f"1. **Target Milestone**: {plan['message']}\n"
            f"2. **Priority Remediation**: Dedicate 4-5 hours weekly to core theory concepts.{weak_msg}\n"
            f"3. **Weekly Routine**: Mon-Wed: Core fundamentals; Thu-Fri: Lab & Coding assignments; Sat: Review & mock tests."
        )
    elif 'cgpa' in msg_lower or 'grade' in msg_lower or 'target' in msg_lower:
        reply = (
            f"Academic Performance Analysis:\n\n"
            f"• Current CGPA: **{cgpa:.2f}**\n"
            f"• Target Goal: **{target_cgpa:.2f}**\n"
            f"• Assessment: {plan['message']}\n"
            f"{weak_msg}\n\n"
            f"To achieve this, maintain consistent test performance and aim for at least 8.5+ SGPA in all remaining courses."
        )
    elif 'placement' in msg_lower or 'job' in msg_lower or 'company' in msg_lower or 'interview' in msg_lower:
        eligibility_note = "You have 0 active backlogs and meet the criteria for leading tier-1 recruitment drives." if backlogs == 0 else f"You currently have {backlogs} active backlog. Clearing this in the immediate arrear exam should be your highest priority."
        reply = (
            f"Placement Readiness Report:\n\n"
            f"• Current CGPA: **{cgpa:.2f}** (Status: {'Placement Eligible' if cgpa >= 7.0 and backlogs == 0 else 'Needs Review'})\n"
            f"• Arrears / Backlogs: **{backlogs}**\n"
            f"• {eligibility_note}\n\n"
            f"Recommendations:\n"
            f"1. Practice at least 2 LeetCode Medium problems daily.\n"
            f"2. Strengthen Database Management and System Design concepts.\n"
            f"3. Build 2 production-grade full-stack projects showcasing real-world problem-solving."
        )
    elif 'hello' in msg_lower or 'hi' in msg_lower or 'hey' in msg_lower:
        reply = (
            f"Hello! I am your EduGrade AI Academic Advisor. "
            f"I have synchronized your Semester {curr_sem} records (CGPA: {cgpa:.2f}). "
            f"Ask me about CGPA planning, weak subject remediation, weekly study schedules, or placement eligibility!"
        )
    else:
        reply = (
            f"Based on your Semester {curr_sem} record (CGPA {cgpa:.2f}), {plan['message']}"
            f"{weak_msg} Feel free to ask for a custom study timetable, placement criteria breakdown, or subject improvement tips."
        )

    return {'response': reply, 'source': 'rule_based', 'context_used': True, 'language': 'en'}

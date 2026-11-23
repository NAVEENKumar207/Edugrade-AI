"""
Industry Skill Mapping and Corporate Fit Analytics Service for EduGrade AI.
Computes credit-weighted academic skill scores, company skill match percentages,
gap identification, and overall career readiness classification.
"""

from core.models import UserProfile, CourseResult, CompanyPlacementCriteria, CourseSkillMap
from core.services.academic_service import FAILING_GRADES

KEYWORD_SKILL_RULES = [
    (["data structure", "dsa", "algorithm"], "DSA"),
    (["database", "dbms", "sql", "rdbms"], "DBMS"),
    (["operating system", "os", "unix", "linux"], "OS"),
    (["network", "computer network", "tcp/ip"], "Networks"),
    (["python", "programming in python"], "Python"),
    (["web", "html", "javascript", "full stack", "internet programming"], "Web"),
    (["math", "calculus", "linear algebra", "discrete", "probability", "statistics"], "Maths"),
    (["cloud", "distributed", "aws", "azure"], "Cloud"),
    (["ai", "machine learning", "deep learning", "artificial intelligence"], "AI/ML"),
]

def _match_keywords_for_title(course_name: str) -> list:
    """Matches course title keywords to standard technical skills."""
    matched = []
    name_lower = (course_name or "").lower()
    for keywords, skill_name in KEYWORD_SKILL_RULES:
        if any(kw in name_lower for kw in keywords):
            matched.append(skill_name)
    return matched

def get_skills_for_course(course_code: str, course_name: str = "") -> list:
    """
    Returns mapped skills for a given course code.
    Uses CourseSkillMap database table if mappings exist; otherwise falls back to title keywords.
    """
    db_mappings = CourseSkillMap.objects.filter(course_code__iexact=course_code.strip())
    if db_mappings.exists():
        return list(db_mappings.values_list('skill', flat=True))
    return _match_keywords_for_title(course_name)

def skill_scores(student_profile) -> dict:
    """
    Calculates credit-weighted average grade points of latest results for mapped courses,
    scaled 0-100 per skill.
    Returns: dict of skill_name -> {score, avg_grade_point, total_credits, courses}
    """
    if not student_profile:
        return {}

    # Gather latest result per course
    courses = CourseResult.objects.filter(
        student=student_profile
    ).order_by('semester_number', 'id')

    latest_courses = {}
    for c in courses:
        code = c.course_code.strip().upper()
        latest_courses[code] = c

    # Group results under each skill
    skill_buckets = {}
    has_db_mappings = CourseSkillMap.objects.exists()

    for c in latest_courses.values():
        code = c.course_code.strip().upper()
        if has_db_mappings:
            db_skills = list(CourseSkillMap.objects.filter(course_code__iexact=code).values_list('skill', flat=True))
            c_skills = db_skills if db_skills else _match_keywords_for_title(c.course_name)
        else:
            c_skills = _match_keywords_for_title(c.course_name)

        for sk in c_skills:
            if sk not in skill_buckets:
                skill_buckets[sk] = []
            skill_buckets[sk].append(c)

    results = {}
    for sk, clist in skill_buckets.items():
        total_credits = sum(float(c.credits) for c in clist)
        total_points = sum(float(c.credits) * float(c.grade_point) for c in clist)
        avg_gp = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
        score = round((avg_gp / 10.0) * 100.0, 1)

        results[sk] = {
            "skill": sk,
            "score": score,
            "avg_grade_point": avg_gp,
            "total_credits": int(total_credits),
            "courses": [
                {
                    "course_code": c.course_code,
                    "course_name": c.course_name,
                    "grade": c.grade,
                    "credits": c.credits,
                    "grade_point": float(c.grade_point)
                }
                for c in clist
            ]
        }

    return results

def company_skill_match(student_profile, company, scores=None) -> dict:
    """
    Compares student's acquired skill scores against corporate required skills.
    Identifies match percentage, weak skills (<60), and uncovered skills (no course evidence).
    """
    raw_req = company.required_skills or ""
    req_list = [s.strip() for s in raw_req.replace(';', ',').split(',') if s.strip()]

    if scores is None:
        scores = skill_scores(student_profile)
    scores_lookup = {k.lower(): v for k, v in scores.items()}

    # Skill name aliases for common technical terms
    aliases = {
        "sql": "dbms",
        "database": "dbms",
        "algorithms": "dsa",
        "data structures": "dsa",
        "operating systems": "os",
        "networking": "networks",
        "machine learning": "ai/ml",
        "mathematics": "maths",
    }

    covered_scores = []
    weak_skills = []
    uncovered_skills = []

    for req in req_list:
        key = req.lower()
        key = aliases.get(key, key)

        if key in scores_lookup:
            sk_data = scores_lookup[key]
            sc = sk_data["score"]
            covered_scores.append(sc)
            if sc < 60.0:
                weak_skills.append(req)
        else:
            uncovered_skills.append(req)

    if covered_scores:
        match_percent = round(sum(covered_scores) / len(covered_scores), 1)
    else:
        match_percent = 0.0

    return {
        "company_name": company.company_name,
        "role_title": company.role_title,
        "required_skills": req_list,
        "match_percent": match_percent,
        "weak_skills": weak_skills,
        "uncovered_skills": uncovered_skills
    }

def evaluate_placement_fit(student_profile, company, skill_match_res: dict) -> dict:
    """
    Combines corporate eligibility criteria and skill match into a unified fit status:
    'Ready', 'Almost', or 'Not yet'.
    """
    cgpa = float(student_profile.current_cgpa) if student_profile.current_cgpa else 0.0
    backlogs = int(student_profile.backlogs_count) if student_profile.backlogs_count else 0
    min_cgpa = float(company.min_cgpa)
    max_backlogs = company.max_backlogs
    match_pct = skill_match_res["match_percent"]

    is_eligible = (cgpa >= min_cgpa) and (backlogs <= max_backlogs)

    # Classification rules:
    # Ready: eligible AND match >= 70
    # Almost: (eligible and match < 70) OR (not eligible but within 0.5 CGPA or 1 backlog)
    # Not yet: otherwise
    cgpa_gap = round(min_cgpa - cgpa, 2)
    backlog_gap = backlogs - max_backlogs

    if is_eligible and match_pct >= 70.0:
        fit_label = "Ready"
        tip = f"Excellent fit! Profile meets all criteria ({cgpa:.2f} >= {min_cgpa:.2f}) with {match_pct}% skill alignment."
    elif is_eligible and match_pct < 70.0:
        fit_label = "Almost"
        tip = f"Academically eligible. Strengthen {', '.join(skill_match_res['weak_skills'] or skill_match_res['uncovered_skills'][:2])} to increase match beyond 70%."
    elif (cgpa >= min_cgpa - 0.50) and (backlog_gap <= 1):
        fit_label = "Almost"
        reasons = []
        if cgpa_gap > 0:
            reasons.append(f"needs +{cgpa_gap:.2f} CGPA")
        if backlog_gap > 0:
            reasons.append(f"clear {backlog_gap} arrear")
        tip = f"Close to eligibility ({', '.join(reasons)}). Skill alignment is at {match_pct}%."
    else:
        fit_label = "Not yet"
        tip = f"Significant gap: CGPA {cgpa:.2f} vs {min_cgpa:.2f} minimum, {backlogs} backlogs (max {max_backlogs})."

    return {
        "company_id": company.id,
        "company_name": company.company_name,
        "role_title": company.role_title,
        "min_cgpa": min_cgpa,
        "max_backlogs": max_backlogs,
        "package_lpa": float(company.package_lpa),
        "is_eligible": is_eligible,
        "fit_label": fit_label,
        "match_percent": match_pct,
        "weak_skills": skill_match_res["weak_skills"],
        "uncovered_skills": skill_match_res["uncovered_skills"],
        "improvement_tip": tip
    }

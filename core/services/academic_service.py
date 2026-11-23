"""
Academic Calculation Engine for EduGrade AI.
Provides deterministic, credit-weighted academic calculations, CGPA simulation,
placement eligibility assessment, and performance analytics.
"""

import math
from core.regulation import (
    INTERNAL_MAX,
    EXTERNAL_PAPER_MAX,
    EXTERNAL_WEIGHT,
    MIN_EXTERNAL_PERCENT,
    MIN_TOTAL_TO_PASS,
    GRADE_BOUNDARIES,
    marks_to_grade,
)

# Standard 10-Point Grade Scale Mapping
GRADE_POINT_MAP = {
    'O': 10.0,
    'A+': 9.0,
    'A': 8.0,
    'B+': 7.0,
    'B': 6.0,
    'C': 5.0,
    'U': 0.0,
    'RA': 0.0,
    'SA': 0.0,
    'W': 0.0,
}

FAILING_GRADES = {'U', 'RA', 'SA', 'W'}
VALID_GRADES = set(GRADE_POINT_MAP.keys())
GRADE_ORDER = ['O', 'A+', 'A', 'B+', 'B', 'C', 'U', 'RA', 'SA', 'W']

# At-risk academic intervention institutional thresholds
AT_RISK_CGPA_THRESHOLD = 6.0
AT_RISK_BACKLOG_THRESHOLD = 2
MIN_PASSING_GRADE_POINT = 5.0
MAX_GRADE_POINT = 10.0

def grade_to_point(grade_str: str) -> float:
    """Converts letter grade to numeric grade points."""
    clean = str(grade_str).strip().upper()
    return GRADE_POINT_MAP.get(clean, 0.0)

def calculate_sgpa(courses: list) -> dict:
    """
    Calculates credit-weighted Semester Grade Point Average (SGPA).
    courses: list of dicts with keys 'credits' (int/float) and 'grade_point' (float) or 'grade' (str).
    Formula: SGPA = sum(credits * grade_point) / sum(credits)
    """
    total_credits = 0.0
    total_credit_points = 0.0
    backlogs = 0

    for c in courses:
        cr = float(c.get('credits', 3.0))
        if 'grade_point' in c and c['grade_point'] is not None:
            gp = float(c['grade_point'])
        else:
            gp = grade_to_point(c.get('grade', 'U'))
            
        if gp == 0.0 or str(c.get('grade', '')).upper() in ['U', 'RA', 'SA']:
            backlogs += 1

        total_credits += cr
        total_credit_points += (cr * gp)

    sgpa = round(total_credit_points / total_credits, 2) if total_credits > 0 else 0.0
    return {
        'sgpa': sgpa,
        'total_credits': total_credits,
        'total_credit_points': round(total_credit_points, 2),
        'backlogs': backlogs
    }

def calculate_cgpa(semesters: list) -> dict:
    """
    Calculates Cumulative Grade Point Average (CGPA) from semester records.
    semesters: list of dicts with 'sgpa' and 'credits_earned'.
    Formula: CGPA = sum(sgpa * credits_earned) / sum(credits_earned)
    """
    total_credits = 0.0
    total_points = 0.0

    for s in semesters:
        cr = float(s.get('credits_earned', 0.0))
        sg = float(s.get('sgpa', 0.0))
        total_credits += cr
        total_points += (cr * sg)

    cgpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
    return {
        'cgpa': cgpa,
        'total_credits': total_credits,
        'total_points': round(total_points, 2)
    }

def plan_target_cgpa(current_cgpa: float, completed_credits: float, target_cgpa: float,
                      remaining_credits: float = None, remaining_semesters: int = 3,
                      degree_total_credits: float = 160.0) -> dict:
    """
    Evaluates target CGPA feasibility and calculates required average SGPA.
    Formula:
    Required SGPA = ((Target CGPA * Total Degree Credits) - (Current CGPA * Completed Credits)) / Remaining Credits
    Where Total Degree Credits = Completed Credits + Remaining Credits
    """
    errors = []

    # Safe numeric coercion
    try:
        current_cgpa = float(current_cgpa) if current_cgpa is not None else 0.0
    except (ValueError, TypeError):
        errors.append("Current CGPA must be a valid number.")
        current_cgpa = 0.0

    try:
        completed_credits = float(completed_credits) if completed_credits is not None else 0.0
    except (ValueError, TypeError):
        errors.append("Completed credits must be a valid number.")
        completed_credits = 0.0

    try:
        target_cgpa = float(target_cgpa) if target_cgpa is not None else 0.0
    except (ValueError, TypeError):
        errors.append("Target CGPA must be a valid number.")
        target_cgpa = 0.0

    try:
        remaining_semesters = int(remaining_semesters) if remaining_semesters is not None else 1
    except (ValueError, TypeError):
        errors.append("Remaining semesters must be a valid integer.")
        remaining_semesters = 1

    try:
        degree_total_credits = float(degree_total_credits) if degree_total_credits is not None else 160.0
    except (ValueError, TypeError):
        errors.append("Degree total credits must be a valid number.")
        degree_total_credits = 160.0

    parsed_rem_credits = None
    if remaining_credits is not None:
        try:
            parsed_rem_credits = float(remaining_credits)
            if parsed_rem_credits < 0.0:
                errors.append("Remaining credits cannot be negative.")
        except (ValueError, TypeError):
            errors.append("Remaining credits must be a valid number.")

    # Validation rules
    if current_cgpa < 0.0 or current_cgpa > 10.0:
        errors.append("Current CGPA must be between 0.00 and 10.00.")

    if target_cgpa < 0.0 or target_cgpa > 10.0:
        errors.append("Target CGPA must be between 0.00 and 10.00.")

    if completed_credits < 0.0:
        errors.append("Completed credits cannot be negative.")

    if degree_total_credits <= 0.0:
        errors.append("Total degree credits must be a positive number.")

    if completed_credits > degree_total_credits and degree_total_credits > 0.0:
        errors.append("Completed credits cannot exceed total degree credits.")

    if remaining_semesters <= 0:
        errors.append("Remaining semesters must be a valid positive integer.")

    if errors:
        return {
            'target_cgpa': target_cgpa,
            'current_cgpa': current_cgpa,
            'completed_credits': completed_credits,
            'remaining_credits': 0.0,
            'remaining_semesters': remaining_semesters,
            'required_average_sgpa': None,
            'max_achievable_cgpa': 0.0,
            'min_passing_cgpa': 0.0,
            'is_achievable': False,
            'status': 'invalid',
            'message': " ".join(errors),
            'scenarios': []
        }

    # Determine remaining credits and total degree credits
    if parsed_rem_credits is not None:
        remaining_credits = parsed_rem_credits
        total_credits = completed_credits + remaining_credits
    else:
        remaining_credits = max(0.0, float(degree_total_credits) - completed_credits)
        total_credits = completed_credits + remaining_credits

    # Guard against zero total credits
    if total_credits <= 0.0:
        total_credits = 160.0

    # Special handling when all credits are completed (zero remaining credits)
    if remaining_credits == 0.0:
        max_achievable_cgpa = round(current_cgpa, 2)
        min_passing_cgpa = round(current_cgpa, 2)
        is_achievable = current_cgpa >= target_cgpa
        status = 'already_achieved' if is_achievable else 'impossible'
        if is_achievable:
            message = (f"All {completed_credits:.0f} degree credits have been completed. "
                       f"Your final CGPA is {current_cgpa:.2f}, successfully achieving your target of {target_cgpa:.2f}.")
        else:
            message = (f"All {completed_credits:.0f} degree credits have been completed with a final CGPA of {current_cgpa:.2f}. "
                       f"There are no remaining credits available to improve or alter your final CGPA to reach {target_cgpa:.2f}.")

        scenarios = []
        for test_sg in [10.0, 9.5, 9.0, 8.5, 8.0, 7.5, 7.0]:
            scenarios.append({
                'future_average_sgpa': test_sg,
                'projected_final_cgpa': round(current_cgpa, 2),
                'meets_target': current_cgpa >= target_cgpa
            })

        return {
            'target_cgpa': target_cgpa,
            'current_cgpa': current_cgpa,
            'completed_credits': completed_credits,
            'remaining_credits': 0.0,
            'remaining_semesters': remaining_semesters,
            'required_average_sgpa': None,
            'max_achievable_cgpa': max_achievable_cgpa,
            'min_passing_cgpa': min_passing_cgpa,
            'is_achievable': is_achievable,
            'status': status,
            'message': message,
            'scenarios': scenarios
        }

    # Calculation with remaining credits > 0
    current_points = current_cgpa * completed_credits
    target_total_points = target_cgpa * total_credits
    required_points = target_total_points - current_points
    required_sgpa = required_points / remaining_credits

    # Maximum achievable CGPA if student scores 10.0 in every remaining credit
    max_achievable_points = current_points + (remaining_credits * 10.0)
    max_achievable_cgpa = min(10.0, round(max_achievable_points / total_credits, 2))

    # Minimum achievable CGPA if student scores passing 5.0 in every remaining credit
    min_passing_points = current_points + (remaining_credits * 5.0)
    min_passing_cgpa = round(min_passing_points / total_credits, 2)

    # Feasibility classification
    if target_cgpa <= current_cgpa:
        status = 'already_achieved'
        is_achievable = True
        required_avg = round(max(0.0, required_sgpa), 2)
        message = (f"Target CGPA {target_cgpa:.2f} has already been achieved! Your current CGPA is {current_cgpa:.2f}. "
                   f"Maintaining an average SGPA of {max(0.0, required_sgpa):.2f} or higher across your remaining "
                   f"{remaining_semesters} semesters ({remaining_credits:.0f} credits) will preserve or enhance your standing.")
    elif required_sgpa > 10.0:
        status = 'impossible'
        is_achievable = False
        required_avg = None
        message = (f"Target CGPA {target_cgpa:.2f} is mathematically unattainable. "
                   f"Even achieving a perfect 10.00 SGPA across all remaining {remaining_credits:.0f} credits "
                   f"yields a maximum possible CGPA of {max_achievable_cgpa:.2f}.")
    elif required_sgpa <= 5.0:
        status = 'easily_achievable'
        is_achievable = True
        required_avg = round(max(0.0, required_sgpa), 2)
        message = (f"Target CGPA {target_cgpa:.2f} is easily achievable! You only need to maintain an average "
                   f"SGPA of {max(0.0, required_sgpa):.2f} across your remaining {remaining_semesters} semesters "
                   f"({remaining_credits:.0f} credits).")
    else:
        status = 'feasible'
        is_achievable = True
        required_avg = round(required_sgpa, 2)
        message = (f"To graduate with a {target_cgpa:.2f} CGPA, you need an average SGPA of "
                   f"{required_sgpa:.2f} across the remaining {remaining_semesters} semesters "
                   f"({remaining_credits:.0f} credits).")

    # What-if scenario generator
    scenarios = []
    test_sgpas = [10.0, 9.5, 9.0, 8.5, 8.0, 7.5, 7.0]
    for test_sg in test_sgpas:
        proj_pts = current_points + (remaining_credits * test_sg)
        proj_cgpa = min(10.0, round(proj_pts / total_credits, 2))
        scenarios.append({
            'future_average_sgpa': test_sg,
            'projected_final_cgpa': proj_cgpa,
            'meets_target': proj_cgpa >= target_cgpa
        })

    return {
        'target_cgpa': target_cgpa,
        'current_cgpa': current_cgpa,
        'completed_credits': completed_credits,
        'remaining_credits': remaining_credits,
        'remaining_semesters': remaining_semesters,
        'required_average_sgpa': required_avg,
        'max_achievable_cgpa': max_achievable_cgpa,
        'min_passing_cgpa': min_passing_cgpa,
        'is_achievable': is_achievable,
        'status': status,
        'message': message,
        'scenarios': scenarios
    }

def required_marks(internal: float, target_grade: str) -> dict:
    """
    Calculates the minimum external paper marks needed to achieve target_grade.
    internal: internal marks out of INTERNAL_MAX (0-40).
    target_grade: 'O', 'A+', 'A', 'B+', 'B', 'C', or 'pass'.
    """
    try:
        internal_val = float(internal)
    except (TypeError, ValueError):
        raise ValueError(f"Internal marks must be a valid number between 0 and {INTERNAL_MAX}.")
    
    if internal_val < 0.0 or internal_val > INTERNAL_MAX:
        raise ValueError(f"Internal marks must be between 0 and {INTERNAL_MAX}.")

    clean_target = str(target_grade).strip().upper()
    valid_targets = ['O', 'A+', 'A', 'B+', 'B', 'C', 'PASS']
    if clean_target not in valid_targets:
        raise ValueError(f"Target grade must be one of: {', '.join(valid_targets)}.")

    if clean_target == 'PASS':
        needed_total = float(MIN_TOTAL_TO_PASS)
    else:
        needed_total = float(GRADE_BOUNDARIES[clean_target])

    required_paper = (needed_total - internal_val) / EXTERNAL_WEIGHT
    required_paper = max(required_paper, float(MIN_EXTERNAL_PERCENT))

    if required_paper > EXTERNAL_PAPER_MAX:
        max_possible_total = round(internal_val + (EXTERNAL_PAPER_MAX * EXTERNAL_WEIGHT), 1)
        best_grade = marks_to_grade(max_possible_total)
        return {
            "status": "impossible",
            "required_paper": None,
            "resulting_total": max_possible_total,
            "grade": best_grade,
            "best_grade": best_grade,
            "message": f"Target grade {clean_target} is impossible with internal score of {internal_val}. Best reachable grade with maximum paper marks ({EXTERNAL_PAPER_MAX}) is {best_grade} ({max_possible_total}/100)."
        }
    else:
        paper_score = int(math.ceil(required_paper))
        resulting_total = round(internal_val + (paper_score * EXTERNAL_WEIGHT), 1)
        res_grade = marks_to_grade(resulting_total)
        return {
            "status": "possible",
            "required_paper": paper_score,
            "resulting_total": resulting_total,
            "grade": res_grade,
            "message": f"You need at least {paper_score}/{EXTERNAL_PAPER_MAX} in the end-semester paper to achieve {res_grade} (resulting total: {resulting_total}/100)."
        }

def evaluate_expected_marks(internal: float, paper_marks: float) -> dict:
    """
    Evaluates final total and grade given internal marks and expected external paper marks.
    Enforces minimum external passing percent threshold.
    """
    try:
        internal_val = float(internal)
        paper_val = float(paper_marks)
    except (TypeError, ValueError):
        raise ValueError("Marks must be valid numbers.")

    if internal_val < 0.0 or internal_val > INTERNAL_MAX:
        raise ValueError(f"Internal marks must be between 0 and {INTERNAL_MAX}.")
    if paper_val < 0.0 or paper_val > EXTERNAL_PAPER_MAX:
        raise ValueError(f"External paper marks must be between 0 and {EXTERNAL_PAPER_MAX}.")

    total = round(internal_val + (paper_val * EXTERNAL_WEIGHT), 1)
    
    if paper_val < MIN_EXTERNAL_PERCENT:
        grade = "U"
        passed_external = False
        message = (
            f"Result is U (arrear) because external paper score ({paper_val:.1f}/{EXTERNAL_PAPER_MAX}) "
            f"is below the minimum passing threshold of {MIN_EXTERNAL_PERCENT}%, even though total is {total}."
        )
    else:
        grade = marks_to_grade(total)
        passed_external = True
        message = f"Expected result: Grade {grade} with total marks of {total}/100."

    return {
        "internal": internal_val,
        "paper_marks": paper_val,
        "total": total,
        "grade": grade,
        "passed_external": passed_external,
        "message": message
    }

def check_placement_eligibility(student_profile, criteria_queryset) -> list:
    """
    Evaluates a student against company criteria.
    Returns structured list of company eligibility results with specific reasons and advice.
    """
    results = []
    cgpa = float(student_profile.current_cgpa)
    backlogs = int(student_profile.backlogs_count)

    for item in criteria_queryset:
        min_cgpa = float(item.min_cgpa)
        max_bl = int(item.max_backlogs)

        reasons = []
        is_eligible = True

        if cgpa < min_cgpa:
            is_eligible = False
            deficit = round(min_cgpa - cgpa, 2)
            reasons.append(f"Current CGPA ({cgpa:.2f}) is below minimum requirement ({min_cgpa:.2f}) by {deficit:.2f} points.")

        if backlogs > max_bl:
            is_eligible = False
            reasons.append(f"Active backlogs ({backlogs}) exceed company allowance (max {max_bl}).")

        if is_eligible:
            status = 'eligible'
            recommendation = (f"Eligible for {item.company_name}! Focus on {item.required_skills} "
                              f"and mock interview preparation.")
        else:
            status = 'ineligible'
            recommendation = (f"To qualify for {item.company_name}, clear remaining backlogs "
                              f"and target higher SGPA in upcoming semesters to reach {min_cgpa:.2f} CGPA.")

        results.append({
            'id': item.id,
            'company_name': item.company_name,
            'role_title': item.role_title,
            'package_lpa': float(item.package_lpa),
            'min_cgpa': min_cgpa,
            'max_backlogs': max_bl,
            'required_skills': item.required_skills,
            'is_eligible': is_eligible,
            'status': status,
            'reasons': reasons,
            'recommendation': recommendation
        })

    return results


class PlacementReadinessResult(dict):
    """Result object that behaves both as an integer score and as a dict with breakdown & tip."""
    def __init__(self, score, cgpa_part, backlog_part, company_part, tip, eligible_count=0, total_companies=0):
        """Initializes dictionary entries and object attributes for composite score representation."""
        super().__init__(
            score=score,
            cgpa_part=cgpa_part,
            backlog_part=backlog_part,
            company_part=company_part,
            tip=tip,
            eligible_count=eligible_count,
            total_companies=total_companies
        )
        self.score = score
        self.cgpa_part = cgpa_part
        self.backlog_part = backlog_part
        self.company_part = company_part
        self.tip = tip
        self.eligible_count = eligible_count
        self.total_companies = total_companies

    def __int__(self):
        """Returns integer readiness score."""
        return self.score

    def __float__(self):
        """Returns float readiness score."""
        return float(self.score)

    def __eq__(self, other):
        """Compares score equality against numeric values or another result object."""
        if isinstance(other, (int, float)):
            return self.score == other
        return super().__eq__(other)


def placement_readiness(profile_or_cgpa, backlogs=None, eligible_count=None, total_companies=None):
    """
    Computes a placement readiness score 0-100:
      - 50% from CGPA (scaled out of 10)
      - 30% from having zero backlogs (reduced by 10 per active backlog)
      - 20% from number of corporate placement criteria met
    Returns a PlacementReadinessResult with score, component breakdown, and actionable tip.
    """
    if hasattr(profile_or_cgpa, 'current_cgpa'):
        cgpa = float(profile_or_cgpa.current_cgpa)
        backlogs = int(profile_or_cgpa.backlogs_count)

        if eligible_count is None or total_companies is None:
            from core.models import CompanyPlacementCriteria
            active_criteria = list(CompanyPlacementCriteria.objects.filter(is_active=True))
            total_companies = len(active_criteria)
            eligible_count = sum(
                1 for c in active_criteria
                if cgpa >= float(c.min_cgpa) and backlogs <= c.max_backlogs
            )
    else:
        cgpa = float(profile_or_cgpa or 0.0)
        backlogs = int(backlogs or 0)
        eligible_count = int(eligible_count or 0)
        total_companies = int(total_companies or 0)

    # 1. 50% from CGPA
    cgpa_clamped = min(max(cgpa, 0.0), 10.0)
    cgpa_part = (cgpa_clamped / 10.0) * 50.0

    # 2. 30% from Backlogs
    backlogs_clean = max(int(backlogs), 0)
    backlog_part = max(0.0, 30.0 - (10.0 * backlogs_clean))

    # 3. 20% from Eligible Companies
    if total_companies > 0:
        company_ratio = min(max(eligible_count / total_companies, 0.0), 1.0)
        company_part = company_ratio * 20.0
    else:
        company_part = 0.0

    score = int(round(cgpa_part + backlog_part + company_part))
    score = max(0, min(100, score))

    # Actionable tip
    if total_companies == 0:
        tip = "No companies have been added yet."
    elif backlogs_clean > 0:
        reclaim = min(backlogs_clean * 10, 30)
        tip = f"Clear {backlogs_clean} active arrear{'s' if backlogs_clean > 1 else ''} to reclaim up to {reclaim} backlog readiness points."
    elif cgpa < 7.5:
        tip = f"Target SGPA improvement to raise your CGPA from {cgpa:.2f} to 7.50+ for Tier-1 placements."
    elif eligible_count < total_companies:
        remaining = total_companies - eligible_count
        tip = f"Meet criteria for remaining {remaining} corporate partner{'s' if remaining > 1 else ''} to reach 100% eligibility."
    else:
        tip = "Outstanding standing! Profile meets 100% of corporate placement criteria."

    return PlacementReadinessResult(
        score=score,
        cgpa_part=round(cgpa_part, 1),
        backlog_part=round(backlog_part, 1),
        company_part=round(company_part, 1),
        tip=tip,
        eligible_count=eligible_count,
        total_companies=total_companies
    )


# ==============================================================================
# Shared Grade Recording & Recalculation Engine (Arrear Tracker & Single/Bulk Entry)
# ==============================================================================

def is_failing_grade(grade_str: str) -> bool:
    """Returns True if the grade string represents a failed or standing arrear."""
    clean = str(grade_str).strip().upper()
    return clean in FAILING_GRADES or grade_to_point(clean) == 0.0

def recalculate_student_metrics(student_profile):
    """
    Recalculates semester SGPA, cumulative CGPA, earned credits,
    total active backlogs across all courses, and placement eligibility.
    """
    from core.models import SemesterRecord, CourseResult

    # 1. Update SGPA for each semester record
    for sem in SemesterRecord.objects.filter(student=student_profile):
        courses = CourseResult.objects.filter(student=student_profile, semester_number=sem.semester_number)
        calc = calculate_sgpa([{'credits': c.credits, 'grade_point': c.grade_point, 'grade': c.grade} for c in courses])
        sem.sgpa = calc['sgpa']
        sem.credits_earned = int(calc['total_credits'])
        sem.save(update_fields=['sgpa', 'credits_earned'])

    # 2. Count active backlogs (courses currently marked with a failing grade)
    active_backlogs = CourseResult.objects.filter(
        student=student_profile,
        grade__in=['U', 'RA', 'SA', 'W', 'u', 'ra', 'sa', 'w']
    ).count()

    # 3. Calculate cumulative CGPA
    all_sems = SemesterRecord.objects.filter(student=student_profile)
    cgpa_res = calculate_cgpa([{'sgpa': s.sgpa, 'credits_earned': s.credits_earned} for s in all_sems])

    student_profile.current_cgpa = cgpa_res['cgpa']
    student_profile.credits_earned = int(cgpa_res['total_credits'])
    student_profile.backlogs_count = active_backlogs
    student_profile.is_placement_eligible = (float(student_profile.current_cgpa) >= 7.0 and active_backlogs == 0)
    student_profile.save(update_fields=['current_cgpa', 'credits_earned', 'backlogs_count', 'is_placement_eligible'])

def record_course_result(
    action_user,
    student_profile,
    semester_number: int,
    course_code: str,
    course_name: str,
    credits: int,
    grade: str,
    grade_point: float = None,
    recalculate: bool = True
):
    """
    Saves or updates a single CourseResult with arrear tracking.
    If an existing course was failing and is now passing:
      - previous_grade is set to the old grade
      - arrear_cleared is set to True
      - cleared_on is set to current time
      - AcademicAuditLog entry: 'Arrear cleared: <course_code> (<old> -> <new>)' is created.
    If a passing course is changed to failing, arrear status is reset.
    Returns (course_result, arrear_cleared_bool).
    """
    from django.utils import timezone
    from core.models import SemesterRecord, CourseResult, AcademicAuditLog

    clean_grade = str(grade).strip().upper()
    if grade_point is None:
        grade_point = grade_to_point(clean_grade)
    else:
        grade_point = float(grade_point)

    sem_num = int(semester_number)
    sem_record, _ = SemesterRecord.objects.get_or_create(
        student=student_profile,
        semester_number=sem_num,
        defaults={'sgpa': grade_point, 'credits_earned': int(credits)}
    )

    existing_cr = CourseResult.objects.filter(
        student=student_profile,
        semester_number=sem_num,
        course_code=course_code
    ).first()

    arrear_cleared = False
    old_grade = ""

    if existing_cr:
        old_grade = existing_cr.grade.strip().upper()
        cr = existing_cr
        cr.course_name = course_name or cr.course_name
        cr.credits = int(credits)
        cr.grade_point = grade_point

        if is_failing_grade(old_grade) and not is_failing_grade(clean_grade):
            cr.previous_grade = old_grade[:3]
            cr.arrear_cleared = True
            cr.cleared_on = timezone.now()
            arrear_cleared = True
        elif is_failing_grade(clean_grade):
            cr.arrear_cleared = False
            cr.cleared_on = None

        cr.grade = clean_grade
        cr.semester_record = sem_record
        cr.save()
    else:
        cr = CourseResult.objects.create(
            student=student_profile,
            semester_record=sem_record,
            semester_number=sem_num,
            course_code=course_code,
            course_name=course_name,
            credits=int(credits),
            grade=clean_grade,
            grade_point=grade_point,
            previous_grade="",
            arrear_cleared=False,
            cleared_on=None
        )

    # Audit logging
    actor = action_user if getattr(action_user, 'is_authenticated', False) else None
    if arrear_cleared:
        AcademicAuditLog.objects.create(
            action_by=actor,
            action_type="Arrear cleared",
            description=f"Arrear cleared: {course_code} ({old_grade} -> {clean_grade})"
        )
    else:
        AcademicAuditLog.objects.create(
            action_by=actor,
            action_type="SINGLE_RESULT_ENTRY",
            description=f"Course {course_code} recorded for {student_profile.roll_number}."
        )

    if recalculate:
        recalculate_student_metrics(student_profile)

    return cr, arrear_cleared


def process_student_grades_csv(student_profile, action_user, csv_text: str):
    """
    Parses and processes CSV results upload for the authenticated student.
    Expected columns: semester, course_code, course_title (or course_name), credits, grade.
    Optional column: roll_number (if provided, must match student).
    """
    import csv
    import io
    from django.db import transaction
    from core.models import AcademicAuditLog

    if not csv_text or not csv_text.strip():
        return {
            "saved": 0,
            "skipped": 0,
            "errors": [],
            "error": "CSV content is empty.",
            "status_code": 400
        }

    f = io.StringIO(csv_text.strip())
    reader = csv.reader(f)
    try:
        header = next(reader)
    except StopIteration:
        return {
            "saved": 0,
            "skipped": 0,
            "errors": [],
            "error": "CSV file contains no header row.",
            "status_code": 400
        }

    clean_header = ['course_title' if col.strip().lower() in ('course_title', 'course_name') else col.strip().lower() for col in header]
    required_cols = ['semester', 'course_code', 'course_title', 'credits', 'grade']
    missing_cols = [c for c in required_cols if c not in clean_header]
    if missing_cols:
        return {
            "saved": 0,
            "skipped": 0,
            "errors": [],
            "error": f"Missing required column(s): {', '.join(missing_cols)}",
            "status_code": 400
        }

    col_idx = {c: clean_header.index(c) for c in required_cols}
    has_roll = 'roll_number' in clean_header
    roll_idx = clean_header.index('roll_number') if has_roll else None
    rows = list(reader)

    non_empty_rows = [r for r in rows if any(cell.strip() for cell in r)]
    if len(non_empty_rows) > 1000:
        return {
            "saved": 0,
            "skipped": 0,
            "errors": [],
            "error": "File exceeds maximum limit of 1000 rows.",
            "status_code": 400
        }

    saved = 0
    skipped = 0
    errors = []

    for idx, row in enumerate(rows, start=2):
        if not any(cell.strip() for cell in row):
            continue

        if len(row) <= max(col_idx.values()):
            errors.append({"row": idx, "reason": "Row has fewer columns than required by header."})
            skipped += 1
            continue

        if has_roll:
            row_roll = row[roll_idx].strip()
            if row_roll and student_profile.roll_number and row_roll.lower() != student_profile.roll_number.lower():
                errors.append({"row": idx, "reason": f"Row roll number '{row_roll}' does not match your profile roll number."})
                skipped += 1
                continue

        sem_raw = row[col_idx['semester']].strip()
        code = row[col_idx['course_code']].strip().upper()
        title = row[col_idx['course_title']].strip()
        cred_raw = row[col_idx['credits']].strip()
        grade_raw = row[col_idx['grade']].strip().upper()

        try:
            sem_num = int(sem_raw)
            if not (1 <= sem_num <= 8):
                raise ValueError()
        except (ValueError, TypeError):
            errors.append({"row": idx, "reason": f"Semester must be an integer between 1 and 8 (got '{sem_raw}')."})
            skipped += 1
            continue

        if not code:
            errors.append({"row": idx, "reason": "Course code cannot be empty."})
            skipped += 1
            continue

        if not title:
            errors.append({"row": idx, "reason": "Course title cannot be empty."})
            skipped += 1
            continue

        try:
            credits_val = float(cred_raw)
            if credits_val <= 0 or credits_val > 10:
                raise ValueError()
            credits_num = int(credits_val) if credits_val.is_integer() else credits_val
        except (ValueError, TypeError):
            errors.append({"row": idx, "reason": f"Credits must be a number between 1 and 10 (got '{cred_raw}')."})
            skipped += 1
            continue

        if grade_raw not in VALID_GRADES:
            errors.append({"row": idx, "reason": f"Invalid grade '{grade_raw}'. Allowed: O, A+, A, B+, B, C, U, RA, SA, W."})
            skipped += 1
            continue

        try:
            with transaction.atomic():
                record_course_result(
                    action_user=action_user,
                    student_profile=student_profile,
                    semester_number=sem_num,
                    course_code=code,
                    course_name=title,
                    credits=credits_num,
                    grade=grade_raw,
                    recalculate=False
                )
            saved += 1
        except Exception as ex:
            errors.append({"row": idx, "reason": f"Database save error: {str(ex)}"})
            skipped += 1

    if saved > 0:
        recalculate_student_metrics(student_profile)
        actor = action_user if getattr(action_user, 'is_authenticated', False) else None
        AcademicAuditLog.objects.create(
            action_by=actor,
            action_type="STUDENT_CSV_IMPORT",
            description=f"Student grade import: {saved} course results imported."
        )

    return {
        "saved": saved,
        "skipped": skipped,
        "errors": errors,
        "status_code": 200
    }


def process_bulk_grades_csv(action_user, csv_text: str):
    """Backward compatibility wrapper delegating to student import."""
    profile = getattr(action_user, 'profile', None)
    if profile:
        return process_student_grades_csv(profile, action_user, csv_text)
    return {"saved": 0, "skipped": 0, "errors": [], "status_code": 400, "error": "No student profile found."}



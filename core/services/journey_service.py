"""
Student Academic Journey, Milestone Badges, and Early Warning Predictive Analytics.
Calculates semester timeline evolution, gamified achievement badges, and least-squares SGPA forecasting.
"""

from core.models import UserProfile, SemesterRecord, CourseResult, AcademicAuditLog
from core.services.academic_service import (
    FAILING_GRADES,
    placement_readiness,
)

# Institutional Early Warning Thresholds
RISK_HIGH_CGPA = 6.0
RISK_HIGH_BACKLOGS = 2
RISK_HIGH_PREDICTED_SGPA = 5.5
RISK_MEDIUM_SGPA_DROP = 1.0
RISK_MEDIUM_BACKLOGS = 1

def predict_next_sgpa(sgpas: list) -> float:
    """
    Computes simple least-squares trend line through given SGPAs (up to last 3),
    predicting the next semester's SGPA clamped between 0.00 and 10.00.
    Returns None if fewer than 2 data points are provided.
    Example: [8.0, 7.0, 6.0] -> predicts 5.00
    """
    if not sgpas or len(sgpas) < 2:
        return None

    # Use up to the last 3 data points
    pts = [float(v) for v in sgpas[-3:]]
    n = len(pts)
    xs = list(range(1, n + 1))
    mean_x = sum(xs) / n
    mean_y = sum(pts) / n

    denom = sum((x - mean_x) ** 2 for x in xs)
    if denom == 0:
        return round(mean_y, 2)

    slope = sum((xs[i] - mean_x) * (pts[i] - mean_y) for i in range(n)) / denom
    intercept = mean_y - (slope * mean_x)

    next_x = n + 1
    predicted = slope * next_x + intercept
    return round(max(0.0, min(10.0, predicted)), 2)

def compute_sgpa_slope(sgpas: list) -> float:
    """Returns the slope across the last up to 3 SGPAs."""
    if not sgpas or len(sgpas) < 2:
        return 0.0
    pts = [float(v) for v in sgpas[-3:]]
    n = len(pts)
    xs = list(range(1, n + 1))
    mean_x = sum(xs) / n
    mean_y = sum(pts) / n
    denom = sum((x - mean_x) ** 2 for x in xs)
    if denom == 0:
        return 0.0
    return sum((xs[i] - mean_x) * (pts[i] - mean_y) for i in range(n)) / denom

def get_journey(student_profile) -> list:
    """
    Builds chronological academic journey timeline for a student.
    Returns list of dicts with semester metrics, trend change, best/hardest courses,
    cleared arrears, and highlight sentences.
    """
    if not student_profile:
        return []

    sem_records = list(SemesterRecord.objects.filter(
        student=student_profile,
        is_published=True
    ).order_by('semester_number'))

    if not sem_records:
        return []

    courses_by_sem = {}
    for c in CourseResult.objects.filter(student=student_profile, is_published=True):
        courses_by_sem.setdefault(c.semester_number, []).append(c)

    journey = []
    prev_sgpa = None

    for sem in sem_records:
        sgpa_val = float(sem.sgpa)
        diff = 0.0
        if prev_sgpa is None:
            change = "flat"
        else:
            diff = round(sgpa_val - prev_sgpa, 2)
            if diff > 0.05:
                change = "up"
            elif diff < -0.05:
                change = "down"
            else:
                change = "flat"

        c_list = courses_by_sem.get(sem.semester_number, [])
        best_course = None
        hardest_course = None
        cleared_courses = []

        if c_list:
            # Sort for best: highest grade_point, then credits
            sorted_best = sorted(c_list, key=lambda c: (float(c.grade_point), float(c.credits)), reverse=True)
            best_course = {
                "code": sorted_best[0].course_code,
                "name": sorted_best[0].course_name,
                "grade": sorted_best[0].grade,
                "grade_point": float(sorted_best[0].grade_point)
            }

            # Sort for hardest: lowest grade_point, then credits
            sorted_hardest = sorted(c_list, key=lambda c: (float(c.grade_point), -float(c.credits)))
            hardest_course = {
                "code": sorted_hardest[0].course_code,
                "name": sorted_hardest[0].course_name,
                "grade": sorted_hardest[0].grade,
                "grade_point": float(sorted_hardest[0].grade_point)
            }

            for c in c_list:
                if c.arrear_cleared:
                    cleared_courses.append(c.course_name)

        # Highlight sentence
        if cleared_courses:
            highlight = f"Cleared arrears in {', '.join(cleared_courses)} while securing {sgpa_val:.2f} SGPA."
        elif change == "up":
            best_name = best_course['name'] if best_course else 'core subjects'
            highlight = f"SGPA surged by +{diff:.2f} to {sgpa_val:.2f} with strong performance in {best_name}."
        elif change == "down":
            hard_name = hardest_course['name'] if hardest_course else 'advanced topics'
            highlight = f"SGPA dipped to {sgpa_val:.2f}; {hard_name} presented academic challenges."
        else:
            best_name = best_course['name'] if best_course else 'major modules'
            highlight = f"Consistent performance with {sgpa_val:.2f} SGPA led by {best_name}."

        journey.append({
            "semester_number": sem.semester_number,
            "sgpa": sgpa_val,
            "credits_earned": sem.credits_earned,
            "change": change,
            "diff": diff,
            "best_course": best_course,
            "hardest_course": hardest_course,
            "cleared_arrears": cleared_courses,
            "highlight": highlight,
        })
        prev_sgpa = sgpa_val

    return journey

def get_badges(student_profile) -> dict:
    """
    Evaluates institutional career milestone badges for a student.
    Returns dictionary with earned, locked, and all badges with rules and descriptions.
    """
    if not student_profile:
        return {"earned_badges": [], "locked_badges": [], "all_badges": []}

    sem_records = list(SemesterRecord.objects.filter(
        student=student_profile,
        is_published=True
    ).order_by('semester_number'))
    sem_count = len(sem_records)

    cgpa = float(student_profile.current_cgpa) if student_profile.current_cgpa is not None else 0.0
    backlogs = int(student_profile.backlogs_count) if student_profile.backlogs_count is not None else 0

    courses_by_sem = {}
    for c in CourseResult.objects.filter(student=student_profile, is_published=True):
        courses_by_sem.setdefault(c.semester_number, []).append(c)

    # 1. Zero Arrears: backlogs == 0 and at least 1 semester
    b1_earned = (backlogs == 0 and sem_count >= 1)

    # 2. Comeback: cleared at least 1 arrear
    has_cleared = CourseResult.objects.filter(student=student_profile, arrear_cleared=True).exists()
    b2_earned = has_cleared

    # 3. Rising Star: SGPA up in 2 consecutive semesters
    b3_earned = False
    if sem_count >= 3:
        for i in range(2, sem_count):
            if (float(sem_records[i].sgpa) > float(sem_records[i-1].sgpa) and
                float(sem_records[i-1].sgpa) > float(sem_records[i-2].sgpa)):
                b3_earned = True
                break

    # 4. Steady: last 3 SGPAs within 0.5 of each other
    b4_earned = False
    if sem_count >= 3:
        last3 = [float(s.sgpa) for s in sem_records[-3:]]
        if max(last3) - min(last3) <= 0.5:
            b4_earned = True

    # 5. Distinction: CGPA >= 8.5
    b5_earned = (cgpa >= 8.5 and sem_count >= 1)

    # 6. Full Credit Semester: at least one semester with no failed course and >0 courses
    b6_earned = False
    for s_num, c_list in courses_by_sem.items():
        if c_list and not any(c.grade in FAILING_GRADES for c in c_list):
            b6_earned = True
            break

    # 7. Placement Ready: readiness >= 70
    readiness_res = placement_readiness(student_profile)
    b7_earned = (int(readiness_res) >= 70)

    definitions = [
        {
            "id": "zero_arrears",
            "name": "Zero Arrears",
            "rule": "Maintain zero active backlogs with at least 1 published semester.",
            "earned": b1_earned,
            "icon": "shield-check",
            "badge_class": "badge-emerald"
        },
        {
            "id": "comeback",
            "name": "Comeback",
            "rule": "Successfully clear at least one standing arrear.",
            "earned": b2_earned,
            "icon": "arrow-path",
            "badge_class": "badge-amber"
        },
        {
            "id": "rising_star",
            "name": "Rising Star",
            "rule": "Achieve SGPA improvement across two consecutive semesters.",
            "earned": b3_earned,
            "icon": "sparkles",
            "badge_class": "badge-primary"
        },
        {
            "id": "steady",
            "name": "Steady",
            "rule": "Maintain consistent performance with your last 3 SGPAs within 0.5 points.",
            "earned": b4_earned,
            "icon": "scale",
            "badge_class": "badge-blue"
        },
        {
            "id": "distinction",
            "name": "Distinction",
            "rule": "Attain a cumulative CGPA of 8.50 or higher.",
            "earned": b5_earned,
            "icon": "trophy",
            "badge_class": "badge-gold"
        },
        {
            "id": "full_credit",
            "name": "Full Credit Semester",
            "rule": "Complete all registered credits in a semester with zero failed subjects.",
            "earned": b6_earned,
            "icon": "academic-cap",
            "badge_class": "badge-emerald"
        },
        {
            "id": "placement_ready",
            "name": "Placement Ready",
            "rule": "Achieve an overall placement readiness score of 70% or higher.",
            "earned": b7_earned,
            "icon": "briefcase",
            "badge_class": "badge-purple"
        },
    ]

    earned = [b for b in definitions if b["earned"]]
    locked = [b for b in definitions if not b["earned"]]

    return {
        "earned_badges": earned,
        "locked_badges": locked,
        "all_badges": definitions
    }

def evaluate_student_risk(student_profile) -> dict:
    """
    Evaluates student academic trajectory for early warning intervention.
    Calculates predicted next SGPA, trend, risk level (high, medium, low), and plain-sentence reasons.
    """
    cgpa = float(student_profile.current_cgpa) if student_profile.current_cgpa is not None else 0.0
    backlogs = int(student_profile.backlogs_count) if student_profile.backlogs_count is not None else 0

    semesters = list(SemesterRecord.objects.filter(
        student=student_profile,
        is_published=True
    ).order_by('semester_number'))
    sgpas = [float(s.sgpa) for s in semesters]

    predicted_next_sgpa = predict_next_sgpa(sgpas)
    slope = compute_sgpa_slope(sgpas)

    if slope > 0.10:
        trend = "improving"
    elif slope < -0.10:
        trend = "declining"
    else:
        trend = "steady"

    # Compute drop in last semester
    last_drop = 0.0
    if len(sgpas) >= 2:
        last_drop = round(sgpas[-2] - sgpas[-1], 2)

    reasons = []
    # High risk checks
    is_high = False
    if cgpa < RISK_HIGH_CGPA:
        is_high = True
        reasons.append(f"CGPA {cgpa:.2f} is below {RISK_HIGH_CGPA:.1f}")
    if backlogs >= RISK_HIGH_BACKLOGS:
        is_high = True
        reasons.append(f"{backlogs} active arrears")
    if predicted_next_sgpa is not None and predicted_next_sgpa < RISK_HIGH_PREDICTED_SGPA:
        is_high = True
        reasons.append(f"Predicted next SGPA ({predicted_next_sgpa:.2f}) is below {RISK_HIGH_PREDICTED_SGPA:.1f}")

    # Medium risk checks
    is_medium = False
    if not is_high:
        if last_drop >= RISK_MEDIUM_SGPA_DROP:
            is_medium = True
            reasons.append(f"SGPA fell {last_drop:.2f} in the last semester")
        if backlogs == RISK_MEDIUM_BACKLOGS:
            is_medium = True
            reasons.append("1 active arrear")

    if is_high:
        risk_level = "high"
    elif is_medium:
        risk_level = "medium"
    else:
        risk_level = "low"
        if not reasons:
            reasons.append("Consistent academic standing")

    return {
        "predicted_next_sgpa": predicted_next_sgpa,
        "trend": trend,
        "risk_level": risk_level,
        "reasons": reasons
    }

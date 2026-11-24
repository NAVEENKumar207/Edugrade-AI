"""
Digital Twin Academic Simulation and Career Impact Engine for EduGrade AI.
Provides Monte Carlo future trajectory forecasting and 'Next Best Move' arrear impact ranking.
"""

import random
from core.models import UserProfile, CourseResult, CompanyPlacementCriteria
from core.services.academic_service import (
    GRADE_POINT_MAP,
    FAILING_GRADES,
    placement_readiness,
)

GRADE_STEPS = ['U', 'C', 'B', 'B+', 'A', 'A+', 'O']

def _get_student_profile(profile_data):
    """Normalizes profile_data into a UserProfile instance."""
    if isinstance(profile_data, UserProfile):
        return profile_data
    if hasattr(profile_data, 'profile'):
        return profile_data.profile
    if isinstance(profile_data, dict):
        pid = profile_data.get('id') or profile_data.get('student_id')
        if pid:
            return UserProfile.objects.filter(id=pid).first()
    if isinstance(profile_data, int):
        return UserProfile.objects.filter(id=profile_data).first()
    return None

def simulate_future(profile_data, target_cgpa: float, effort: str = "same", runs: int = 2000, seed: int = None) -> dict:
    """
    Simulates academic trajectory using Monte Carlo modeling based on student's past grade probabilities.
    effort: 'lower', 'same', or 'higher'.
    runs: number of iterations (default 2000).
    seed: optional integer seed for deterministic testing.
    """
    student = _get_student_profile(profile_data)
    if not student:
        return {"enough_data": False, "message": "Student profile not found."}

    # Fetch latest attempt per course for the student
    all_results = CourseResult.objects.filter(student=student).order_by('semester_number', 'id')
    latest_courses = {}
    for cr in all_results:
        code = cr.course_code.strip().upper()
        latest_courses[code] = cr

    if len(latest_courses) < 5:
        return {
            "enough_data": False,
            "message": "Add at least 5 course results to unlock the simulator."
        }

    # Learn pattern: probability of each grade, double weighting most recent semester
    max_sem = max(cr.semester_number for cr in latest_courses.values())
    counts = {g: 0.0 for g in GRADE_STEPS}

    for cr in latest_courses.values():
        w = 2.0 if cr.semester_number == max_sem else 1.0
        g = cr.grade.strip().upper()
        if g in FAILING_GRADES or g not in counts:
            g = 'U'
        counts[g] += w

    total_weight = sum(counts.values())
    if total_weight <= 0:
        return {"enough_data": False, "message": "Add at least 5 course results to unlock the simulator."}

    grades_list = list(counts.keys())
    weights_list = [counts[g] for g in grades_list]

    # Degree credits and remaining calculations
    deg_total = float(student.total_credits) if student.total_credits and student.total_credits > 0 else 160.0
    completed_cr = float(student.credits_earned) if student.credits_earned is not None else 0.0
    current_cgpa = float(student.current_cgpa) if student.current_cgpa is not None else 0.0
    current_backlogs = int(student.backlogs_count) if student.backlogs_count is not None else 0
    remaining_cr = max(0.0, deg_total - completed_cr)

    companies = list(CompanyPlacementCriteria.objects.all())

    # If no remaining credits, trajectory is already fixed
    if remaining_cr <= 0.0:
        prob = 100.0 if current_cgpa >= target_cgpa else 0.0
        zero_bl_prob = 100.0 if current_backlogs == 0 else 0.0
        company_probs = []
        for c in companies:
            c_eligible = 100.0 if (current_cgpa >= float(c.min_cgpa) and current_backlogs <= c.max_backlogs) else 0.0
            company_probs.append({
                "company_name": c.company_name,
                "role_title": c.role_title,
                "min_cgpa": float(c.min_cgpa),
                "max_backlogs": c.max_backlogs,
                "package_lpa": float(c.package_lpa),
                "probability": c_eligible
            })
        company_probs.sort(key=lambda x: x['probability'], reverse=True)
        return {
            "enough_data": True,
            "probability": prob,
            "expected_cgpa": round(current_cgpa, 2),
            "p10_cgpa": round(current_cgpa, 2),
            "p90_cgpa": round(current_cgpa, 2),
            "zero_backlogs_probability": zero_bl_prob,
            "companies": company_probs,
            "message": "Degree already completed! No remaining credits to simulate.",
            "disclaimer": "This simulation is an estimate based on your own past pattern, not a guarantee."
        }

    # Assume average of 4 credits per future course
    future_course_credits = 4.0
    num_future_courses = max(1, int(round(remaining_cr / future_course_credits)))

    rng = random.Random(seed)
    final_cgpas = []
    runs_backlogs = []
    runs_eligibility = {c.id: 0 for c in companies}
    target_achieved_count = 0
    zero_backlogs_count = 0

    base_points = current_cgpa * completed_cr

    for _ in range(runs):
        sampled_grades = rng.choices(grades_list, weights=weights_list, k=num_future_courses)
        run_new_backlogs = 0
        run_future_earned_cr = 0.0
        run_future_points = 0.0

        for raw_g in sampled_grades:
            # Effort shift: higher moves up 1 step (O stays O), lower moves down 1 step (U stays U)
            raw_idx = GRADE_STEPS.index(raw_g)
            if effort == "higher":
                shift_idx = min(len(GRADE_STEPS) - 1, raw_idx + 1)
            elif effort == "lower":
                shift_idx = max(0, raw_idx - 1)
            else:
                shift_idx = raw_idx

            final_g = GRADE_STEPS[shift_idx]
            if final_g == 'U':
                run_new_backlogs += 1
            else:
                gp = GRADE_POINT_MAP[final_g]
                run_future_earned_cr += future_course_credits
                run_future_points += (future_course_credits * gp)

        total_earned_at_end = completed_cr + run_future_earned_cr
        if total_earned_at_end > 0:
            final_cgpa = round((base_points + run_future_points) / total_earned_at_end, 2)
        else:
            final_cgpa = current_cgpa

        final_backlogs = current_backlogs + run_new_backlogs
        final_cgpas.append(final_cgpa)
        runs_backlogs.append(final_backlogs)

        if final_cgpa >= target_cgpa:
            target_achieved_count += 1
        if final_backlogs == 0:
            zero_backlogs_count += 1

        for c in companies:
            if final_cgpa >= float(c.min_cgpa) and final_backlogs <= c.max_backlogs:
                runs_eligibility[c.id] += 1

    final_cgpas.sort()
    p10_idx = int(0.10 * runs)
    p90_idx = min(len(final_cgpas) - 1, int(0.90 * runs))

    expected_cgpa = round(sum(final_cgpas) / len(final_cgpas), 2)
    p10_cgpa = round(final_cgpas[p10_idx], 2)
    p90_cgpa = round(final_cgpas[p90_idx], 2)
    prob_target = round((target_achieved_count / runs) * 100.0, 1)
    prob_zero_backlogs = round((zero_backlogs_count / runs) * 100.0, 1)

    company_results = []
    for c in companies:
        c_prob = round((runs_eligibility[c.id] / runs) * 100.0, 1)
        company_results.append({
            "company_name": c.company_name,
            "role_title": c.role_title,
            "min_cgpa": float(c.min_cgpa),
            "max_backlogs": c.max_backlogs,
            "package_lpa": float(c.package_lpa),
            "probability": c_prob
        })

    company_results.sort(key=lambda x: x['probability'], reverse=True)

    return {
        "enough_data": True,
        "probability": prob_target,
        "expected_cgpa": expected_cgpa,
        "p10_cgpa": p10_cgpa,
        "p90_cgpa": p90_cgpa,
        "zero_backlogs_probability": prob_zero_backlogs,
        "companies": company_results,
        "disclaimer": "This simulation is an estimate based on your own past pattern, not a guarantee."
    }

def rank_next_moves(student, assumed_grade: str = "B") -> list:
    """
    Ranks potential arrear clearing actions by corporate eligibility unlock and CGPA gain.
    Simulates clearing each active backlog WITHOUT saving changes to the database.
    """
    clean_grade = str(assumed_grade).strip().upper()
    if clean_grade not in ['C', 'B', 'A']:
        raise ValueError("Assumed grade must be one of: C, B, A.")

    student_profile = _get_student_profile(student)
    if not student_profile:
        return []

    cgpa_before = float(student_profile.current_cgpa) if student_profile.current_cgpa is not None else 0.0
    credits_before = float(student_profile.credits_earned) if student_profile.credits_earned is not None else 0.0
    backlogs_before = int(student_profile.backlogs_count) if student_profile.backlogs_count is not None else 0

    companies = list(CompanyPlacementCriteria.objects.all())
    eligible_before = [c for c in companies if cgpa_before >= float(c.min_cgpa) and backlogs_before <= c.max_backlogs]
    readiness_before = int(placement_readiness(student_profile, backlogs=backlogs_before, eligible_count=len(eligible_before), total_companies=len(companies)))

    # Fetch active arrears (failing grade and not yet marked cleared)
    active_arrears = list(CourseResult.objects.filter(
        student=student_profile,
        grade__in=FAILING_GRADES,
        arrear_cleared=False
    ).order_by('semester_number', 'course_code'))

    if not active_arrears:
        # Fallback to weakest passed course suggestion
        weakest = CourseResult.objects.filter(
            student=student_profile
        ).exclude(grade__in=FAILING_GRADES).order_by('grade_point', 'credits').first()

        if weakest:
            sentence = f"All arrears clear! Aim higher in {weakest.course_name} ({weakest.course_code}) or target A+ grades in upcoming semesters to boost your CGPA."
        else:
            sentence = "All arrears clear! Maintain consistent academic momentum to maximize placement eligibility."

        return [{
            "type": "no_arrears",
            "course_code": weakest.course_code if weakest else "N/A",
            "course_name": weakest.course_name if weakest else "Upcoming Courses",
            "credits": weakest.credits if weakest else 0,
            "cgpa_before": cgpa_before,
            "cgpa_after": cgpa_before,
            "cgpa_gain": 0.0,
            "new_companies": [],
            "readiness_before": readiness_before,
            "readiness_after": readiness_before,
            "readiness_gain": 0,
            "sentence": sentence,
        }]

    assumed_gp = GRADE_POINT_MAP[clean_grade]
    moves = []

    for course in active_arrears:
        cr = float(course.credits)
        credits_after = credits_before + cr
        if credits_after > 0:
            cgpa_after = round((credits_before * cgpa_before + cr * assumed_gp) / credits_after, 2)
        else:
            cgpa_after = cgpa_before

        backlogs_after = max(0, backlogs_before - 1)
        eligible_after = [c for c in companies if cgpa_after >= float(c.min_cgpa) and backlogs_after <= c.max_backlogs]
        new_eligible = [c.company_name for c in eligible_after if c not in eligible_before]

        readiness_after = int(placement_readiness(student_profile, backlogs=backlogs_after, eligible_count=len(eligible_after), total_companies=len(companies)))

        cgpa_gain = round(cgpa_after - cgpa_before, 2)
        readiness_gain = readiness_after - readiness_before

        if new_eligible:
            unlock_str = f" and unlocks {', '.join(new_eligible[:3])}."
        else:
            unlock_str = "."

        sentence = (
            f"Clearing {course.course_name} ({int(cr)} cr) with a {clean_grade}: "
            f"CGPA {cgpa_before:.2f} -> {cgpa_after:.2f}{unlock_str}"
        )

        moves.append({
            "type": "arrear",
            "course_code": course.course_code,
            "course_name": course.course_name,
            "credits": int(cr),
            "cgpa_before": cgpa_before,
            "cgpa_after": cgpa_after,
            "cgpa_gain": cgpa_gain,
            "new_companies": new_eligible,
            "readiness_before": readiness_before,
            "readiness_after": readiness_after,
            "readiness_gain": readiness_gain,
            "sentence": sentence,
        })

    # Rank by number of newly eligible companies (descending), then CGPA gain (descending)
    moves.sort(key=lambda m: (len(m["new_companies"]), m["cgpa_gain"]), reverse=True)
    return moves

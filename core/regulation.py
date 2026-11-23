"""
Default values - verify against your college's regulation document and edit here.
Institutional academic regulation constants for internal assessments, end-semester
examinations, passing minimums, and letter grade conversion thresholds.
"""

INTERNAL_MAX = 40            # internal marks out of 40
EXTERNAL_PAPER_MAX = 100     # end-semester paper is marked out of 100
EXTERNAL_WEIGHT = 0.6        # paper marks are scaled to 60% of the total
MIN_EXTERNAL_PERCENT = 45    # minimum percent in the end-semester paper to pass
MIN_TOTAL_TO_PASS = 50       # minimum total out of 100 to pass
GRADE_BOUNDARIES = {"O": 91, "A+": 81, "A": 71, "B+": 61, "B": 56, "C": 50}

def marks_to_grade(total: float) -> str:
    """
    Returns letter grade for a given total out of 100 according to lower bounds of GRADE_BOUNDARIES.
    Checks from the highest grade down and returns the first grade whose low bound is <= total;
    below MIN_TOTAL_TO_PASS the grade is 'U'.
    Totals below 0 or above 100 are validation errors (raises ValueError).
    """
    if total is None:
        raise ValueError("Total marks cannot be None.")
    try:
        val = float(total)
    except (TypeError, ValueError):
        raise ValueError(f"Total marks must be a valid number, got {total}.")

    if val < 0.0 or val > 100.0:
        raise ValueError(f"Total marks must be between 0 and 100, got {val}.")

    if val < MIN_TOTAL_TO_PASS:
        return "U"

    # Sort boundaries descending: O (91), A+ (81), A (71), B+ (61), B (56), C (50)
    for grade, min_score in sorted(GRADE_BOUNDARIES.items(), key=lambda item: item[1], reverse=True):
        if val >= min_score:
            return grade
    return "U"

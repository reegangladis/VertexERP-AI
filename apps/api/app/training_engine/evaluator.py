import uuid
from datetime import date
from typing import Any

SKILL_LEVEL_WEIGHTS = {
    "Beginner": 1,
    "Intermediate": 2,
    "Advanced": 3,
    "Expert": 4,
}


class TrainingEvaluator:
    """Evaluation engine for L&D assessment grading, certificate generation, and skill gap calculation."""

    @staticmethod
    def evaluate_assessment(score: float, passing_score: float) -> dict[str, Any]:
        passed = score >= passing_score
        return {
            "passed": passed,
            "score": score,
            "passing_score": passing_score,
            "status": "Passed" if passed else "Failed",
        }

    @staticmethod
    def generate_certificate_number(course_code: str) -> str:
        date_str = date.today().strftime("%Y%m%d")
        rand_hex = uuid.uuid4().hex[:6].upper()
        return f"CERT-{course_code.upper()}-{date_str}-{rand_hex}"

    @staticmethod
    def calculate_skill_gap(required_level: str, current_level: str | None) -> dict[str, Any]:
        req_weight = SKILL_LEVEL_WEIGHTS.get(required_level, 2)
        curr_weight = SKILL_LEVEL_WEIGHTS.get(current_level, 0) if current_level else 0

        gap = req_weight - curr_weight
        has_gap = gap > 0

        return {
            "required_level": required_level,
            "current_level": current_level or "None",
            "has_gap": has_gap,
            "gap_levels": max(0, gap),
            "status": "Gap Identified" if has_gap else "Compliant",
        }

"""
Helper functions for building assignment detail responses.

This keeps complex logic out of `backend/app.py` and makes the
assignment-detail API easier to read and maintain.
"""

from typing import Any, Dict, Optional, List

from bson import ObjectId


def _build_quiz_mcq_detail(assignment: Dict[str, Any]) -> Dict[str, Any]:
    """Build detail payload for MCQ quiz assignments."""
    questions: List[Dict[str, Any]] = []

    # Prefer detailed results if quiz has been completed
    results = assignment.get("results")
    if results:
        for r in results:
            questions.append(
                {
                    "question": r.get("question", ""),
                    "options": r.get("options", []),
                    "correct_index": r.get("correct_index", 0),
                    "user_answer": r.get("user_answer", None),
                    "is_correct": bool(r.get("is_correct", False)),
                    "explanation": r.get("explanation", ""),
                }
            )
    else:
        # Pending quiz: show questions without marking correctness
        for q in assignment.get("question_set", []):
            questions.append(
                {
                    "question": q.get("question", ""),
                    "options": q.get("options", []),
                    "correct_index": q.get("correct_index", 0),
                    "user_answer": None,
                    "is_correct": None,
                }
            )

    base: Dict[str, Any] = {
        "type": "quiz_mcq",
        "questions": questions,
    }
    return base


def _build_text_detail(assignment: Dict[str, Any]) -> Dict[str, Any]:
    """Build detail payload for text/descriptive assignments."""
    question_text = (
        assignment.get("question") or assignment.get("description") or ""
    )
    student_answer = assignment.get("student_answer", "")

    return {
        "type": "text",
        "question": question_text,
        "student_answer": student_answer,
    }


def get_assignment_detail(
    assignments_collection, assignment_id: str
) -> Optional[Dict[str, Any]]:
    """
    Fetch and build a complete assignment detail structure.

    Returns:
        A dictionary with all assignment detail fields, or None if not found.
    """
    assignment = assignments_collection.find_one({"_id": ObjectId(assignment_id)})
    if not assignment:
        return None

    base: Dict[str, Any] = {
        "id": str(assignment["_id"]),
        "title": assignment.get("title", ""),
        "course": assignment.get("course", ""),
        "status": assignment.get("status", "pending"),
        "points": assignment.get("points", 0),
        "score": assignment.get("score"),
        "rating": assignment.get("rating"),
        "difficulty_level": assignment.get("difficulty_level", 1),
        "feedback": assignment.get("feedback", ""),
        "assignment_type": assignment.get("assignment_type", "text"),
    }

    if assignment.get("assignment_type") == "quiz_mcq":
        base.update(_build_quiz_mcq_detail(assignment))
    else:
        base.update(_build_text_detail(assignment))

    return base



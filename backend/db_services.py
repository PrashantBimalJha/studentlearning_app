"""
Database helper functions for courses and assignments.

These helpers keep `app.py` smaller and more focused on
HTTP route handling.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from bson import ObjectId


# ----------------------------- COURSES -----------------------------

def get_courses(courses_collection, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Get all courses from database with optional filters."""
    query: Dict[str, Any] = {}
    if filters:
        if filters.get("category"):
            query["category"] = filters["category"]
        if filters.get("level"):
            query["level"] = filters["level"]
        if filters.get("instructor"):
            query["instructor"] = {"$regex": filters["instructor"], "$options": "i"}

    courses = list(courses_collection.find(query).sort("created_at", -1))
    for course in courses:
        course["_id"] = str(course["_id"])
        # Ensure all required fields exist with defaults
        course.setdefault("enrolled_students", 0)
        course.setdefault("rating", 0)
        course.setdefault("duration", "")
        course.setdefault("description", "")
    return courses


def add_course(courses_collection, course_data: Dict[str, Any]) -> Optional[str]:
    """Add a new course to database."""
    course_data["created_at"] = datetime.utcnow()
    result = courses_collection.insert_one(course_data)
    return str(result.inserted_id)


def update_course(courses_collection, course_id: str, course_data: Dict[str, Any]) -> bool:
    """Update an existing course."""
    result = courses_collection.update_one(
        {"_id": ObjectId(course_id)},
        {"$set": course_data},
    )
    return result.modified_count > 0


def delete_course(courses_collection, course_id: str) -> bool:
    """Delete a course."""
    result = courses_collection.delete_one({"_id": ObjectId(course_id)})
    return result.deleted_count > 0


# ----------------------------- ASSIGNMENTS -----------------------------

def get_assignments(assignments_collection, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Get all assignments from database with optional filters."""
    query: Dict[str, Any] = {}
    if filters:
        if filters.get("course"):
            query["course"] = filters["course"]
        if filters.get("status"):
            query["status"] = filters["status"]
        if filters.get("due_date"):
            query["due_date"] = {"$gte": filters["due_date"]}

    assignments = list(assignments_collection.find(query).sort("due_date", 1))
    for assignment in assignments:
        assignment["_id"] = str(assignment["_id"])
        # Ensure all required fields exist with defaults
        assignment.setdefault("points", 100)
        assignment.setdefault("description", "")
        assignment.setdefault("status", "pending")
        # Adaptive learning / grading fields
        assignment.setdefault("difficulty_level", 1)
        assignment.setdefault("score", None)
        assignment.setdefault("rating", None)
    return assignments


def add_assignment(assignments_collection, assignment_data: Dict[str, Any]) -> Optional[str]:
    """Add a new assignment to database."""
    assignment_data["created_at"] = datetime.utcnow()
    result = assignments_collection.insert_one(assignment_data)
    return str(result.inserted_id)


def update_assignment(assignments_collection, assignment_id: str, assignment_data: Dict[str, Any]) -> bool:
    """Update an existing assignment."""
    result = assignments_collection.update_one(
        {"_id": ObjectId(assignment_id)},
        {"$set": assignment_data},
    )
    return result.modified_count > 0


def delete_assignment(assignments_collection, assignment_id: str) -> bool:
    """Delete an assignment."""
    result = assignments_collection.delete_one({"_id": ObjectId(assignment_id)})
    return result.deleted_count > 0


def get_user_assignments(assignments_collection, user_email: str) -> List[Dict[str, Any]]:
    """Get assignments for a specific user."""
    assignments = list(assignments_collection.find({"student_email": user_email}).sort("due_date", 1))
    for assignment in assignments:
        assignment["_id"] = str(assignment["_id"])
        # Ensure all required fields exist with defaults
        assignment.setdefault("points", 100)
        assignment.setdefault("description", "")
        assignment.setdefault("status", "pending")
        assignment.setdefault("difficulty_level", 1)
        assignment.setdefault("score", None)
        assignment.setdefault("rating", None)
    return assignments



# =============================================================================
# TASK: Mini Student Record System
# Topics covered: type hints, generic types, union types, classes as type hints,
#                 Pydantic BaseModel, coercion, validation errors, Annotated
#
# Steps:
#   1. letter_grades(score) -> str         : type hints on a utility function
#   2. Subject class                       : class with type hints, describe() method
#   3. Student(BaseModel)                  : Pydantic model with coercion + validation
#   4. evaluate(student, subject) -> str   : function using class as type hint
#   5. Test coercion (id="7" -> 7)         : Pydantic coerces str to int
#   6. Test validation error (score="abc") : Pydantic raises error for bad type
# =============================================================================

from pydantic import BaseModel


class Student(BaseModel):
    id: int
    name: str
    age: int | None = None
    subjects: list[str] = []
    score: float  # Annotated[float, "testing"] — the string metadata does nothing, plain float is fine here


class Subject:
    # type hints belong on parameters, not on self.x — gives editor autocomplete when calling Subject(...)
    def __init__(self, name: str, max_marks: int):
        self.name = name
        self.max_marks = max_marks

    def describe(self) -> str:
        return f"{self.name.capitalize()} ({self.max_marks} marks)"  # f-string avoids str+int crash


def letter_grades(score: float) -> str:
    if score > 85:
        return "A"
    elif score > 70:
        return "B"
    elif score > 55:
        return "C"
    elif score > 40:
        return "D"
    elif score > 25:
        return "E"
    else:
        return "F"


# Annotated[Subject, "..."] works without error but the string does nothing — Python/FastAPI ignores plain strings
def evaluate(student: Student, subject: Subject) -> str:
    return f"{student.name.capitalize()} scored {letter_grades(student.score)} in {subject.describe()}"


print("-+-" * 10)

# max_marks passed as int (not "100") — plain class won't coerce like Pydantic
subject_1 = Subject("maths", 100)

# Pydantic coerces id="7" -> 7 and score="50" -> 50.0
student_A = Student(id="7", name="A", score="50")
print(f"student_A.id type: {type(student_A.id)} value: {student_A.id}")  # confirm coercion
print(evaluate(student_A, subject_1))
print("-+-" * 10)

# Pydantic raises ValidationError for score="not-a-number" — wrap in try/except to see the error and continue
try:
    student_B = Student(id=7, name="B", score="not-a-number")
    print(evaluate(student_B, subject_1))
except Exception as e:
    print(f"Validation error caught:\n{e}")
print("-+-" * 10)


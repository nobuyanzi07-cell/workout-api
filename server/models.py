from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import validates

db = SQLAlchemy()

CATEGORIES = ["strength", "cardio", "flexibility", "balance", "other"]


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    workout_exercises = db.relationship(
        "WorkoutExercise", back_populates="exercise", cascade="all, delete-orphan"
    )
    workouts = db.relationship(
        "Workout", secondary="workout_exercises", viewonly=True, back_populates="exercises"
    )

    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="ck_exercise_name_not_blank"),
        CheckConstraint(
            "category IN ('strength','cardio','flexibility','balance','other')",
            name="ck_exercise_category",
        ),
    )

    @validates("name")
    def validate_name(self, key, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Exercise name cannot be blank.")
        if len(value.strip()) > 100:
            raise ValueError("Exercise name must be 100 characters or fewer.")
        return value.strip()

    @validates("category")
    def validate_category(self, key, value):
        if value not in CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(CATEGORIES)}.")
        return value

    def __repr__(self):
        return f"<Exercise {self.id} {self.name}>"


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    workout_exercises = db.relationship(
        "WorkoutExercise", back_populates="workout", cascade="all, delete-orphan"
    )
    exercises = db.relationship(
        "Exercise", secondary="workout_exercises", viewonly=True, back_populates="workouts"
    )

    __table_args__ = (
        CheckConstraint("duration_minutes > 0", name="ck_workout_duration_positive"),
    )

    @validates("duration_minutes")
    def validate_duration(self, key, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Duration must be a positive integer (minutes).")
        return value

    @validates("notes")
    def validate_notes(self, key, value):
        if value is not None and len(value) > 500:
            raise ValueError("Notes must be 500 characters or fewer.")
        return value

    def __repr__(self):
        return f"<Workout {self.id} {self.date}>"


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    __table_args__ = (
        UniqueConstraint("workout_id", "exercise_id", name="uq_workout_exercise"),
        CheckConstraint("sets IS NULL OR sets > 0", name="ck_we_sets_positive"),
        CheckConstraint("reps IS NULL OR reps > 0", name="ck_we_reps_positive"),
        CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds > 0",
            name="ck_we_duration_positive",
        ),
        CheckConstraint(
            "(sets IS NOT NULL AND reps IS NOT NULL) OR duration_seconds IS NOT NULL",
            name="ck_we_has_measure",
        ),
    )

    @validates("sets", "reps", "duration_seconds")
    def validate_positive(self, key, value):
        if value is not None and (not isinstance(value, int) or value <= 0):
            raise ValueError(f"{key} must be a positive integer.")
        return value

    def __repr__(self):
        return f"<WorkoutExercise w={self.workout_id} e={self.exercise_id}>"
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db, Workout, Exercise, WorkoutExercise
from schemas import (
    exercise_schema,
    exercises_schema,
    workout_schema,
    workouts_schema,
    workout_exercise_schema,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)


def error(message, status):
    return jsonify({"error": message}), status


def save(obj):
    """Add and commit obj; return an error response tuple on failure, else None."""
    try:
        db.session.add(obj)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("Database constraint violated (duplicate or invalid data).", 409)
    return None


def build(model, **data):
    """Construct a model, converting model-level validation errors to ValueError."""
    return model(**data)


@app.errorhandler(ValidationError)
def handle_schema_error(e):
    return jsonify({"errors": e.messages}), 400


@app.errorhandler(ValueError)
def handle_model_error(e):
    db.session.rollback()
    return error(str(e), 422)


@app.get("/")
def index():
    return jsonify({"message": "Workout API"}), 200


# ---------- Workouts ----------
@app.get("/workouts")
def get_workouts():
    return jsonify(workouts_schema.dump(Workout.query.all())), 200


@app.get("/workouts/<int:id>")
def get_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return error("Workout not found.", 404)
    return jsonify(workout_schema.dump(workout)), 200


@app.post("/workouts")
def create_workout():
    data = workout_schema.load(request.get_json() or {})
    workout = build(Workout, **data)
    if (err := save(workout)):
        return err
    return jsonify(workout_schema.dump(workout)), 201


@app.delete("/workouts/<int:id>")
def delete_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return error("Workout not found.", 404)
    db.session.delete(workout)
    db.session.commit()
    return "", 204


# ---------- Exercises ----------
@app.get("/exercises")
def get_exercises():
    return jsonify(exercises_schema.dump(Exercise.query.all())), 200


@app.get("/exercises/<int:id>")
def get_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return error("Exercise not found.", 404)
    return jsonify(exercise_schema.dump(exercise)), 200


@app.post("/exercises")
def create_exercise():
    data = exercise_schema.load(request.get_json() or {})
    exercise = build(Exercise, **data)
    if (err := save(exercise)):
        return err
    return jsonify(exercise_schema.dump(exercise)), 201


@app.delete("/exercises/<int:id>")
def delete_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return error("Exercise not found.", 404)
    db.session.delete(exercise)
    db.session.commit()
    return "", 204


# ---------- Add exercise to workout ----------
@app.post("/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises")
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    exercise = db.session.get(Exercise, exercise_id)
    if not workout:
        return error("Workout not found.", 404)
    if not exercise:
        return error("Exercise not found.", 404)

    data = workout_exercise_schema.load(request.get_json() or {})
    link = build(WorkoutExercise, workout_id=workout_id, exercise_id=exercise_id, **data)
    if (err := save(link)):
        return err
    return jsonify(workout_exercise_schema.dump(link)), 201


if __name__ == "__main__":
    app.run(port=5555, debug=True)
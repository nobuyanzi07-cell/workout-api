# Workout Tracker API

A Flask + SQLAlchemy + Marshmallow backend for a workout tracking app used by personal trainers. Trainers can create workouts, create reusable exercises, and add exercises to workouts with sets/reps or a duration.

## Installation

```bash
git clone <your-repo-url>
cd workout-api
pipenv install
pipenv shell
cd server
export FLASK_APP=app.py
flask db init
flask db migrate -m "initial schema"
flask db upgrade
python seed.py
```

## Run

```bash
flask run -p 5555
```

## Data Model

- **Workout**: date, duration_minutes, notes
- **Exercise**: name (unique), category, equipment_needed
- **WorkoutExercise** (join): workout_id, exercise_id, sets, reps, duration_seconds

A workout has many exercises through WorkoutExercise, and an exercise can belong to many workouts.

## Validations

- **Table constraints**: unique exercise name, valid category, positive duration/sets/reps, unique (workout, exercise) pair, sets+reps or duration required
- **Model validations**: non-blank exercise name, valid category, positive duration, notes length, positive sets/reps/duration
- **Schema validations**: length and range checks, `OneOf` category, required fields, cross-field check requiring sets+reps or duration

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/workouts` | List all workouts with their exercises |
| GET | `/workouts/<id>` | Show one workout with its exercises |
| POST | `/workouts` | Create a workout (`date`, `duration_minutes`, optional `notes`) |
| DELETE | `/workouts/<id>` | Delete a workout and its exercise links |
| GET | `/exercises` | List all exercises |
| GET | `/exercises/<id>` | Show one exercise |
| POST | `/exercises` | Create an exercise (`name`, `category`, optional `equipment_needed`) |
| DELETE | `/exercises/<id>` | Delete an exercise and its workout links |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout (`sets` + `reps`, or `duration_seconds`) |

## Example

```bash
curl -X POST localhost:5555/workouts/1/exercises/2/workout_exercises \
  -H "Content-Type: application/json" \
  -d '{"sets": 3, "reps": 10}'
```

## Error codes

400 schema validation, 404 not found, 409 constraint violation (e.g. duplicate), 422 model validation.
from datetime import date

from app import app
from models import db, Workout, Exercise, WorkoutExercise

with app.app_context():
    print("Clearing data...")
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()

    print("Seeding exercises...")
    squat = Exercise(name="Squat", category="strength", equipment_needed=True)
    pushup = Exercise(name="Push-up", category="strength", equipment_needed=False)
    run = Exercise(name="Treadmill Run", category="cardio", equipment_needed=True)
    plank = Exercise(name="Plank", category="balance", equipment_needed=False)
    stretch = Exercise(name="Hamstring Stretch", category="flexibility", equipment_needed=False)
    db.session.add_all([squat, pushup, run, plank, stretch])

    print("Seeding workouts...")
    w1 = Workout(date=date(2025, 1, 6), duration_minutes=45, notes="Lower body day")
    w2 = Workout(date=date(2025, 1, 8), duration_minutes=30, notes="Cardio and core")
    w3 = Workout(date=date(2025, 1, 10), duration_minutes=20)
    db.session.add_all([w1, w2, w3])
    db.session.commit()

    print("Linking exercises to workouts...")
    db.session.add_all([
        WorkoutExercise(workout_id=w1.id, exercise_id=squat.id, sets=4, reps=8),
        WorkoutExercise(workout_id=w1.id, exercise_id=stretch.id, duration_seconds=120),
        WorkoutExercise(workout_id=w2.id, exercise_id=run.id, duration_seconds=1200),
        WorkoutExercise(workout_id=w2.id, exercise_id=plank.id, duration_seconds=90),
        WorkoutExercise(workout_id=w3.id, exercise_id=pushup.id, sets=3, reps=15),
        WorkoutExercise(workout_id=w3.id, exercise_id=squat.id, sets=3, reps=12),
    ])
    db.session.commit()
    print("Done.")
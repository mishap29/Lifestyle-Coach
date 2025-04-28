# src/exercise_planner.py
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

class ExercisePlanner:
    def __init__(self, user_id: str = "default"):
        """
        Initialize the exercise planner with user-specific data.
        Args:
            user_id: Unique identifier for user data isolation
        """
        self.data_path = Path(f"data/processed/{user_id}_exercise.json")
        self.data = self._load_data()

    def _load_data(self) -> Dict:
        """Load exercise data from a JSON file."""
        try:
            with open(self.data_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"exercise_logs": []}

    def _save_data(self):
        """Save exercise data back to the JSON file."""
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_path, 'w') as f:
            json.dump(self.data, f, indent=2)

    def log_exercise(self, activity_type: str, duration_hours: float, notes: str = "") -> None:
        """
        Record a new exercise entry.
        Args:
            activity_type: Type of exercise (e.g., Cardio, Walking, Running, Fitness Class, Other)
            duration_hours: Time spent exercising (in hours, eg 1.5)
            notes: Optional extra notes
        """
        if activity_type.lower() not in ["cardio", "walking", "running", "fitness class", "other"]:
            raise ValueError("Invalid activity type. Choose from Cardio, Walking, Running, Fitness Class, Other.")

        new_entry = {
            "date": datetime.now().isoformat(),
            "activity_type": activity_type.title(),
            "duration_hours": round(duration_hours, 2),
            "notes": notes
        }
        self.data["exercise_logs"].append(new_entry)
        self._save_data()

    def get_weekly_summary(self) -> Dict[str, any]:
        """
        Summarize the exercise activities for the past week.
        Returns:
            Dictionary including total time spent, number of sessions, and activity breakdown.
        """
        df = pd.DataFrame(self.data["exercise_logs"])
        if df.empty:
            return {}

        df['date'] = pd.to_datetime(df['date'])
        last_week = df[df['date'] > (datetime.now() - timedelta(days=7))]

        if last_week.empty:
            return {}

        total_hours = round(last_week['duration_hours'].sum(), 2)
        sessions = len(last_week)
        activity_counts = last_week['activity_type'].value_counts().to_dict()

        return {
            "total_hours": total_hours,
            "sessions": sessions,
            "activity_breakdown": activity_counts
        }

    def get_exercise_intervals(self) -> Dict[str, int]:
        """
        Categorize exercises into intervals based on time spent.
        Returns:
            Dictionary of interval counts.
        """
        df = pd.DataFrame(self.data["exercise_logs"])
        if df.empty:
            return {}

        intervals = {
            "0-2 hours": 0,
            "2-4 hours": 0,
            "4-6 hours": 0,
            "6+ hours": 0
        }

        for duration in df['duration_hours']:
            if duration <= 2:
                intervals["0-2 hours"] += 1
            elif duration <= 4:
                intervals["2-4 hours"] += 1
            elif duration <= 6:
                intervals["4-6 hours"] += 1
            else:
                intervals["6+ hours"] += 1

        return intervals

# Example usage
if __name__ == "__main__":
    planner = ExercisePlanner("test_user")

    # Test logging
    planner.log_exercise("Running", 1.5, "Morning run")
    planner.log_exercise("Fitness Class", 2.5, "Yoga class")

    # Test summaries
    print("Weekly Summary:", planner.get_weekly_summary())
    print("Exercise Intervals:", planner.get_exercise_intervals())

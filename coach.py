# src/coach.py
from data.sleep_database import get_sleep_issue_info  # <-- New import
import json
from datetime import datetime, timedelta
from typing import Dict
from pathlib import Path
import pandas as pd
from openai import OpenAI
from config import Config

class SleepCoach:
    def __init__(self, user_id: str = "default"):
        """
        Initialize with user-specific data storage and OpenAI client.
        Args:
            user_id: Unique identifier for user data isolation
        """
        self.data_path = Path(f"data/processed/{user_id}_sleep.json")
        self.data = self._load_data()
        self.client = OpenAI(api_key=Config.OPENAI_KEY)

    def _load_data(self) -> Dict:
        """Load user's sleep data from JSON file."""
        try:
            with open(self.data_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"sleep_logs": [], "goals": {}}

    def _save_data(self):
        """Persist data to JSON file."""
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_path, 'w') as f:
            json.dump(self.data, f, indent=2)

    def log_sleep(self, hours: float, quality: int, notes: str = "") -> None:
        """Record a new sleep entry."""
        new_entry = {
            "date": datetime.now().isoformat(),
            "hours": hours,
            "quality": quality,
            "notes": notes
        }
        self.data["sleep_logs"].append(new_entry)
        self._save_data()

    def get_weekly_report(self) -> Dict:
        """Generate weekly sleep statistics."""
        df = pd.DataFrame(self.data["sleep_logs"])
        if df.empty:
            return {}

        df['date'] = pd.to_datetime(df['date'])
        last_week = df[df['date'] > (datetime.now() - timedelta(days=7))]

        if last_week.empty:
            return {}

        return {
            "avg_hours": round(last_week['hours'].mean(), 1),
            "avg_quality": int(last_week['quality'].mean()),
            "consistency_score": self._calculate_consistency(last_week),
        }

    def _calculate_consistency(self, df: pd.DataFrame) -> float:
        """Calculate sleep schedule consistency (0-100 scale)."""
        if len(df) < 2:
            return 0
        hour_diffs = abs(df['hours'].diff().mean())
        return max(0, 100 - (hour_diffs * 10))

    def set_goal(self, goal_type: str, target: float) -> None:
        """Set a sleep-related goal."""
        self.data["goals"][goal_type] = target
        self._save_data()

    def check_goals(self) -> Dict:
        """Compare recent performance against goals."""
        report = self.get_weekly_report()
        if not report or not self.data["goals"]:
            return {}

        results = {}
        for goal_type in ['hours', 'quality']:
            if goal_type in self.data["goals"]:
                target = self.data["goals"][goal_type]
                actual = report.get(f"avg_{goal_type}", 0)
                difference = actual - target
                results[goal_type] = {
                    "status": "met" if difference >= 0 else "unmet",
                    "difference": round(difference, 1)
                }
        return results

    def get_ai_coaching(self, prompt: str, sleep_issue: str = "poor_sleep_quality") -> str:
        """
        Get personalized coaching from OpenAI based on the last few nights of sleep.
        Args:
            prompt: User's specific question/context.
            sleep_issue: Sleep issue key for pulling expert advice.
        Returns:
            AI-generated coaching response.
        """
        context = "\n".join(
            f"{log['date'][:10]}: {log['hours']}h, {log['quality']}/100 quality"
            for log in self.data["sleep_logs"][-3:]  # Last 3 entries
        )

        # Pull structured expert advice from sleep_database
        issue_info = get_sleep_issue_info(sleep_issue)

        if not issue_info:
            structured_advice = "No specific structured advice available."
        else:
            structured_advice = (
                f"Problem: {issue_info['description']}\n"
                "Recommended actions:\n"
                + "\n".join(f"- {tip}" for tip in issue_info["recommendations"])
            )

        # Build the full prompt
        full_prompt = (
            f"You are a professional sleep coach.\n"
            f"USER CONTEXT:\n{context}\n\n"
            f"KNOWN SLEEP ISSUE:\n{structured_advice}\n\n"
            f"USER QUESTION:\n{prompt}\n\n"
            "Respond with specific, actionable, compassionate advice. Cite the structured advice where helpful."
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in sleep science and coaching."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.5,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ Coaching unavailable: {str(e)}"

# Example usage
if __name__ == "__main__":
    coach = SleepCoach("test_user")

    coach.log_sleep(7.5, 85, "Good day")
    coach.log_sleep(6, 70, "Worked late")

    print("Weekly Report:", coach.get_weekly_report())

    coach.set_goal("hours", 8)
    coach.set_goal("quality", 80)
    print("Goal Status:", coach.check_goals())

    print("\nAI Advice:", coach.get_ai_coaching("Why do I feel tired even though I sleep 7 hours?"))


# Ensure required libraries are installed: pandas, matplotlib, seaborn, json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from typing import Optional
import plotly.express as px

class Visualizer:
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.sleep_data = self._load_data(f"data/{user_id}_sleep.json", "sleep_logs")
        self.exercise_data = self._load_data(f"data/{user_id}_exercise.json", "exercise_logs")

    def _load_data(self, path: str, key: str) -> pd.DataFrame:
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data.get(key, []))
            if not df.empty and 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            return df
        except (FileNotFoundError, json.JSONDecodeError):
            return pd.DataFrame()

    def plot_sleep_hours_trend(self):
        """Plot user's sleep hours over time."""
        if self.sleep_data.empty:
            print("No sleep data available.")
            return

        plt.figure(figsize=(10, 5))
        sns.lineplot(data=self.sleep_data, x="date", y="hours", marker="o")
        plt.title("Sleep Duration Over Time")
        plt.ylabel("Hours Slept")
        plt.xlabel("Date")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def plot_sleep_quality_trend(self):
        """Plot sleep quality trend over time."""
        if self.sleep_data.empty:
            print("No sleep data available.")
            return

        plt.figure(figsize=(10, 5))
        sns.lineplot(data=self.sleep_data, x="date", y="quality", marker="o", color="green")
        plt.title("Sleep Quality Over Time")
        plt.ylabel("Quality (0-100)")
        plt.xlabel("Date")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def plot_exercise_distribution(self):
        """Show distribution of exercise types."""
        if self.exercise_data.empty:
            print("No exercise data available.")
            return

        plt.figure(figsize=(8, 5))
        sns.countplot(data=self.exercise_data, x="activity", order=self.exercise_data['activity'].value_counts().index, palette="pastel")
        plt.title("Exercise Types Frequency")
        plt.ylabel("Sessions")
        plt.xlabel("Activity Type")
        plt.xticks(rotation=30)
        plt.tight_layout()
        plt.show()

    def plot_exercise_time_vs_sleep_quality(self):
        """Analyze relationship between time spent exercising and sleep quality."""
        if self.sleep_data.empty or self.exercise_data.empty:
            print("Insufficient data for combined analysis.")
            return

        combined = pd.merge_asof(
            self.sleep_data.sort_values('date'),
            self.exercise_data.sort_values('date'),
            on='date',
            direction='backward',
            tolerance=pd.Timedelta('1D')  # assume exercise affects next sleep
        )

        if combined.empty:
            print("No matched data to analyze.")
            return

        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=combined, x="duration_hours", y="quality", hue="activity", palette="muted")
        plt.title("Exercise Duration vs Sleep Quality")
        plt.xlabel("Exercise Duration (hours)")
        plt.ylabel("Sleep Quality (0-100)")
        plt.tight_layout()
        plt.show()

    def plot_goal_tracking(self, goals: Optional[dict] = None):
        """Visualize how user is performing against goals."""
        if self.sleep_data.empty:
            print("No sleep data available.")
            return

        if not goals:
            print("No goals provided for visualization.")
            return

        avg_sleep = self.sleep_data['hours'].mean()
        avg_quality = self.sleep_data['quality'].mean()

        metrics = ["Sleep Hours", "Sleep Quality"]
        current = [avg_sleep, avg_quality]
        targets = [goals.get('hours', 8), goals.get('quality', 80)]

        df = pd.DataFrame({"Metric": metrics, "Current": current, "Target": targets})

        df_melt = df.melt(id_vars="Metric", value_vars=["Current", "Target"], var_name="Type", value_name="Value")

        plt.figure(figsize=(8, 5))
        sns.barplot(data=df_melt, x="Metric", y="Value", hue="Type", palette="deep")
        plt.title("Goal Tracking Overview")
        plt.ylabel("Value")
        plt.tight_layout()
        plt.show()

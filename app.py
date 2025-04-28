# app.py
from exercise_planner import ExercisePlanner
from visualizations import Visualizer
from config import Config
import sys
from pathlib import Path

# Add project root so we can import from data/
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import json
import pandas as pd
import plotly.express as px
from openai import OpenAI
from datetime import datetime
# ======================
# SETUP & CONFIGURATION
# ======================
st.set_page_config(page_title="Lifestyle Coach", layout="wide")

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.api_key_valid = False

# ======================
# DATA MANAGEMENT
# ======================
class SleepDataManager:
    def __init__(self, user_id="default"):
        self.file_path = Path(f"data/{user_id}_sleep.json")
        self.data = self._load_data()

    def _load_data(self):
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"sleep_logs": []}

    def add_entry(self, hours: float, quality: int, notes: str = ""):
        new_entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "hours": hours,
            "quality": quality,
            "notes": notes
        }
        self.data["sleep_logs"].append(new_entry)
        self._save_data()

    def _save_data(self):
        self.file_path.parent.mkdir(exist_ok=True)
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f, indent=2)

    def get_last_entries(self, n=7):
        return self.data["sleep_logs"][-n:]

    def get_dataframe(self):
        return pd.DataFrame(self.data["sleep_logs"])

# ======================
# AI CHATBOT
# ======================
def initialize_chatbot(api_key: str):
    try:
        client = OpenAI(api_key=api_key)
        client.models.list()  # Test the API key
        st.session_state.api_key_valid = True
        return client
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        st.session_state.api_key_valid = False
        return None

def generate_coach_response(client, question: str, sleep_data: list):
    context = "\n".join(
        f"{log['date']}: {log['hours']} hours, Quality {log['quality']}/100"
        for log in sleep_data
    )
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You're a compassionate lifestyle coach. Provide specific advice based on the user's sleep data."},
            {"role": "user", "content": f"My recent sleep:\n{context}\n\nQuestion: {question}"}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

# ======================
# VISUALIZATIONS
# ======================
def plot_sleep_data(df):
    fig = px.line(df, 
                 x="date", 
                 y=["hours", "quality"],
                 title="Your Sleep Trends (Last 7 Days)",
                 labels={"value": "Metric", "variable": "Type"},
                 hover_data=["notes"],
                 markers=True)
    
    fig.update_layout(
        hovermode="x unified",
        yaxis_range=[0, 100],
        height=400
    )
    fig.update_yaxes(title_text="Hours/Quality (%)")
    return fig

# ======================
# STREAMLIT UI
# ======================
def main():
    # Sidebar - API Key and Authentication
    with st.sidebar:
        st.header("🔑 API Configuration")
        api_key = st.text_input("Enter OpenAI API Key", type="password")
        
        if st.button("Connect to AI"):
            st.session_state.client = initialize_chatbot(api_key)
        
        if st.session_state.get("api_key_valid", False):
            st.success("✅ API Key Valid")
        else:
            st.warning("Please enter a valid API key")

    # Main App Interface
    st.title("🌙 Sleep Lifestyle Coach")
    
    # Initialize data manager
    manager = SleepDataManager()
    
    # Tab System
    tab1, tab2, tab3, tab4 = st.tabs(["Sleep Logger", "Trends Dashboard", "AI Coach", "Exercise Planner"])

    with tab1:
        st.header("Log Your Sleep")
        col1, col2 = st.columns(2)
        
        with col1:
            hours = st.number_input("Hours Slept", 0.0, 24.0, 7.5, step=0.25)
            notes = st.text_area("Notes (optional)")
        
        with col2:
            quality = st.slider("Sleep Quality (0-100)", 0, 100, 75)
        
        if st.button("Save Sleep Entry"):
            manager.add_entry(hours, quality, notes)
            st.success("Entry saved successfully!")
            st.rerun()

    with tab2:
        st.header("Your Sleep Patterns")
        df = manager.get_dataframe()
        
        if not df.empty:
            st.plotly_chart(plot_sleep_data(df), use_container_width=True)
            
            # Statistics
            avg_hours = df["hours"].mean()
            st.metric("Average Sleep", f"{avg_hours:.1f} hours")
        else:
            st.info("No sleep data yet. Log some sleep in the first tab!")
    with tab3:
        st.header("Ask Your Lifestyle Coach")

        if not st.session_state.get("api_key_valid"):
            st.warning("Please enter a valid API key in the sidebar")
            return

    # Initialize ExercisePlanner if not already
        if "exercise_planner" not in st.session_state:
            st.session_state.exercise_planner = ExercisePlanner(user_id="default")

        question = st.text_input("What would you like to know about your sleep and exercise habits?")

        if question and st.button("Get Advice"):
            with st.spinner("Analyzing your lifestyle patterns..."):
            # Load recent sleep entries
                last_sleep_entries = manager.get_last_entries(7)
            # Load recent exercise entries
                exercise_summary = st.session_state.exercise_planner.get_weekly_summary()

            # Create a richer context for OpenAI
                sleep_context = "\n".join(
                f"{log['date']}: {log['hours']}h sleep, {log['quality']}/100 quality"
                for log in last_sleep_entries
            )

                exercise_context = (
                f"Total exercise hours this week: {exercise_summary.get('total_hours', 0)}\n"
                f"Number of sessions: {exercise_summary.get('sessions', 0)}\n"
                f"Activities: {exercise_summary.get('activity_breakdown', {})}"
            )

            # Combine both contexts
                full_context = (
                f"User Sleep Data (Last 7 Days):\n{sleep_context}\n\n"
                f"User Exercise Data (Last 7 Days):\n{exercise_context}\n\n"
                "Analyze how sleep and exercise might be interacting, and give the user personalized advice."
            )

            # Send to OpenAI
                response = st.session_state.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                    {"role": "system", "content": "You're a professional lifestyle coach specialized in sleep and exercise optimization."},
                    {"role": "user", "content": f"{full_context}\n\nQuestion: {question}"}
                    ],
                    temperature=0.7
            )

                st.subheader("Coach's Response")
                st.write(response.choices[0].message.content)
    with tab4:
        st.header("🏃‍♂️ Exercise Planner")
    
    # Initialize Exercise Planner
        if "exercise_planner" not in st.session_state:
            st.session_state.exercise_planner = ExercisePlanner(user_id="default")
    
    # Exercise Logging Form
        with st.form("exercise_form"):
            activity = st.selectbox("Activity Type", ["Cardio", "Walking", "Running", "Fitness Class", "Other"])
            duration = st.slider("Duration in Hours", 0.0, 6.0, step=0.5)
            notes = st.text_input("Notes (optional)")
            submit_exercise = st.form_submit_button("Log Exercise")
        
            if submit_exercise:
                st.session_state.exercise_planner.log_exercise(activity_type=activity, duration_hours=duration, notes=notes)
                st.success(f"Logged {activity} for {duration} hours!")

    # Weekly Exercise Summary
        st.subheader("Weekly Exercise Summary")
        summary = st.session_state.exercise_planner.get_weekly_summary()
    
        if summary:
            st.metric("Total Exercise Time", f"{summary['total_hours']} hours")
            st.metric("Exercise Sessions", f"{summary['sessions']}")
            st.write("Activity Breakdown:")
            st.json(summary['activity_breakdown'])
        else:
            st.info("No exercises logged yet.")


if __name__ == "__main__":
    main()
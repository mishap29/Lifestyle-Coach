# Lifestyle-Coach
🏄 Lifestyle Coach – Sleep and Exercise Tracker
Lifestyle Coach is a Streamlit-based application designed to help users track, visualize, and improve their sleep and exercise habits.
It combines personal data logging, data visualizations, and AI-driven personalized advice using OpenAI's API.

📋 Features
🛌 Sleep Logger:
Record nightly sleep hours, sleep quality, and personal notes.

🏋️‍♂️ Exercise Tracker:
Log different types of exercise activities (Cardio, Running, Walking, Fitness Class, Other) and duration.

📊 Trends Dashboard:
Interactive Plotly visualizations showing sleep patterns and exercise activity summaries over time.

🧠 AI Coaching:
Personalized lifestyle coaching based on sleep and exercise data, powered by OpenAI's GPT model.

🎯 Goal Tracking:
Set personal goals for sleep duration and quality, and monitor progress visually.

📚 Scientific Knowledge Base:
Built-in sleep and health facts support coaching responses with research-backed information.

📂 Project Structure
lifestyle-coach/
├── src/
│   ├── app.py                  # Main Streamlit app
│   ├── coach.py                 # SleepCoach class
│   ├── exercise.py              # ExercisePlanner class
│   ├── analyzer.py              # Combined sleep/exercise analysis
│   ├── visualizations.py        # Graphing and plotting
│   ├── config.py                # API key management
├── data/
│   ├── processed/               # User-specific JSON data
│   ├── processed.py             # Load/save data functions
│   ├── sleep_database.py        # Static sleep advice database
│   ├── knowledge_base.json      # Facts for coaching
├── venv/                        # Virtual environment
├── .env                         # API keys (private)
├── .gitignore                   # Ignored files list
└── requirements.txt             # Python dependencies

🛠 How to Run Locally
# Clone this repository
git clone https://github.com/your-username/lifestyle-coach.git
cd lifestyle-coach

# Create and activate a virtual environment (Windows example)
python -m venv venv
.\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Add your OpenAI API key to a `.env` file
echo OPENAI_API_KEY=your-openai-key-here > .env

# Run the app
streamlit run src/app.py

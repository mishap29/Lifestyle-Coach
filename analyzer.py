from data.sleep_database import SLEEP_ISSUES, get_sleep_issue_info
from openai import OpenAI
import json
from src.config import Config

class LifestyleAnalyzer:
    def __init__(self, user_id: str = "default"):
        ...
        self.client = OpenAI(api_key=Config.OPENAI_KEY)
        self.knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self) -> dict:
        with open("data/knowledge_base.json", "r") as f:
            return json.load(f)

    def generate_ai_advice(self, user_context: str) -> str:
        """
        Use OpenAI to generate smarter, science-based advice.
        Args:
            user_context: Summary of user's sleep/exercise situation
        Returns:
            AI-generated coaching advice.
        """
        facts = "\n".join(self.knowledge_base.get("sleep", []) + self.knowledge_base.get("exercise", []))

        prompt = (
            f"You are a professional health coach. Base your advice on scientific facts.\n"
            f"USER CONTEXT: {user_context}\n"
            f"SCIENTIFIC FACTS:\n{facts}\n\n"
            "Give a detailed but concise advice paragraph, citing at least one scientific source."
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert health and lifestyle coach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ AI advice unavailable: {str(e)}"

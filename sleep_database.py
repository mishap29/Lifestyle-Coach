# data/sleep_database.py

from typing import Dict, Any

SLEEP_ISSUES = {
    "difficulty_falling_asleep": {
        "description": "Difficulty falling asleep is often caused by stress, late-night screen use, caffeine consumption, or inconsistent sleep routines.",
        "recommendations": [
            "Establish a consistent bedtime and wake-up time, even on weekends.",
            "Limit screen use at least 1 hour before bed (blue light affects melatonin production).",
            "Avoid caffeine after 2 PM.",
            "Create a relaxing pre-sleep routine, such as reading or meditation."
        ]
    },
    "frequent_night_wakings": {
        "description": "Waking up frequently during the night can be linked to anxiety, noise disruptions, sleep apnea, or consuming heavy meals before bedtime.",
        "recommendations": [
            "Keep your bedroom cool, dark, and quiet.",
            "Avoid heavy meals and alcohol within 3 hours of bedtime.",
            "Consider white noise machines or earplugs if environmental noise is an issue.",
            "If persistent, consult a sleep specialist for possible underlying disorders."
        ]
    },
    "poor_sleep_quality": {
        "description": "Poor sleep quality means not feeling rested even after sleeping enough hours. It may be linked to stress, poor sleep hygiene, or hidden medical conditions.",
        "recommendations": [
            "Prioritize deep sleep by sticking to a regular sleep schedule.",
            "Avoid stimulating activities close to bedtime.",
            "Limit naps during the day to no more than 30 minutes.",
            "Ensure your mattress and pillows are supportive and comfortable."
        ]
    },
    "sleeping_too_late": {
        "description": "Sleeping very late (delayed sleep phase) can affect morning alertness, productivity, and mental health.",
        "recommendations": [
            "Shift your bedtime earlier by 15-minute increments over several nights.",
            "Expose yourself to bright natural light early in the morning.",
            "Avoid exposure to bright lights and screens at night.",
            "Consider melatonin supplements under a doctor's supervision."
        ]
    }
}

def get_sleep_issue_info(issue_key: str) -> Dict[str, Any]:
    """
    Retrieve structured information about a specific sleep problem.
    
    Args:
        issue_key (str): The key identifying the sleep issue (e.g., 'difficulty_falling_asleep')
    
    Returns:
        dict: Dictionary containing description and recommendations, or empty dict if not found.
    """
    return SLEEP_ISSUES.get(issue_key, {})

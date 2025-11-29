# src/motivation.py
import random
from datetime import date

MESSAGES = [
    "Day by day, brick by brick. You're building an empire.",
    "Most people quit on day 0. You opened the app again. That’s already the 1%.",
    "Your future millionaire self is watching and smiling right now.",
    "R136 479 + R399/month at 8% → R1.4 million. That’s not a dream. That’s math.",
    "Unemployed today ≠ unemployed forever. Every application is a deposit.",
    "The compound interest on discipline is freedom.",
    "You don’t need to be great to start, but you have to start to be great.",
    "Someone out there is praying for the exact skills you’re building right now.",
    "Keep going. The version of you in 2030 is begging you not to stop.",
]

def daily_message() -> str:
    today = date.today()
    random.seed(today.toordinal())  # same message all day
    return random.choice(MESSAGES)
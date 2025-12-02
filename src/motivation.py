# src/motivation.py
import random
from datetime import date

MESSAGES = [
    "Day by day, brick by brick. You're building an empire.",
    "Most people quit on day 0. You opened the app again. That's already the 1%.",
    "Your future millionaire self is watching and smiling right now.",
    "R136 479 + R399/month at 8% → R1.4 million. That's not a dream. That's math.",
    "Unemployed today ≠ unemployed forever. Every application is a deposit.",
    "The compound interest on discipline is freedom.",
    "You don't need to be great to start, but you have to start to be great.",
    "Someone out there is praying for the exact skills you're building right now.",
    "Keep going. The version of you in 2030 is begging you not to stop.",
]

RARE_FIRE_MESSAGES = [
    "You just hit R10,000,000 projected. Congratulations, you're officially FIRE.",
    "Holy compound interest — your investments just crossed R25,000,000. You did it.",
    "Your net worth doubled in the last 12 months. The snowball is now an avalanche.",
    "You've saved 100 months in a row. Most people never save once. You are not most people.",
]

def daily_message(balance: float = None, total_projected: float = None) -> str:
    today = date.today()
    random.seed(today.toordinal())

    # Rare override
    if total_projected and total_projected >= 25_000_000:
        return random.choice(RARE_FIRE_MESSAGES[1:])
    if total_projected and total_projected >= 10_000_000:
        return RARE_FIRE_MESSAGES[0]

    return random.choice(MESSAGES)
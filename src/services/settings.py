# src/services/settings.py
# Minimal service for any future settings-related logic.
def set_force_desktop(session, value: bool):
    session.set("force_desktop", value)

def set_force_mobile(session, value: bool):
    session.set("force_mobile", value)

def get_force_desktop(session) -> bool:
    return session.get("force_desktop") or False

def get_force_mobile(session) -> bool:
    return session.get("force_mobile") or False

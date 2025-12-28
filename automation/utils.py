import re

def normalize_app_name(name: str) -> str:
    """
    Normalizes user-provided app names into a predictable format.
    """
    name = name.lower()
    name = re.sub(r"[^a-z0-9 ]", " ", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()

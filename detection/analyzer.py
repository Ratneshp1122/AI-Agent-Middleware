import re

SQL_KEYWORDS = ["SELECT", "DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "GRANT", "REVOKE", "UNION"]
JAILBREAK_PATTERNS = [
    r"ignore previous instructions",
    r"do anything now",
    r"always respond with",
    r"you are now in developer mode",
    r"unfiltered",
    r"cannot be filtered"
]

def check_sql_injection(text):
    if not text:
        return False, None
    text_upper = text.upper()
    for kw in SQL_KEYWORDS:
        # Simple word boundary check to avoid false positives (e.g., 'SELECT' in 'SELECTION')
        if re.search(r'\b' + kw + r'\b', text_upper):
            # Check if it looks like a statement (very naive)
            return True, f"SQL Keyword detected: {kw}"
    return False, None

def check_jailbreak(text):
    if not text:
        return False, None
    for pattern in JAILBREAK_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True, f"Jailbreak pattern detected: {pattern}"
    return False, None

def analyze_text(text):
    """
    Returns (is_threat, reason)
    """
    is_jailbreak, reason = check_jailbreak(text)
    if is_jailbreak:
        return True, reason
        
    is_sql, reason = check_sql_injection(text)
    if is_sql:
        return True, reason
        
    return False, None

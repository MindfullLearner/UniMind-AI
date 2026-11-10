
import re


INJECTION_PATTERNS = {
    "ignore_instructions": r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    "reveal_system_prompt": r"reveal\s+(the\s+)?(system prompt|hidden instructions)",
    "override_instructions": r"override\s+(all\s+)?(previous|system)\s+instructions",
    "disregard_instructions": r"disregard\s+(all\s+)?(previous|prior)\s+instructions",
    "unrestricted_ai": r"act\s+as\s+(an\s+)?(unrestricted|unfiltered)",
    "jailbreak": r"\bjailbreak\b",
    "developer_message": r"developer message",
    "bypass_safety": r"bypass\s+(the\s+)?safety",
}


def detect_prompt_injection(text):
    """
    Detect common prompt-injection patterns in text.
    """

    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    matched_patterns = []

    for pattern_name, pattern in INJECTION_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            matched_patterns.append(pattern_name)

    return {
        "is_suspicious": len(matched_patterns) > 0,
        "matched_patterns": matched_patterns,
    }


EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

PHONE_PATTERN = (
    r"(?<!\w)"
    r"(?:\+92[\s-]?3\d{2}|03\d{2})[\s-]?\d{7}"
    r"(?!\w)"
)


def redact_pii(text):
    """
    Detect and redact email addresses and Pakistani mobile numbers.
    """

    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    email_matches = re.findall(EMAIL_PATTERN, text)
    phone_matches = re.findall(PHONE_PATTERN, text)

    redacted_text = re.sub(
        EMAIL_PATTERN,
        "[REDACTED_EMAIL]",
        text
    )

    redacted_text = re.sub(
        PHONE_PATTERN,
        "[REDACTED_PHONE]",
        redacted_text
    )

    return {
        "redacted_text": redacted_text,
        "detected_pii": {
            "emails": len(email_matches),
            "phone_numbers": len(phone_matches),
        },
        "has_pii": bool(email_matches or phone_matches),
    }

def scan_text(text):
    """
    Scan text for prompt injection and redact PII.
    """

    injection_result = detect_prompt_injection(text)
    pii_result = redact_pii(text)

    return {
        "is_suspicious": injection_result["is_suspicious"],
        "matched_patterns": injection_result["matched_patterns"],
        "redacted_text": pii_result["redacted_text"],
        "detected_pii": pii_result["detected_pii"],
        "has_pii": pii_result["has_pii"],
    }

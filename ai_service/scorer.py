def analyze_lead(lead):

    message = lead["message"].lower()

    score = 0
    reasons = []

    # Purchase intent
    intent_words = [
        "buy",
        "purchase",
        "need",
        "interested",
        "demo",
        "quotation",
        "price"
    ]

    intent_count = sum(
        word in message
        for word in intent_words
    )

    if intent_count > 0:
        score += 20
        reasons.append(
            "The message indicates purchase intent."
        )

    # Urgency
    urgency_words = [
        "urgent",
        "as soon as possible",
        "immediately",
        "today",
        "this week"
    ]

    if any(word in message for word in urgency_words):
        score += 15
        reasons.append(
            "The lead indicates urgency."
        )

    # Budget indication
    if lead.get("budget"):
        score += 15
        reasons.append(
            "The lead has provided a budget."
        )

    # Repeat lead
    if lead.get("repeat_lead"):
        score += 10
        reasons.append(
            "This is a repeat lead."
        )

    # Limit score
    score = min(score, 100)

    if score >= 70:
        category = "HOT"

    elif score >= 40:
        category = "WARM"

    else:
        category = "COLD"

    reason = " ".join(reasons)

    if not reason:
        reason = "Low purchase intent detected."

    return {
        "score": score,
        "category": category,
        "reason": reason
    }
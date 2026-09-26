from ..models import ScoringConfig


def get_weight(factor_name):

    config = ScoringConfig.objects.filter(
        factor_name=factor_name,
        is_active=True
    ).first()

    if config:
        return config.weight

    return 0
def calculate_final_score(lead, ai_result):

    ai_score = ai_result["score"]

    final_score = ai_score

    rule_breakdown = {}

    # -----------------------------
    # High budget
    # -----------------------------

    if lead.budget and lead.budget >= 100000:

        weight = get_weight("high_budget")

        final_score += weight

        rule_breakdown["high_budget"] = weight

    # -----------------------------
    # Referral
    # -----------------------------

    if lead.source.lower() == "referral":

        weight = get_weight("referral_source")

        final_score += weight

        rule_breakdown["referral_source"] = weight

    # -----------------------------
    # Repeat lead
    # -----------------------------

    if lead.repeat_lead:

        weight = get_weight("repeat_lead")

        final_score += weight

        rule_breakdown["repeat_lead"] = weight

    # -----------------------------
    # Maximum 100
    # -----------------------------

    final_score = min(
        final_score,
        100
    )

    # -----------------------------
    # Category
    # -----------------------------

    if final_score >= 70:

        category = "HOT"

    elif final_score >= 40:

        category = "WARM"

    else:

        category = "COLD"

    return {
        "final_score": final_score,
        "category": category,
        "rule_breakdown": rule_breakdown
    }
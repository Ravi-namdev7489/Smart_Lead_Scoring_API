import requests


AI_SERVICE_URL = "http://127.0.0.1:8001/score"


def score_lead_with_ai(lead):

    payload = {
        "name": lead.name,
        "email": lead.email,
        "phone": lead.phone,
        "message": lead.message,
        "source": lead.source,
        "budget": float(lead.budget)
        if lead.budget else None,
        "company": lead.company,
        "repeat_lead": lead.repeat_lead
    }

    response = requests.post(
        AI_SERVICE_URL,
        json=payload,
        timeout=5
    )

    response.raise_for_status()

    return response.json()
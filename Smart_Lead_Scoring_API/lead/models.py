from django.db import models

# Create your models here.
from django.db import models


class Lead(models.Model):

    SOURCE_CHOICES = [
        ("website", "Website"),
        ("whatsapp", "WhatsApp"),
        ("email", "Email"),
        ("instagram", "Instagram"),
        ("referral", "Referral"),
    ]

    STATUS_CHOICES = [
        ("SCORED", "Scored"),
        ("PENDING_SCORE", "Pending Score"),
        ("DUPLICATE", "Duplicate"),
    ]

    CATEGORY_CHOICES = [
        ("HOT", "Hot"),
        ("WARM", "Warm"),
        ("COLD", "Cold"),
    ]

    name = models.CharField(max_length=150)

    email = models.EmailField(
        null=True,
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    message = models.TextField()

    source = models.CharField(
        max_length=50,
        choices=SOURCE_CHOICES
    )

    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    company = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )

    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        null=True,
        blank=True
    )

    latest_score = models.FloatField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING_SCORE"
    )

    repeat_lead = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )
    def __str__(self):
        return f"{self.name}"

class ScoringConfig(models.Model):

    factor_name = models.CharField(
        max_length=100,
        unique=True
    )

    weight = models.FloatField()

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.factor_name} - {self.weight}"
from django.db import models


class ScoreAudit(models.Model):
    lead_id = models.IntegerField()

    model_name = models.CharField(
        max_length=100
    )

    raw_ai_response = models.JSONField()

    rule_breakdown = models.JSONField()

    final_score = models.FloatField()

    scored_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "score_audit"

    def __str__(self):
        return f"Lead {self.lead_id} - {self.final_score}"
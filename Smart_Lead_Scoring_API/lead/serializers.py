from rest_framework import serializers
from .models import Lead


class LeadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lead
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "message",
            "source",
            "budget",
            "company",
            "category",
            "latest_score",
            "status",
            "repeat_lead",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "category",
            "latest_score",
            "status",
            "repeat_lead",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):

        email = data.get("email")
        phone = data.get("phone")

        # At least email or phone is required
        if not email and not phone:
            raise serializers.ValidationError(
                "Either email or phone is required."
            )

        return data

    def validate_name(self, value):

        if not value.strip():
            raise serializers.ValidationError(
                "Name cannot be empty."
            )

        return value

    def validate_message(self, value):

        if not value.strip():
            raise serializers.ValidationError(
                "Message cannot be empty."
            )

        return value

    def validate_budget(self, value):

        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Budget cannot be negative."
            )

        return value

class BatchLeadSerializer(serializers.Serializer):
    leads = LeadSerializer(many=True)

    def validate_leads(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                "At least one lead is required."
            )

        if len(value) > 50:
            raise serializers.ValidationError(
                "Maximum 50 leads are allowed per batch."
            )

        return value
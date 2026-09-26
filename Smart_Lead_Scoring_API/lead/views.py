from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Lead
from .serializers import LeadSerializer,BatchLeadSerializer
from .services.ai_services import score_lead_with_ai
from .services.scoring import calculate_final_score

from .models import ScoreAudit
class LeadCreateAPIView(APIView):

    def post(self, request):

        serializer = LeadSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data.get("email")
        phone = serializer.validated_data.get("phone")

        lead = None

        # --------------------------------
        # Duplicate detection
        # --------------------------------

        if email:
            lead = Lead.objects.filter(
                email=email
            ).first()

        if not lead and phone:
            lead = Lead.objects.filter(
                phone=phone
            ).first()

        # --------------------------------
        # Duplicate lead
        # --------------------------------

        if lead:

            for field, value in serializer.validated_data.items():
                setattr(lead, field, value)

            lead.repeat_lead = True
            lead.status = "PENDING_SCORE"

            lead.save()

        # --------------------------------
        # New lead
        # --------------------------------

        else:

            lead = serializer.save(
                repeat_lead=False,
                status="PENDING_SCORE"
            )

        # --------------------------------
        # AI + Hybrid scoring
        # --------------------------------

        try:

            ai_result = score_lead_with_ai(lead)

            print("AI RESULT:", ai_result)

            final_result = calculate_final_score(
                lead,
                ai_result
            )

            print("FINAL RESULT:", final_result)

            # IMPORTANT
            lead.latest_score = final_result["final_score"]
            lead.category = final_result["category"]
            lead.status = "SCORED"

            lead.save()

        except Exception as e:

            # Don't hide the real error
            print("SCORING ERROR:", str(e))

            lead.status = "PENDING_SCORE"
            lead.save()

            return Response(
                {
                    "message": "Lead saved but AI scoring is pending.",
                    "error": str(e),
                    "lead": LeadSerializer(lead).data
                },
                status=status.HTTP_202_ACCEPTED
            )

        return Response(
            {
                "message": "Lead scored successfully",

                "lead": LeadSerializer(lead).data,

                "ai": ai_result,

                "final_score": final_result["final_score"],

                "category": final_result["category"],

                "rule_breakdown": final_result["rule_breakdown"]
            },
            status=status.HTTP_200_OK
        )
class LeadBatchCreateAPIView(APIView):

    def post(self, request):

        serializer = BatchLeadSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        leads_data = serializer.validated_data["leads"]

        results = []

        for lead_data in leads_data:

            # -----------------------------
            # 1. Check duplicate
            # -----------------------------

            email = lead_data.get("email")
            phone = lead_data.get("phone")

            lead = None

            if email:
                lead = Lead.objects.filter(
                    email=email
                ).first()

            if not lead and phone:
                lead = Lead.objects.filter(
                    phone=phone
                ).first()

            # -----------------------------
            # 2. Create / Update Lead
            # -----------------------------

            if lead:

                for field, value in lead_data.items():
                    setattr(
                        lead,
                        field,
                        value
                    )

                lead.repeat_lead = True
                lead.status = "PENDING_SCORE"
                lead.save()

            else:

                lead = Lead.objects.create(
                    **lead_data,
                    repeat_lead=False,
                    status="PENDING_SCORE"
                )

            # -----------------------------
            # 3. Call FastAPI
            # -----------------------------

            try:

                ai_result = score_lead_with_ai(
                    lead
                )

                # -----------------------------
                # 4. Hybrid scoring
                # -----------------------------

                final_result = calculate_final_score(
                    lead,
                    ai_result
                )

                # -----------------------------
                # 5. Update MySQL Lead
                # -----------------------------

                lead.latest_score = (
                    final_result["final_score"]
                )

                lead.category = (
                    final_result["category"]
                )

                lead.status = "SCORED"

                lead.save()

                # -----------------------------
                # 6. Save audit in SQLite
                # -----------------------------

                ScoreAudit.objects.create(
                    lead_id=lead.id,
                    model_name="lead-intent-v1",
                    raw_ai_response=ai_result,
                    rule_breakdown=(
                        final_result["rule_breakdown"]
                    ),
                    final_score=(
                        final_result["final_score"]
                    )
                )

                # -----------------------------
                # 7. Add result
                # -----------------------------

                results.append({
                    "lead_id": lead.id,
                    "score": final_result[
                        "final_score"
                    ],
                    "category": final_result[
                        "category"
                    ],
                    "status": "SCORED"
                })

            except Exception as e:

                print(
                    "BATCH SCORING ERROR:",
                    str(e)
                )

                lead.status = "PENDING_SCORE"
                lead.save()

                results.append({
                    "lead_id": lead.id,
                    "score": None,
                    "category": None,
                    "status": "PENDING_SCORE"
                })

        return Response(
            {
                "message": "Batch processed successfully",
                "total": len(results),
                "results": results
            },
            status=status.HTTP_200_OK
        )
from django.db.models import Count, Avg
class LeadAnalyticsAPIView(APIView):

    def get(self, request):

        # Total leads
        total_leads = Lead.objects.count()

        # HOT / WARM / COLD breakdown
        category_breakdown = {
            "HOT": Lead.objects.filter(
                category="HOT"
            ).count(),

            "WARM": Lead.objects.filter(
                category="WARM"
            ).count(),

            "COLD": Lead.objects.filter(
                category="COLD"
            ).count(),
        }

        # Average score per source
        average_score = (
            Lead.objects
            .filter(latest_score__isnull=False)
            .values("source")
            .annotate(
                average_score=Avg("latest_score")
            )
            .order_by("source")
        )

        average_score_per_source = {}

        for item in average_score:
            average_score_per_source[
                item["source"]
            ] = round(
                item["average_score"],
                2
            )

        # Top 5 hottest leads
        top_leads = (
            Lead.objects
            .filter(latest_score__isnull=False)
            .order_by("-latest_score")[:5]
        )

        top_5_hottest_leads = []

        for lead in top_leads:

            top_5_hottest_leads.append({
                "id": lead.id,
                "name": lead.name,
                "email": lead.email,
                "phone": lead.phone,
                "source": lead.source,
                "score": lead.latest_score,
                "category": lead.category,
            })

        return Response({
            "total_leads": total_leads,

            "category_breakdown": (
                category_breakdown
            ),

            "average_score_per_source": (
                average_score_per_source
            ),

            "top_5_hottest_leads": (
                top_5_hottest_leads
            ),
        })
class LeadRescoreAPIView(APIView):

    def get(self, request, lead_id):

        try:
            lead = Lead.objects.get(id=lead_id)

        except Lead.DoesNotExist:
            return Response(
                {
                    "error": "Lead not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Call FastAPI
            ai_result = score_lead_with_ai(lead)

            # Hybrid scoring
            final_result = calculate_final_score(
                lead,
                ai_result
            )

            # Update lead
            lead.latest_score = final_result["final_score"]
            lead.category = final_result["category"]
            lead.status = "SCORED"
            lead.save()

            # Save audit in SQLite
            ScoreAudit.objects.using("sqlite").create(
                lead_id=lead.id,
                model_name="lead-intent-v1",
                raw_ai_response=ai_result,
                rule_breakdown=final_result["rule_breakdown"],
                final_score=final_result["final_score"]
            )

            return Response(
                {
                    "message": "Lead rescored successfully",
                    "lead_id": lead.id,
                    "score": final_result["final_score"],
                    "category": final_result["category"],
                    "rule_breakdown": final_result["rule_breakdown"],
                    "status": lead.status
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:

            print("RESCORE ERROR:", str(e))

            lead.status = "PENDING_SCORE"
            lead.save()

            return Response(
                {
                    "message": "Lead scoring is pending",
                    "lead_id": lead.id,
                    "status": "PENDING_SCORE",
                    "error": str(e)
                },
                status=status.HTTP_202_ACCEPTED
            )
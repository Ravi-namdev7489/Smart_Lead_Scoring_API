from django.urls import path
from .views import LeadCreateAPIView,LeadBatchCreateAPIView,LeadAnalyticsAPIView,LeadRescoreAPIView

urlpatterns = [
    path('leads/', 
        LeadCreateAPIView.as_view()
),
    path('leads/batch/', 
         
        LeadBatchCreateAPIView.as_view()
),
    path(
    "leads/analytics/",
    LeadAnalyticsAPIView.as_view(),
    name="lead-analytics"
),
    path(
    "leads/<int:lead_id>/rescore/",
    LeadRescoreAPIView.as_view(),
    name="lead-rescore"
),
]
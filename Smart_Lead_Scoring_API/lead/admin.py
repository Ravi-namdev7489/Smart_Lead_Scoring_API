from django.contrib import admin
from .models import Lead,ScoringConfig,ScoreAudit
# Register your models here.
admin.site.register(Lead)
admin.site.register(ScoringConfig)
admin.site.register(ScoreAudit)

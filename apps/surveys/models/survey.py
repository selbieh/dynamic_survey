from django.core.cache import cache
from django.db import models
from apps.base.models import CustomBaseModel


class Survey(CustomBaseModel):
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField()
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=True)
    created_by = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="created_surveys")

    def save(self, *args, **kwargs):
        cache.clear()
        return super().save(*args, **kwargs)


class SurveyResponse(CustomBaseModel):
    survey = models.ForeignKey("surveys.Survey", on_delete=models.CASCADE, related_name="responses")
    respondent = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="survey_responses")
    is_completed = models.BooleanField(default=False)
    is_submitted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('survey', 'respondent')

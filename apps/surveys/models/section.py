from django.db import models
from apps.base.models import CustomBaseModel


class Section(CustomBaseModel):
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField()
    survey = models.ForeignKey("surveys.Survey", on_delete=models.CASCADE, related_name="sections")

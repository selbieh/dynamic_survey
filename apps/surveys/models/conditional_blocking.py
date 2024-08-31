from django.db import models
from apps.base.models import CustomBaseModel


class ConditionalBlocking(CustomBaseModel):
    choice = models.ForeignKey("surveys.QuestionChoice", on_delete=models.CASCADE, related_name="blocking_choices")
    question = models.ForeignKey("surveys.Question", on_delete=models.CASCADE, related_name="blocked_questions")

    class Meta:
        unique_together = ('choice', 'question')

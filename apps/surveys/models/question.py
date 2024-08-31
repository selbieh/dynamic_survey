import datetime
from django.db import models
from apps.base.models import CustomBaseModel


class QuestionType(models.TextChoices):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    RADIO_BUTTON = "radio button"


ChoiceQuestionType = [QuestionType.DROPDOWN, QuestionType.CHECKBOX, QuestionType.RADIO_BUTTON]


class Question(CustomBaseModel):
    text = models.TextField()
    order = models.PositiveIntegerField()
    type = models.CharField(max_length=50, choices=QuestionType.choices, default=QuestionType.TEXT)
    section = models.ForeignKey("surveys.Section", on_delete=models.CASCADE, related_name="questions")

    def requires_choices(self) -> bool:
        return self.type in ChoiceQuestionType


class QuestionChoice(CustomBaseModel):
    choice = models.TextField()
    question = models.ForeignKey("surveys.Question", on_delete=models.CASCADE, related_name="choices")


class QuestionAnswer(CustomBaseModel):
    text_answer = models.TextField(null=True)
    question = models.ForeignKey("surveys.Question", on_delete=models.CASCADE, related_name="respondent_answers")
    survey_response = models.ForeignKey("surveys.SurveyResponse", on_delete=models.CASCADE, related_name="answers")
    question_choices = models.ManyToManyField("surveys.QuestionChoice", through="QuestionAnswerQuestionChoice")

    class Meta:
        unique_together = ('survey_response', 'question')

    @classmethod
    def is_valid_text_answer(cls, text_answer: str, question_type: QuestionType) -> bool:
        if question_type == QuestionType.NUMBER:
            try:
                int(text_answer)
                return True
            except ValueError:
                return False

        if question_type == QuestionType.DATE:
            try:
                datetime.date.fromisoformat(text_answer)
                return True
            except ValueError:
                return False

        return True

    def save(self, *args, **kwargs):
        response = super().save(*args, **kwargs)

        # update the survey response status
        from apps.surveys.tasks import check_and_update_survey_response_status
        check_and_update_survey_response_status.delay(survey_response_id=self.survey_response.id)

        return response


class QuestionAnswerQuestionChoice(CustomBaseModel):
    question_answer = models.ForeignKey("surveys.QuestionAnswer", on_delete=models.CASCADE, related_name="choices")
    question_choice = models.ForeignKey("surveys.QuestionChoice", on_delete=models.CASCADE, related_name="answers")

    class Meta:
        unique_together = ('question_answer', 'question_choice')

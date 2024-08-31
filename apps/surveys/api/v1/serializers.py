from rest_framework.serializers import (ModelSerializer, HiddenField, CurrentUserDefault,
                                        ValidationError, PrimaryKeyRelatedField)
from rest_framework.validators import UniqueTogetherValidator
from apps.surveys.models import (Survey, Section, Question, QuestionChoice, SurveyResponse, QuestionAnswer,
                                 ConditionalBlocking)


class SurveySerializer(ModelSerializer):
    created_by = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Survey
        fields = ["name", "description", "start_date", "end_date", "created_by"]


class SurveyReadOnlySerializer(ModelSerializer):
    class Meta:
        model = Survey
        fields = "__all__"


class SectionSerializer(ModelSerializer):
    class Meta:
        model = Section
        fields = ["name", "description", "survey"]


class SectionReadOnlySerializer(ModelSerializer):
    class Meta:
        model = Section
        fields = "__all__"


class QuestionSerializer(ModelSerializer):
    class Meta:
        model = Question
        fields = ["text", "order", "type", "section"]

    def validate(self, attrs):
        section = attrs.get('section')
        order = attrs.get('order')

        if Question.objects.filter(section__survey=section.survey, order=order).exists():
            raise ValidationError("A question with this order in the given survey already exists.")

        return attrs


class QuestionReadOnlySerializer(ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


class QuestionChoiceSerializer(ModelSerializer):
    class Meta:
        model = QuestionChoice
        fields = ["choice", "question"]

    def validate_question(self, question):
        if not question.requires_choices():
            raise ValidationError("You cannot assign choices to this question.")

        return question


class QuestionChoiceReadOnlySerializer(ModelSerializer):
    class Meta:
        model = QuestionChoice
        fields = "__all__"


class SurveyResponseSerializer(ModelSerializer):
    respondent = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = SurveyResponse
        fields = ["survey", "respondent"]


class SurveyResponseReadOnlySerializer(ModelSerializer):
    class Meta:
        model = SurveyResponse
        fields = "__all__"


class QuestionAnswerSerializer(ModelSerializer):
    question_choices = PrimaryKeyRelatedField(queryset=QuestionChoice.objects.all(), many=True, required=False)

    class Meta:
        model = QuestionAnswer
        fields = ["text_answer", "question", "survey_response", "question_choices"]

    def validate_survey_response(self, survey_response):
        current_user = self.context.get("current_user")

        if current_user != survey_response.respondent:
            raise ValidationError("This survey response does not belong to the current user.")

        return survey_response

    def validate(self, attrs):
        text_answer = attrs.get("text_answer")
        question = attrs.get("question")
        question_choices = attrs.get("question_choices")

        if text_answer and question_choices:
            raise ValidationError("You cannot pick a choice while submitting an text answer.")

        if question.requires_choices():
            if not question_choices:
                raise ValidationError("You must pick at least one choice.")

            for question_choice in question_choices:
                if question_choice.question != question:
                    raise ValidationError("Not all choices belong to this question.")
        else:
            if not text_answer:
                raise ValidationError("You must write an answer.")

            if not QuestionAnswer.is_valid_text_answer(text_answer=text_answer, question_type=question.type):
                raise ValidationError("You must enter a valid answer that matches the question type.")

        return attrs


class QuestionAnswerReadOnlySerializer(ModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = "__all__"


class ConditionalBlockingSerializer(ModelSerializer):
    class Meta:
        model = ConditionalBlocking
        fields = ["choice", "question"]

    def validate(self, attrs):
        choice = attrs.get("choice")
        question = attrs.get("question")

        if question.order <= choice.question.order:
            raise ValidationError("A choice can only block upcoming questions.")

        return attrs


class ConditionalBlockingReadOnlySerializer(ModelSerializer):
    class Meta:
        model = ConditionalBlocking
        fields = "__all__"

import django_filters
from apps.surveys.models import (Survey, Section, Question, QuestionChoice, SurveyResponse, QuestionAnswer,
                                 ConditionalBlocking)


class SurveyFilter(django_filters.FilterSet):
    start_date_from = django_filters.DateFilter(field_name="start_date", lookup_expr="gte")
    start_date_to = django_filters.DateFilter(field_name="start_date", lookup_expr="lte")
    start_date_on = django_filters.DateFilter(field_name="start_date", lookup_expr="exact")
    end_date_from = django_filters.DateFilter(field_name="end_date", lookup_expr="gte")
    end_date_to = django_filters.DateFilter(field_name="end_date", lookup_expr="lte")
    end_date_on = django_filters.DateFilter(field_name="end_date", lookup_expr="exact")

    class Meta:
        model = Survey
        fields = ["created_by", "start_date_from", "start_date_to", "start_date_on",
                  "end_date_from", "end_date_to", "end_date_on"]


class SectionFilter(django_filters.FilterSet):
    class Meta:
        model = Section
        fields = ["survey"]


class QuestionFilter(django_filters.FilterSet):
    class Meta:
        model = Question
        fields = ["type", "section"]


class QuestionChoiceFilter(django_filters.FilterSet):
    class Meta:
        model = QuestionChoice
        fields = ["question"]


class SurveyResponseFilter(django_filters.FilterSet):
    class Meta:
        model = SurveyResponse
        fields = ["survey", "respondent", "is_completed", "is_submitted"]


class QuestionAnswerFilter(django_filters.FilterSet):
    class Meta:
        model = QuestionAnswer
        fields = ["question", "survey_response"]


class ConditionalBlockingFilter(django_filters.FilterSet):
    class Meta:
        model = ConditionalBlocking
        fields = ["choice", "question"]

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import DjangoModelPermissions, SAFE_METHODS
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from apps.surveys.models import (Survey, Section, Question, QuestionChoice, SurveyResponse, QuestionAnswer,
                                 ConditionalBlocking)
from apps.surveys.api.v1.serializers import (SurveySerializer, SurveyReadOnlySerializer,
                                             SectionSerializer, SectionReadOnlySerializer,
                                             QuestionSerializer, QuestionReadOnlySerializer,
                                             QuestionChoiceSerializer, QuestionChoiceReadOnlySerializer,
                                             SurveyResponseSerializer, SurveyResponseReadOnlySerializer,
                                             QuestionAnswerSerializer, QuestionAnswerReadOnlySerializer,
                                             ConditionalBlockingSerializer, ConditionalBlockingReadOnlySerializer)
from apps.surveys.filters import (SurveyFilter, SectionFilter, QuestionFilter, QuestionChoiceFilter,
                                  SurveyResponseFilter, QuestionAnswerFilter, ConditionalBlockingFilter)
from apps.surveys.utility import generate_cache_key


class SurveyViewSet(ModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = Survey.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = SurveyFilter
    search_fields = ["name", "description"]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return SurveyReadOnlySerializer

        return SurveySerializer

    @method_decorator(cache_page(settings.CACHING_TIME_IN_SECONDS, key_prefix=lambda request: request.get_full_path()))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class SectionViewSet(ModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = Section.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = SectionFilter
    search_fields = ["name", "description"]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return SectionReadOnlySerializer

        return SectionSerializer


class QuestionViewSet(ModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = Question.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = QuestionFilter
    search_fields = ["text"]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return QuestionReadOnlySerializer

        return QuestionSerializer


class QuestionChoiceViewSet(ModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = QuestionChoice.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = QuestionChoiceFilter
    search_fields = ["choice"]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return QuestionChoiceReadOnlySerializer

        return QuestionChoiceSerializer


class SurveyResponseViewSet(ModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = SurveyResponse.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = SurveyResponseFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return SurveyResponseReadOnlySerializer

        return SurveyResponseSerializer


class QuestionAnswerViewSet(ModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = QuestionAnswer.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = QuestionAnswerFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return QuestionAnswerReadOnlySerializer

        return QuestionAnswerSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['current_user'] = self.request.user

        return context


class ConditionalBlockingViewSet(ModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = ConditionalBlocking.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = ConditionalBlockingFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return ConditionalBlockingReadOnlySerializer

        return ConditionalBlockingSerializer


class GetNextQuestion(APIView):
    def get(self, request, previous_question_id, *args, **kwargs):
        respondent = request.user
        previous_question = get_object_or_404(Question, pk=previous_question_id)
        current_survey = previous_question.section.survey

        respondent_previous_choice_answers = (QuestionChoice.
                                              objects.
                                              filter(answers__question_answer__survey_response__survey=current_survey,
                                                     answers__question_answer__survey_response__respondent=respondent))

        questions = (Question.objects.filter(section__survey=current_survey)
                     .exclude(blocked_questions__choice__in=respondent_previous_choice_answers).order_by("order"))

        next_question = questions.filter(order__gt=previous_question.order).first()

        if not next_question:
            return Response(data={"result": "No more questions."})

        return Response(data=QuestionReadOnlySerializer(instance=next_question).data)

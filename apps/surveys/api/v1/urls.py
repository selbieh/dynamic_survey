from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.surveys.api.v1.views import (SurveyViewSet, SectionViewSet, QuestionViewSet, QuestionChoiceViewSet,
                                       SurveyResponseViewSet, QuestionAnswerViewSet, ConditionalBlockingViewSet,
                                       GetNextQuestion)

router = DefaultRouter()

router.register(prefix="survey", viewset=SurveyViewSet, basename="survey-api")
router.register(prefix="section", viewset=SectionViewSet, basename="section-api")
router.register(prefix="question", viewset=QuestionViewSet, basename="question-api")
router.register(prefix="question-choice", viewset=QuestionChoiceViewSet, basename="question-choice-api")
router.register(prefix="survey-response", viewset=SurveyResponseViewSet, basename="survey-response-api")
router.register(prefix="question-answer", viewset=QuestionAnswerViewSet, basename="question-answer-api")
router.register(prefix="conditional-block", viewset=ConditionalBlockingViewSet, basename="conditional-blocking-api")

urlpatterns = [
    path("", include(router.urls)),
    path("next-question/<int:previous_question_id>/", GetNextQuestion.as_view()),
]

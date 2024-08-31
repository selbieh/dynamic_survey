from celery import shared_task
from django.shortcuts import get_object_or_404
from apps.surveys.models import SurveyResponse, QuestionChoice, Question


@shared_task()
def check_and_update_survey_response_status(survey_response_id):
    survey_response = get_object_or_404(SurveyResponse, pk=survey_response_id)
    survey = survey_response.survey
    respondent = survey_response.respondent

    respondent_choice_answers = (QuestionChoice.objects.
                                 filter(answers__question_answer__survey_response__survey=survey,
                                        answers__question_answer__survey_response__respondent=respondent))

    survey_questions = Question.objects.filter(section__survey=survey)

    questions = survey_questions.exclude(blocked_questions__choice__in=respondent_choice_answers)

    survey_response_completed = True
    for question in questions:
        if not question.respondent_answers.exists():
            survey_response_completed = False
            break

    if survey_response_completed != survey_response.is_completed:
        survey_response.is_completed = survey_response_completed
        survey_response.save()

    return

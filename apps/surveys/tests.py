from django.contrib.auth.models import Group
from django.core.management import call_command
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from apps.surveys.models import Question, QuestionChoice, Section, Survey, SurveyResponse,ConditionalBlocking


class QuestionAPIViewTestCase(APITestCase):
    def setUp(self):
        call_command("create_groups")
        # Create a user and get access token
        self.admin_group = Group.objects.get(name="Admin")
        self.respondent_group = Group.objects.get(name="Respondent")
        self.admin = User.objects.create_user(email='testadmin@example.com', password='testpass')
        self.admin.groups.add(self.admin_group)
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass')
        self.user.groups.add(self.respondent_group)
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

        # Create survey, section, and questions
        self.survey = Survey.objects.create(name="Survey", start_date="2024-08-30", created_by=self.admin)
        self.section = Section.objects.create(name="Section", survey=self.survey)
        self.question1 = Question.objects.create(
            text="Question #1",
            order=1,
            type="checkbox",
            section=self.section
        )
        self.question2 = Question.objects.create(
            text="Question #2",
            order=2,
            type="number",
            section=self.section
        )
        self.question3 = Question.objects.create(
            text="Question #3",
            order=3,
            type="checkbox",
            section=self.section
        )

        # Create question choices
        self.question1_choiceA = QuestionChoice.objects.create(
            choice="Choice A",
            question=self.question1
        )
        self.question1_choiceB = QuestionChoice.objects.create(
            choice="Choice B",
            question=self.question1
        )

        # Block Question #2 if the respondent chose Choice B in Question #1
        self.conditional_blocking = ConditionalBlocking.objects.create(
            choice=self.question1_choiceB,
            question=self.question2
        )

        # Create Survey response
        self.survey_response = SurveyResponse.objects.create(
            survey=self.survey,
            respondent=self.user
        )

    def get_auth_headers(self):
        return {
            'Authorization': f'Bearer {self.access_token}'
        }

    def choose_choice_in_question1(self, choice_id):
        url = f'/api/v1/question-answer/'
        data = {
            "question": self.question1.id,
            "survey_response": self.survey_response.id,
            "question_choices": [choice_id]
        }
        response = self.client.post(path=url, data=data, headers=self.get_auth_headers())

        return response

    def test_get_next_question_with_conditional_blocking(self):
        post_response = self.choose_choice_in_question1(choice_id=self.question1_choiceB.id)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)

        url = f'/api/v1/next-question/{self.question1.id}/'
        get_response = self.client.get(path=url, headers=self.get_auth_headers())

        self.assertEqual(get_response.data.get("id"), self.question3.id)

    def test_get_next_question_without_conditional_blocking(self):
        post_response = self.choose_choice_in_question1(choice_id=self.question1_choiceA.id)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)

        url = f'/api/v1/next-question/{self.question1.id}/'
        get_response = self.client.get(path=url, headers=self.get_auth_headers())

        self.assertEqual(get_response.data.get("id"), self.question2.id)

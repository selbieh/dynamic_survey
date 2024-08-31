from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth.models import Group


class CustomRegisterSerializer(RegisterSerializer):
    def save(self, request):
        user = super().save(request=request)

        respondent_group = Group.objects.filter(name="Respondent").first()
        if respondent_group:
            user.groups.add(respondent_group)

        return user

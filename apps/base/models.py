from django.db import models


class CustomBaseModel(models.Model):
    """
        TimeStampedModel

        An abstract base class model that provides self-managed "created at" and
        "modified at" fields.
        """

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

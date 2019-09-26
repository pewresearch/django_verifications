from django.db import models

from django_verifications.models import VerifiedModel


class MovieReview(VerifiedModel):

    text = models.TextField()

    class Meta(object):
        fields_to_verify = ["text"]
        verification_filters = [{"text__regex": "action"}]

    def get_verification_metadata(self):

        return {"test": "test", "text": self.text}

from django.db import models

from django_queries.models import QueryModel


class MovieReview(QueryModel):

    text = models.TextField()

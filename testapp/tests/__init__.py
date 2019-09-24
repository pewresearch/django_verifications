from __future__ import print_function

import os

from django.test import TestCase as DjangoTestCase
from django.core.management import call_command
from django.conf import settings

from pewtils import is_not_null
from testapp.models import MovieReview


class BaseTests(DjangoTestCase):

    """
    To test, navigate to django_verifications root folder and run `python manage.py test testapp.tests`
    """

    def setUp(self):

        import pandas as pd

        reviews = pd.read_csv(
            os.path.join(settings.BASE_DIR, "testapp", "test_data.csv")
        )
        for index, row in reviews[:50].iterrows():
            if is_not_null(row["text"]):
                obj = MovieReview.objects.create(text=row["text"][:200], id=index)

    def test(self):

        pass

    def tearDown(self):

        pass

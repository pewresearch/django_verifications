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

        from django_verifications.models import Verification
        from django_verifications.exceptions import VerifiedFieldLock
        from testapp.models import MovieReview
        from django.contrib.auth import get_user_model

        model_name = Verification.objects.available_model_names()[0]
        model_name = model_name.replace(" ", "_")
        self.assertEqual(model_name, "movie_review")

        for query, value in [
            ("flagged_for_verification", 5),
            ("has_unexamined_fields", 5),
            ("any_field_incorrect", 0),
            ("all_fields_good_or_corrected", 0),
        ]:
            count = getattr(Verification.objects, query)(model_name).count()
            self.assertEqual(count, value)
            count = getattr(MovieReview.objects, query)().count()
            self.assertEqual(count, value)

        user = get_user_model().objects.create_user(
            username="testuser", password="12345"
        )

        for obj in MovieReview.objects.flagged_for_verification():
            for field in MovieReview._meta.fields_to_verify:
                v = Verification.objects.create_or_update(
                    {"user": user, "field": field, "content_object": obj},
                    {"is_good": False, "corrected": False},
                )

        for query, value in [
            ("flagged_for_verification", 5),
            ("has_unexamined_fields", 0),
            ("any_field_incorrect", 5),
            ("all_fields_good_or_corrected", 0),
        ]:
            count = getattr(Verification.objects, query)(model_name).count()
            self.assertEqual(count, value)
            count = getattr(MovieReview.objects, query)().count()
            self.assertEqual(count, value)

        for obj in MovieReview.objects.flagged_for_verification():
            for field in MovieReview._meta.fields_to_verify:
                v = Verification.objects.create_or_update(
                    {"user": user, "field": field, "content_object": obj},
                    {"is_good": True, "corrected": True},
                )

        for query, value in [
            ("flagged_for_verification", 5),
            ("has_unexamined_fields", 0),
            ("any_field_incorrect", 0),
            ("all_fields_good_or_corrected", 5),
        ]:
            count = getattr(Verification.objects, query)(model_name).count()
            self.assertEqual(count, value)
            count = getattr(MovieReview.objects, query)().count()
            self.assertEqual(count, value)

        obj.text = "NEW TEXT"
        self.assertRaises(VerifiedFieldLock, obj.save)

    def tearDown(self):

        pass

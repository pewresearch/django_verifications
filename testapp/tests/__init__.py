from __future__ import print_function

import os

from django.test import TestCase as DjangoTestCase
from django.test import RequestFactory, Client
from django.core.management import call_command
from django.conf import settings
from django.contrib.auth.models import User

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

        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="test", email="test@test.com")
        self.user.set_password("test")
        self.user.save()
        self.client = Client()
        self.client.login(username="test", password="test")

    def test_functions(self):

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

    def test_views(self):

        from django.urls import reverse
        from django_verifications.models import Verification

        pk = Verification.objects.has_unexamined_fields("movie_review")[0].pk
        for view, method, args, data, tests in [
            (
                "django_verifications:home",
                "get",
                [],
                {},
                [
                    (lambda x: x["verification_models"][0]["name"], "movie review"),
                    (
                        lambda x: x["verification_models"][0][
                            "flagged_for_verification"
                        ],
                        5,
                    ),
                    (lambda x: x["verification_models"][0]["unexamined"], 5),
                    (lambda x: x["verification_models"][0]["need_correction"], 0),
                    (lambda x: x["verification_models"][0]["finished"], 0),
                    (
                        lambda x: Verification.objects.flagged_for_verification(
                            "movie_review"
                        ).count(),
                        5,
                    ),
                    (
                        lambda x: Verification.objects.has_unexamined_fields(
                            "movie_review"
                        ).count(),
                        5,
                    ),
                    (
                        lambda x: Verification.objects.any_field_incorrect(
                            "movie_review"
                        ).count(),
                        0,
                    ),
                    (
                        lambda x: Verification.objects.all_fields_good_or_corrected(
                            "movie_review"
                        ).count(),
                        0,
                    ),
                ],
            ),
            (
                "django_verifications:verify",
                "get",
                ["movie_review", pk],
                {},
                [
                    (lambda x: x["fields_to_verify"][0][0], "text"),
                    (lambda x: x["fields_to_verify"][0][1][:10], ' " knock o'),
                    (lambda x: x["num_remaining"], 5),
                    (lambda x: x["verification_metadata"]["test"], "test"),
                    (
                        lambda x: Verification.objects.flagged_for_verification(
                            "movie_review"
                        ).count(),
                        5,
                    ),
                    (
                        lambda x: Verification.objects.has_unexamined_fields(
                            "movie_review"
                        ).count(),
                        5,
                    ),
                    (
                        lambda x: Verification.objects.any_field_incorrect(
                            "movie_review"
                        ).count(),
                        0,
                    ),
                    (
                        lambda x: Verification.objects.all_fields_good_or_corrected(
                            "movie_review"
                        ).count(),
                        0,
                    ),
                ],
            ),
            (
                "django_verifications:verify",
                "post",
                ["movie_review", pk],
                {"pk": pk, "text": False},
                [
                    (lambda x: x["num_remaining"], 4),
                    (
                        lambda x: Verification.objects.flagged_for_verification(
                            "movie_review"
                        ).count(),
                        5,
                    ),
                    (
                        lambda x: Verification.objects.has_unexamined_fields(
                            "movie_review"
                        ).count(),
                        4,
                    ),
                    (
                        lambda x: Verification.objects.any_field_incorrect(
                            "movie_review"
                        ).count(),
                        1,
                    ),
                    (
                        lambda x: Verification.objects.all_fields_good_or_corrected(
                            "movie_review"
                        ).count(),
                        0,
                    ),
                ],
            ),
            (
                "django_verifications:correct",
                "get",
                ["movie_review", pk],
                {},
                [
                    (lambda x: x["widget"]["name"], "text"),
                    (lambda x: x["widget"]["required"], True),
                    (lambda x: x["num_remaining"], 1),
                    (lambda x: x["verification_metadata"]["test"], "test"),
                    (lambda x: x["verification_metadata"]["text"][:10], ' " knock o'),
                    (
                        lambda x: Verification.objects.flagged_for_verification(
                            "movie_review"
                        ).count(),
                        5,
                    ),
                    (
                        lambda x: Verification.objects.has_unexamined_fields(
                            "movie_review"
                        ).count(),
                        4,
                    ),
                    (
                        lambda x: Verification.objects.any_field_incorrect(
                            "movie_review"
                        ).count(),
                        1,
                    ),
                    (
                        lambda x: Verification.objects.all_fields_good_or_corrected(
                            "movie_review"
                        ).count(),
                        0,
                    ),
                ],
            ),
            (
                "django_verifications:correct",
                "post",
                ["movie_review", pk],
                {"pk": pk, "text": "test action"},
                [
                    (lambda x: x["num_remaining"], 0),
                    (lambda x: x["verification_metadata"]["test"], "test"),
                    (lambda x: x["verification_metadata"]["text"], "test action"),
                    (
                        lambda x: Verification.objects.flagged_for_verification(
                            "movie_review"
                        ).count(),
                        5,
                    ),
                    (
                        lambda x: Verification.objects.has_unexamined_fields(
                            "movie_review"
                        ).count(),
                        4,
                    ),
                    (
                        lambda x: Verification.objects.any_field_incorrect(
                            "movie_review"
                        ).count(),
                        0,
                    ),
                    (
                        lambda x: Verification.objects.all_fields_good_or_corrected(
                            "movie_review"
                        ).count(),
                        1,
                    ),
                ],
            ),
            (
                "django_verifications:set_as_incorrect",
                "get",
                ["movie_review", pk, "text"],
                {},
                [
                    (
                        lambda x: Verification.objects.flagged_for_verification(
                            "movie_review"
                        ).count(),
                        5,
                    ),
                    (
                        lambda x: Verification.objects.has_unexamined_fields(
                            "movie_review"
                        ).count(),
                        4,
                    ),
                    (
                        lambda x: Verification.objects.any_field_incorrect(
                            "movie_review"
                        ).count(),
                        1,
                    ),
                    (
                        lambda x: Verification.objects.all_fields_good_or_corrected(
                            "movie_review"
                        ).count(),
                        0,
                    ),
                ],
            ),
        ]:
            response = getattr(self.client, method)(reverse(view, args=args), data=data)
            self.assertEqual(response.status_code, 200)
            for func, value in tests:
                self.assertEqual(func(response.context), value)

    def tearDown(self):

        pass

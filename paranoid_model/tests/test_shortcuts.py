from django.http import Http404
from django.test import TestCase
from model_bakery import baker

from paranoid_model.shortcuts import get_object_or_404
from paranoid_model.tests import models


class TestGetObjectOr404(TestCase):
    def test_raise_when_object_does_not_exists(self):
        with self.assertRaises(Http404):
            get_object_or_404(
                models.Person.objects,
                id=None
            )

    def test_raise_when_object_is_soft_deleted(self):
        person = baker.make(models.Person)
        person.delete()

        with self.assertRaises(Http404):
            get_object_or_404(
                models.Person.objects,
                id=person.id
            )

    def test_returns_the_object_when_object_exists(self):
        person = baker.make(models.Person)

        found = get_object_or_404(models.Person.objects, id=person.id)
        self.assertEqual(person, found)

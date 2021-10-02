from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
import django.shortcuts
from django.test import TestCase
from model_bakery import baker

from paranoid_model.exceptions import SoftDeleted
from paranoid_model.tests.models import Person


class TestSoftDeletedExceptions(TestCase):
    def test_soft_delete_is_sub_class_of_does_not_exists_exception(self):
        soft_deleted_exception = Person.SoftDeleted

        self.assertTrue(issubclass(soft_deleted_exception, SoftDeleted))
        self.assertTrue(issubclass(soft_deleted_exception, Person.DoesNotExist))
        self.assertTrue(issubclass(soft_deleted_exception, ObjectDoesNotExist))

    def test_keep_compatibility_with_django_does_not_exist_exception(self):
        person = baker.make(Person)
        person.delete(hard_delete=False)

        with self.assertRaises(Http404):
            django.shortcuts.get_object_or_404(Person, id=person.id)

        with self.assertRaises(Person.SoftDeleted):
            Person.objects.get(id=person.id)

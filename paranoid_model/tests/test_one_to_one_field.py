from django.test import TestCase
from paranoid_model.tests.models import Car
from model_bakery import baker


class RelatedModelTest(TestCase):
    """Test model with relationship ManyToMany, ForeignKey, OneToOne"""

    def setUp(self):
        car = baker.make(Car)
        self.car = car
        self.person = car.owner

    def test_create(self):
        """Test create a model with OneToOneField"""
        Car.objects.get()
        self.assertTrue(Car.objects.filter(owner=self.person).exists())

    def test_delete(self):
        """Test delete model with OneToOneField"""
        self.person.delete()
        self.assertFalse(Car.objects.all().exists())
        self.assertTrue(Car.objects.filter(with_deleted=True).exists())

        self.assertRaises(Car.SoftDeleted, Car.objects.get)

        self.car.delete(hard_delete=True)
        self.assertFalse(Car.objects.all(with_deleted=True).exists())

    def test_related_object_being_queried_by_default(self):
        """Test if related object is being queried"""
        self.person.delete()
        self.assertFalse(Car.objects.all().exists())
        self.assertEqual(Car.objects.get_deleted().owner, self.person)

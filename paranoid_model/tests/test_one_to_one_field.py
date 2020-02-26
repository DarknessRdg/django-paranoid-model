from django.test import TestCase
from paranoid_model.tests.models import Car, Person
from paranoid_model.tests.utils import get_person_instance


class RelatedModelTest(TestCase):
    """Test model with relatioships ManyToMany, ForeignKey, OneToOne"""

    def setUp(self):
        person = get_person_instance()
        person.save()
        car = Car(owner=person)
        car.save()

    def test_create(self):
        """Test create a model with OneToOneField"""
        Car.objects.get()
        person = Person.objects.get()

        self.assertTrue(Car.objects.filter(owner=person).exists())
    
    def test_delete(self):
        """Test dele model with OneToOneField"""
        person = Person.objects.get()
        car = Car.objects.get()

        person.delete()
        self.assertFalse(Car.objects.all().exists())
        self.assertTrue(Car.objects.filter(with_deleted=True).exists())

        self.assertRaises(Car.SoftDeleted, 
                          lambda: Car.objects.get())
                    
        car.delete(hard_delete=True)
        self.assertFalse(Car.objects.all(with_deleted=True).exists())

    def test_related_object_been_queried_by_default(self):
        """Test if related object is been queried"""
        person = Person.objects.get()
        person.delete()
        self.assertEquals(Car.objects.all().exists(), False)

        self.assertEquals(Car.objects.get_deleted().owner, person)

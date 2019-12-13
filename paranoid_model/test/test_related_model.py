from django.test import TestCase
from paranoid_model.test.models import Person, Phone
from faker import Faker
from paranoid_model.test.utils import (
    any_list, all_list, get_person_instance, create_list_of_person,
    get_phone_instace
)


fake = Faker('en_US')


class RelatedModelTest(TestCase):
    """Test model with relatioships ManyToMany, ForeignKey, OneToOne"""
    
    def setUp(self):
        pass
    
    def test_create(self):
        """Test creation of a related model"""
        person = get_person_instance()
        person.save()
        get_phone_instace(person).save()

        all_phones = person.phones.all()
        self.assertEquals(all_phones.count(), 1)
    
    def test_related_name_queries(self):
        """Test related name query"""
        person = get_person_instance()
        person.save()
        
        phone1 = get_phone_instace(person)
        phone1.save()
        phone2 = get_phone_instace(person)
        phone2.save()

        self.assertEquals(person.phones.all().count(), 2)

        phone1.delete()
        self.assertEquals(person.phones.all().count(), 1)
        self.assertEquals(person.phones.all(with_deleted=True).count(), 2)
        
        phone1.restore()
        person.delete()
        self.assertEquals(person.phones.all().count(), 2)
        self.assertEquals(person.phones.all(with_deleted=True).count(), 2)
        self.assertEquals(person.phones.all(with_deleted=False).count(), 0)
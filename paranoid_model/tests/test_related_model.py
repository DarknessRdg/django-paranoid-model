from django.test import TestCase
from django.utils import timezone

from paranoid_model.tests.models import Person, Phone, Clothes, Address
from model_bakery import baker


class RelatedModelTest(TestCase):
    """Test model with relationships ManyToMany, ForeignKey, OneToOne"""
    databases = '__all__'

    def assertNotRaises(self, function):
        """
        Method to check if a function does not raises an exception
        Args:
            function: callback function name
        """
        try:
            function()
        except Exception as exc:
            self.fail('Raised in a query that was not suposed to! Message: {}'.format(exc))

    def test_create(self):
        """Test creation of a related model"""
        phone = baker.make(Phone)
        person = phone.owner

        all_phones = person.phones.all()
        self.assertEqual(all_phones.count(), 1)

    def test_delete_cascade(self):
        """Test delete with cascade"""
        person = baker.make(Person)

        baker.make(Phone, owner=person)
        person.delete()

        self.assertNotRaises(lambda: person.phones.get_deleted(owner=person))
        phone1 = person.phones.get_deleted(owner=person)

        self.assertTrue(person.is_soft_deleted and phone1.is_soft_deleted)

    def test_if_delete_affects_other_queries(self):
        """Test if all other queries are updated when delete an instance"""
        person = baker.make(Person)
        baker.make(Phone, owner=person, _quantity=3)

        all_phones = person.phones.all()
        all_with_deleted = person.phones.all(with_deleted=True)

        self.assertEqual(all_phones.count(), 3)
        self.assertEqual(all_with_deleted.count(), 3)

        person.delete()
        self.assertEqual(all_phones.count(), 0)

        # cached queries with with_deleted=True should not exclude deleted ones.
        self.assertEqual(all_with_deleted.count(), 3)

    def test_delete_cascade_with_many_objects(self):
        """Test delete cascade with many objects"""
        person = baker.make(Person)
        baker.make(Phone, owner=person, _quantity=5)
        baker.make(Address, owner=person, _quantity=5)

        phones = person.phones.all()
        self.assertEqual(phones.count(), 5)

        person.delete()
        phones = person.phones.all(with_deleted=True)
        phones_without_deleted = phones.all()

        self.assertEqual(phones.count(), 5)
        self.assertEqual(phones_without_deleted.count(), 0)

        addresses = person.addresses.all(with_deleted=True)
        address_without_deleted = addresses.all()

        self.assertEqual(addresses.count(), 5)
        self.assertEqual(address_without_deleted.count(), 0)

    def test_delete_cascade_with_objects_not_paranoid(self):
        """
        Test if when delete a paranoid model, other models
        not paranoid are not deleted
        """
        person = baker.make(Person)
        baker.make(Clothes, person=person)

        person.delete()
        self.assertNotRaises(Clothes.objects.get)

    def test_restore_cascade(self):
        """Test restore cascade"""
        person = baker.make(Person)
        baker.make(Phone, owner=person, _quantity=5)
        baker.make(Address, owner=person, _quantity=5)

        person.delete()

        phones = person.phones.all(with_deleted=False)
        addresses = person.phones.all(with_deleted=False)

        self.assertEqual(phones.count(), 0)
        self.assertEqual(addresses.count(), 0)

        person.restore()
        self.assertEqual(phones.all(with_deleted=False).count(), 5)
        self.assertEqual(addresses.all(with_deleted=False).count(), 5)

    def test_restore_cascade_in_queryset(self):
        """Test restore on cascade in a queryset.restore()"""
        deleted_time = timezone.now()

        amount, amount_phones = 10, 3

        person_list = baker.make(Person, deleted_at=deleted_time, _quantity=amount)
        for person in person_list:
            baker.make(Phone, owner=person, _quantity=amount_phones)

        Person.objects.all(with_deleted=True).restore()
        people = Person.objects.all()
        self.assertEqual(people.count(), amount)

        for person in people:
            self.assertFalse(person.is_soft_deleted)
            self.assertEqual(person.phones.all().count(), amount_phones)

    def test_related_name_queries_all(self):
        """Test related name query .all()"""
        person = baker.make(Person)
        phone1 = baker.make(Phone, owner=person, _quantity=2)[0]

        self.assertEqual(person.phones.all().count(), 2)

        phone1.delete()
        self.assertEqual(person.phones.all().count(), 1)
        self.assertEqual(person.phones.all(with_deleted=True).count(), 2)

        phone1.restore()
        person.delete()
        self.assertEqual(person.phones.all().count(), 2)
        self.assertEqual(person.phones.all(with_deleted=True).count(), 2)
        self.assertEqual(person.phones.all(with_deleted=False).count(), 0)

    def test_related_name_queries_filter(self):
        """Test related name query .filter()"""
        person = baker.make(Person)

        phone1 = baker.make(Phone, owner=person, _quantity=2)[0]

        phone1.delete()
        self.assertEqual(person.phones.filter().count(), 1)
        self.assertEqual(person.phones.filter(with_deleted=True).count(), 2)
        self.assertEqual(person.phones.filter(with_deleted=False).count(), 1)

    def test_get_on_related(self):
        """Test .get() with related_name query"""
        person = baker.make(Person)
        phone1 = baker.make(Phone, owner=person)

        self.assertNotRaises(lambda: person.phones.get(phone=phone1.phone))
        with self.assertRaises(Phone.DoesNotExist):
            person.phones.get(phone=phone1.phone+'0')

        phone1.delete()
        with self.assertRaises(Phone.SoftDeleted):
            person.phones.get(phone=phone1.phone)

        with self.assertRaises(Phone.DoesNotExist):
            person.phones.get(phone=phone1.phone+'0')

    def test_get_deleted(self):
        """Test .get_deleted() with related_name query"""
        person = baker.make(Person)

        phone1, phone2 = baker.make(Phone, owner=person, _quantity=2)

        phone2.delete()

        with self.assertRaises(Phone.IsNotSoftDeleted):
            person.phones.get_deleted(phone=phone1.phone)

        self.assertNotRaises(
            lambda: person.phones.get_deleted(phone=phone2.phone))

        with self.assertRaises(Phone.MultipleObjectsReturned):
            person.phones.get(owner=person)

    def test_get_or_restore(self):
        """Test get_or_restore() related_name query"""
        person = baker.make(Person)
        phone1 = baker.make(Phone, owner=person)

        phone1.delete()
        phones = person.phones
        self.assertFalse(phones.get_or_restore().is_soft_deleted)

        baker.make(Phone, owner=person)
        with self.assertRaises(Phone.MultipleObjectsReturned):
            person.phones.get_or_restore()

        with self.assertRaises(Phone.DoesNotExist):
            person.phones.get_or_restore(phone='a')

    def test_filter_deleted_only(self):
        """Test .deleted_only() with related name queries"""
        person = baker.make(Person)
        phones = baker.make(Phone, owner=person, _quantity=10)

        for phone, counter in zip(phones, range(10)):
            if counter % 2 == 0:
                phone.delete()

        deleted = person.phones.deleted_only()
        self.assertEqual(deleted.count(), 5)

        deleted_zero = person.phones.all().deleted_only()
        self.assertEqual(deleted_zero.count(), 0)

    def test_delete_using(self):
        using = 'db2'

        save_kwargs = {'using': using}
        person = baker.make(Person, _save_kwargs=save_kwargs)
        baker.make(Phone, owner=person, _save_kwargs=save_kwargs)

        person.delete()

        people = Person.objects.using(using).all(with_deleted=True)
        phones = Phone.objects.using(using).all(with_deleted=True)
        self.assertEqual(people.count(), 1)
        self.assertEqual(phones.count(), 1)

        self.assertEqual(phones.all().count(), 0)
        self.assertEqual(people.all().count(), 0)

        self.assertEqual(phones.deleted_only().count(), 1)
        self.assertEqual(people.deleted_only().count(), 1)

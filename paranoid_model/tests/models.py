from django.db import models
from paranoid_model import models as paranoid_model


class Person(paranoid_model.Paranoid):
    """
    Person model with Paranoid inheritance
    Attributes:
         name: CharField
         created_at: DateTimeField
         updated_at: DateTimeField
         deleted_at: DateTimeField
    """
    name = models.CharField(max_length=255)


class Phone(paranoid_model.Paranoid):
    """
    Phone model with Paranoid inheritance
    Attributes:
         phone: CharField
         owner: ForeignKey to Person
         created_at: DateTimeField
         updated_at: DateTimeField
         deleted_at: DateTimeField
    """

    phone = models.CharField(max_length=255)
    owner = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='phones')


class Address(paranoid_model.Paranoid):
    """
    Address model with Paranoid inheritance
    Attributes:
         street: CharField
         owner: ForeignKey to Person
         created_at: DateTimeField
         updated_at: DateTimeField
         deleted_at: DateTimeField
    """
    street = models.CharField(max_length=255)
    owner = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='addresses')


class Car(paranoid_model.Paranoid):
    owner = models.OneToOneField(Person, on_delete=models.CASCADE)


class Clothes(models.Model):
    """
    Person clothes not paranoid model
    Attributes:
        street: CharField
        owner: ForeignKey to Person
        created_at: DateTimeField
        updated_at: DateTimeField
        deleted_at: DateTimeField
    """
    description = models.CharField(max_length=255)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='my_clothes')

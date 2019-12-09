from django.db import models
from paranoid_model import paranoid_model


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

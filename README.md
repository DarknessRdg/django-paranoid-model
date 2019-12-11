# django-paranoid-model
Django abstract model with paranoid behavior, therefore when an instance is deleted it is not really deleted from database, it's applied and mask on the filter so when filter, the result are the "undeleted" instances.

# Get Started
Raw the file paranoid_model.py from app paranoid_model and paste on your local project. 

You can copy from this link:
https://raw.githubusercontent.com/Experluan/django-paranoid-model/master/paranoid_model/paranoid_model.py

File link: https://github.com/Experluan/django-paranoid-model/blob/master/paranoid_model/paranoid_model.py

# Create your Paranoid Model

On your models.py file import Paranoid class from paranoid_moldel.py, then inheritance Paranoid class on your models

```py
from django.db import models
import paranoid_model

class Person(paranoid_model.Paranoid):  # make an inheritance
    # all the default fields come with inheritance:
    # created_at
    # updated_at
    # deleted_at
    name = models.CharField(max_length=255)
```

# Create your Paranoid Model

On your models.py file import Paranoid class from `paranoid_models.models` file, then inheritance Paranoid class on your models

```py
from django.db import models
from paranoid_model.models import Paranoid

class Person(Paranoid):  # make an inheritance
    # all the default fields come with inheritance:
    # created_at
    # updated_at
    # deleted_at
    name = models.CharField(max_length=255)
```

!!! note

    * **created_at** : is the field with creation date
    * **updated_at** : is the field with latest update date
    * **deleted_at** : is the field with deletion date, so when it is None it means it hasn't been deleted

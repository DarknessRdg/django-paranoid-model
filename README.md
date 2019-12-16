# django-paranoid-model
Django abstract model with paranoid behavior, therefore when an instance is deleted it is not really deleted from database, it's applied a mask on the filter so when filter, the result are the "undeleted" instances.

# Get Started
Raw the file paranoid_model.py from app paranoid_model and paste on your local project. 

You can copy from this link:
https://raw.githubusercontent.com/DarknessRdg/django-paranoid-model/master/paranoid_model/paranoid_model.py

File link: https://github.com/DarknessRdg/django-paranoid-model/blob/master/paranoid_model/paranoid_model.py

# Create your Paranoid Model

On your models.py file import Paranoid class from paranoid_models.models file, then inheritance Paranoid class on your models

```py
from django.db import models
import paranoid_model.models 
# from paranoid_models import models DON'T DO THAT!
# it will override ' from django.db import models ' 
# and will get and error to access models.Field() 

class Person(paranoid_model.models.Paranoid):  # make an inheritance
    # all the default fields come with inheritance:
    # created_at
    # updated_at
    # deleted_at
    name = models.CharField(max_length=255)
```

* created_at is the field with creation date
* updated_at is the field with latest update date
* deleted_at is the field with deletion date, so when it is None it means it hasn't been deleted

# Making queries

In short, the queries are the same as django's queries. The difference is that by default behavior all the queries comes with 
not soft deleted.

To make a querry and include the deleted instance just need to give parameter ``with_deleted`` to the querry. This is a boolean parameter, so it can be True or False.

##### Obs: Soft deleted is a instance where the filed ``deleted_at`` is not None


### All()
```py
ParanoidModel.objects.all()  # will return all the instancnes that hasn't been soft deleted
ParanoidModel.objects.all(with_deleted=False)  # this will exclude the soft deleted
ParanoidModel.objects.all(with_deleted=True)  # will include the soft deleted
```

As you can see, ``.all()`` will return the same instances as ``all(with_deleted=False)``

### Filter()
```py
ParanoidModel.objects.filter(**kwargs)  # will return the filtered instancnes that hasn't been soft deleted
ParanoidModel.objects.all(with_deleted=False, **kwargs)  # this will exclude the soft deleted
ParanoidModel.objects.all(with_deleted=True, **kwargs)  # will include the soft deleted
```

As you can see, ``.filter(**kwargs)`` will return the same instances as ``filter(with_deleted=False, **kwargs)``


### Get()
```py
ParanoidModel.objects.get(**kwargs)  
# will retrun a single instance of the object that matches with the querry
```

Careful with get() method, because it can raise some errors.
The possible raises are: 
* **model.DoesNotExist**: will be raised if the querry doesn't match to any instance
* **model.SoftDeleted**: will be raised if the instance has been soft deleted.

You can do the following:
```py
try:
    ParanoidModel.objects.get(pk=10)
except ParanoidModel.DoesNotExist:
    # The querry didn't find any instance with pk = 10
    pass
```
or
```py
try:
    ParanoidModel.objects.get(pk=10)
except ParanoidModel.SoftDeleted:
    # The querry found an instance, but it has been soft deleted
    # it means you need to querry with method get_deleted() or get_or_restore()
    pass
```

But, if you pay attention it doesn't allow you to get an instance that has been soft deleted. Don't worry, no need to cry! :sob: ``get_deleted`` and ``get_or_restore`` will save you!

### Get_deleted()
```py
ParanoidModel.objects.get_deleted(**kwargs)  
# will retrun a single instance of the object that matches with the querry
```

Careful with get_deleted() method, because it can raise some errors.
The possible raises are: 
* **model.DoesNotExist**: will be raised if the querry doesn't match to any instance
* **model.IsNotSoftDeleted**: will be raised if the instance has not been soft deleted yet.

You can do the following:
```py
try:
    ParanoidModel.objects.get_deleted(pk=10)
except ParanoidModel.DoesNotExist:
    # The querry didn't find any instance with pk = 10
    pass
```
or
```py
try:
    ParanoidModel.objects.get_deleted(pk=10)
except ParanoidModel.IsNotSoftDeleted:
    # The querry found an instance, but it has not been soft deleted yet
    # it means you need to querry with method get()
    pass
```

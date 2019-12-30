# django-paranoid-model
Django abstract model with paranoid behavior, therefore when an instance is deleted it is not really deleted from database, it's applied a mask on the filter so when filter, the result are the "undeleted" instances.

## Summary

1) [Get Started](https://github.com/DarknessRdg/django-paranoid-model/blob/master/docs/02_get_started.md)
2) [Create you paranoid model](https://github.com/DarknessRdg/django-paranoid-model/blob/master/docs/03_create_your_paranoid_model.md)
3) [Instance Manipulate](https://github.com/DarknessRdg/django-paranoid-model/blob/master/docs/04_instance_manipulate.md)
4) [Making queries](https://github.com/DarknessRdg/django-paranoid-model/blob/master/docs/04_instance_manipulate.md)
5) [Admin](https://github.com/DarknessRdg/django-paranoid-model/blob/master/docs/06_django_admin.md)

---

# Get Started

```
pip install django-paranoid-model
```

Add paranoid to your INSTALLED_APPS

```py
INSTALLED_APPS = [
    ...
    'paranoid_model'
]
```

---

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

---

# Instance Manipulate

ParanoidModel has some some differences on default Django methods.

### Save()

This method has no difference, it work just like Django's

```py
my_paranoid_instance = Paranoid()
my_paranoid_instance.save()
```

### Delete()

The **most important** method. This is why pararanoid model exists. When ``delete()`` an instance it should not be really deleted from database, but hide from user. 

The magic is in the attribute ``deleted_at``. When there is no date (deleted_at is None) it means it has not been deleted, but if has a date it means it has been deleted. So when we call delete(), it will set up the current date to delete_at field and save the instance, instead of deleted.  

**The delete works on *CASCADE*. So all the related objects will be soft deleted**

```py
instance = ParanoidModel.objects.create()
instance.delete()  # instance has the current date on the field deleted_at but it still saved on database 
instance.deleted_at is None
>> False

# but remember that this delete will do the same to every related instances like:
person = Person.objects.create(name='My Name')
for i in range(5):
    Phone.objects.create(phone='123456789', owner=person)

person.delete()  # this will soft delete person
# but will also delete all the 5 phones related to this person
```

### Delete(hard_delete=True)

If you really wants to delete the instance from databse you can use parameter ``hard_delete``. It calls Django's default method

```py
instance = ParanoidModel.objects.create()
intance.delete()  # will soft delete
instance.delete(hard_delete=True)  # will call django delete, so will delete from database
```

Be careful using ``hard_delete``

### is_soft_deletd

This is a @property that returns a boolean if current instance has been soft deleted or not. Otherwise, it returns if attribute deleted_at is None. It is just a more easy way to check if deleted_at is None instead of use this whole sentence to check.

So you can just do the following:

```py
instance = ParanoidModel.objects.create()

instance.is_soft_deleted
>> False

instance.delete()
instance.is_soft_deleted
>> True

# real example
person = Person.objects.create(name='My name')
person.delete()

if person.is_soft_deleted:
    person.restore()
```

### Restore()

Once an instance has been soft deleted, it can be easily undeleted with method restore()

```py
instance = ParanoidModel.objects.create()

instance.delete()
instance.is_soft_deleted
>> True

instance.restore()
instance.is_soft_deleted
>> False
```

---

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

As you can see, ``.all()`` will return the same instances that ``all(with_deleted=False)``

**Obs on related_name queries:** when an instance has been soft deleted, the related_querry ``all()`` will return ``with_deleted=True`` by default, because if the instance has been soft deleted, I guess, it want's to be querried the deleted objects, BUT you can alway pass the parameter ``with_deleted`` and it will work as you wish.

It's something like this:
```py
person = Person.objects.create(name='person')
for i in range(20):
    phone = Phone.objects.create(phone='123', owner=person)
    if i % 2 == 0:
        phone.delete()

person.phones.all()  # will return all not soft deleted

person.delete()  # will delete all the phones that belongs to person

# since person has been deleted, a related_name querry will work a little different
person.phones.all()  # will return all and include the soft deleted
person.phones.all(with_deleted=True)  # will return all and include soft deleted
person.phones.all(with_deleted=False)  # will return all not soft deleted
```
The explanation why Paranoid Query does it, is because imagine we have a *person* and we have *2 phones related to that person*, and that *person has been soft deleted*, and by cascade person's phones also soft deleted.

Now imagine that in the future, that person wants a report of your datas once saved in database, so when we filter his data, we will need, also, his data deleted.

That is why paranoid query will include soft deleted when querring related_name with a soft delete instance.

### Filter()
```py
ParanoidModel.objects.filter(**kwargs)  # will return the filtered instancnes that hasn't been soft deleted
ParanoidModel.objects.filter(with_deleted=False, **kwargs)  # this will exclude the soft deleted
ParanoidModel.objects.filter(with_deleted=True, **kwargs)  # will include the soft deleted
```

As you can see, ``.filter(**kwargs)`` will return the same instances that ``filter(with_deleted=False, **kwargs)``

### Deleted_only()

To filter only deleted you must use ``deleted_only`` filter. Thats because ``filter`` override querry parameter ``deleted_at`` and change it.

```py
for i in range(20):
    instance = ParanoidModel.objects.create()
    
    if i % 2 == 0:
        instance.delete()

ParanoidModel.objects.deleted_only()  # only soft deleted_instance

# DON'T DO THAT
# 
# ParanoidModel.objects.filter(deleted_at__isnull=True)
# this param 'deleted_at__isnull' is overwritten by querry filter
# that's because every param wich starts with 'deleted_at' are removed
```

### Get()
```py
ParanoidModel.objects.get(**kwargs)  
# will retrun a single instance of the object that matches with the querry
```

Careful with get() method, because it can raise some errors.
The possible raises are: 
* **model.DoesNotExist**: (Django) will be raised if the querry doesn't match to any instance
* **model.MultipleObjectsReturned**: (Django) will be raised if more than 1 instances matches with the querry
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
* **model.DoesNotExist**: (Django) will be raised if the querry doesn't match to any instance
* **model.MultipleObjectsReturned**: (Django) will be raised if more than 1 instances matches with the querry
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
### Get_or_restore()
This method will work just like Django's wiht a thiny difference, it will restore the instance if it has been soft deleted

```py
ParanoidModel.objects.get_or_restore(pk=10)
```

Like all get method, it can raises some exceptions:
* **model.DoesNotExist**: (Django) will be raised if the querry doesn't match to any instance
* **model.MultipleObjectsReturned**: (Django) will be raised if more than 1 instances matches with the querry

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
    ParanoidModel.objects.get_deleted(name__icontains='a')
except ParanoidModel.MultipleObjectsReturned:
    # The querry found more than 1 instance
    pass
```

### Restore()
This method restore all the instances soft deleted int the current querry set. Look at the example bellow

```py
for i in range(20):
    ParanoidModel.objects.create()

ParanoidModel.objects.all().count() == 0
>> True

ParanoidModel.objects.all(with_deleted=True).restore()

ParanoidModel.objects.all().count() == 0:
>> False
ParanoidModel.objects.all().count() == 20:
>> True
```

---

# Django Admin

### Register your models

To register your model on django admin, is recomended to let ParanoidAdmin handle with admin action. Otherwise you may have
some trouble.

ParanoidAdmin also include some aditional methods to look more "paranoid" on admin page, some functions are:
  * Delete: soft delete instance
  * Permanently delete: hard delete
  * Restore: remode deleted_at date
  * Filter: filter all, only deleted, not deleted

On you  ``admin.py`` register you models like the example below:

```py
# admin.py

from paranoid_model.admin import ParanoidAdmin
from .models import MyModel

admin.site.register(MyModel, ParanoidAdmin)
```

This will allow ParanoidAdmin to handle with admin actions.

Once done that, it should looks something like this:
<img src="https://github.com/DarknessRdg/django-paranoid-model/blob/master/docs/images/admin/default.png">

### Customize list

You can customize the way objects are displayed changing the attribute ``list_display`` on admin. To do that, you're gonna
have to make an inheritance of ParanoidAdmin and change this attribute.


```py
# admin.py

from paranoid_model.admin import ParanoidAdmin
from .models import MyModel


class MyAdmin(ParanoidAdmin):
    list_display = ('__str__',)  # Django's Default display when list


admin.site.register(MyModel, MyAdmin)
```

This is how it will look like:
<img src="https://github.com/DarknessRdg/django-paranoid-model/blob/master/docs/images/admin/change_list_display.png">

If you like the Paranoid's default list display but just want to add some more attributes, you can do the following:

```py
class MyAdmin(ParanoidAdmin):
    list_display = ('name', 'phone',) + ParanoidAdmin.list_display
```

[Checkout Official Docs here](https://docs.djangoproject.com/en/3.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_display)


### Customize filter

You can customize filter window as you want like remove, add more filter.

**Add more filter:**

```py
# admin.py

from paranoid_model.admin import ParanoidAdmin
from .models import MyModel


class MyFilter(ParanoidAdminFilter):

    def lookups(self, request, mode_admin):
        # Method to get tuple with all (`search_param`, `name to show`) 
        # to list on filter window
        
        return super().lookups(request, mode_admin) + (
            ('additional', 'Additional filter'),  # add aditional filters to super() filter
        )
    
    def queryset(self, request, queryset):
        # Method to handle the querrying and return the QuerySet[]
        # to be showed on site
        
        if self.value() == 'additional':
            # filter additional objects
            pass
        else:
            # Not one of our additionals querry
            return super().queryset(request, queryset)



class MyAdmin(ParanoidAdmin):
    list_filter = (MyFilter,)  # Use our list filter created just above


admin.site.register(MyModel, MyAdmin)
```

Look at the result:
<img src="https://github.com/DarknessRdg/django-paranoid-model/blob/master/docs/images/admin/additional_filter.png">

[Checkout Official Docs here](https://docs.djangoproject.com/en/3.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter)

**Remove filter window:**

Remove filter window is a peace of cake

```py
# admin.py

from paranoid_model.admin import ParanoidAdmin
from .models import MyModel


class MyAdmin(ParanoidAdmin):
    list_filter = ()  # set list_filter with 0 filter inside


admin.site.register(MyModel, MyAdmin)
```

And if you also set ``list_display`` to be Django's default it will be just like Django's default model page.

```py
# admin.py

from paranoid_model.admin import ParanoidAdmin
from .models import MyModel


class MyAdmin(ParanoidAdmin):
    list_display = ('__str__',)  # list like django
    list_filter = ()  # remove filter window


admin.site.register(MyModel, MyAdmin)
```

Django's default view:
<img src="https://github.com/DarknessRdg/django-paranoid-model/blob/master/docs/images/admin/default_django.png">


---


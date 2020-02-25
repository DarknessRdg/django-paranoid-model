# Making queries

In short, the queries are the same as django's queries. The difference is that by default behavior all soft deleted instances are excluded.

To make a querry and include the deleted instance just need to give parameter `with_deleted` to the querry. This is a boolean parameter, so it can be True or False.

!!! info

    Soft deleted is an instance where the filed ``deleted_at`` is not None

### All

```py
ParanoidModel.objects.all()
# returns all the instancnes that hasn't been soft deleted
```

```py
ParanoidModel.objects.all(with_deleted=False)
# this will exclude the soft deleted
```

```py
ParanoidModel.objects.all(with_deleted=True)
# will include the soft deleted
```

As you can see, `:::py .all()` will return the same instances that `:::py all(with_deleted=False)`

??? note "On related_name queries"
    When an instance has been soft deleted, the related_querry `:::py all()` will return
    `:::py with_deleted=True` by default.
    
    That happens ecause if the instance has been soft deleted it want's to be querried the deleted objects,
    BUT you can alway use the parameter `:::py with_deleted=False` and it all soft deleted are excluded.

    It's something like this:

    ```py
    person = Person.objects.create(name='person')
    for i in range(20):
        phone = Phone.objects.create(phone='123', owner=person)
        if i % 2 == 0:
            phone.delete()

    person.phones.all()  # will return all not soft deleted

    person.delete()  # will delete all the phones that belongs to person

    # since person has been deleted,
    # a related_name querry will work a little different

    person.phones.all()
    # will return all and include the soft deleted

    person.phones.all(with_deleted=True)
    # will return all and include soft deleted

    person.phones.all(with_deleted=False)
    # will return all not soft deleted
    ```

    ??? quote "Why paranoid does it"
        The explanation why Paranoid Query does it, is because imagine we have a *person* and we have *2 phones related to that person*, and that *person has been soft deleted*, and by cascade person's phones also soft deleted.

        Now imagine that in the future, that person wants a report of your datas once saved in database, so when we filter his data, we will need, also, his data deleted.

        That is why paranoid query will include soft deleted when querring related_name with a soft delete instance.

### Filter

```py
ParanoidModel.objects.filter(**kwargs)
# Will return the filtered instancnes that has not been soft deleted
```

```py
ParanoidModel.objects.filter(with_deleted=False, **kwargs)
# Will exclude the soft deleted
```

```py
ParanoidModel.objects.filter(with_deleted=True, **kwargs)
#  Will include the soft deleted
```

!!! note "On related_name queries"

    It works just like `.all()` querry.

    [chekcou here](#all)

As you can see, `:::py .filter(**kwargs)` will return the same instances that `:::py filter(with_deleted=False, **kwargs)`

### Deleted_only

To filter only deleted you must use `deleted_only` filter. Thats because `filter` override querry parameter `deleted_at` and change it.

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

!!! failure

    **Do not do that**

    ```py
    ParanoidModel.objects.filter(deleted_at__isnull=True)
    ```

    The param `deleted_at__isnull` is overwritten by querry filter.

    That happens because every param wich starts with `deleted_at` are removed

### Get

```py
ParanoidModel.objects.get(**kwargs)
# will retrun a single instance of the object that matches with the querry
```

Careful with get() method, because it can raise some errors.
The possible raises are:

- **model.DoesNotExist**: (Django) will be raised if the querry doesn't match to any instance

- **model.MultipleObjectsReturned**: (Django) will be raised if more than 1 instances matches with the querry

- **model.SoftDeleted**: will be raised if the instance has been soft deleted.

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

But, if you pay attention it doesn't allow you to get an instance that has been soft deleted. Don't worry, no need to cry! :sob: `get_deleted` and `get_or_restore` will save you!

### Get_deleted

```py
ParanoidModel.objects.get_deleted(**kwargs)
# will retrun a single instance of the object that matches with the querry
```

Careful with get_deleted() method, because it can raise some errors.
The possible raises are:

- **model.DoesNotExist**: (Django) will be raised if the querry doesn't match to any instance

- **model.MultipleObjectsReturned**: (Django) will be raised if more than 1 instances matches with the querry

- **model.IsNotSoftDeleted**: will be raised if the instance has not been soft deleted yet.

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

### Get_or_restore

This method will work just like Django's wiht a thiny difference, it will restore the instance if it has been soft deleted

```py
ParanoidModel.objects.get_or_restore(pk=10)
```

Like all get method, it can raises some exceptions:

- **model.DoesNotExist**: (Django) will be raised if the querry doesn't match to any instance

- **model.MultipleObjectsReturned**: (Django) will be raised if more than 1 instances matches with the querry

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

### Restore

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

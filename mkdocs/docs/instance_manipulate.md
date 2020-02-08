# Instance Manipulate

ParanoidModel has some some differences on default Django methods.

### Save

This method has no difference, it work just like Django's

```py
my_paranoid_instance = Paranoid()
my_paranoid_instance.save()
```

### Delete

The **most important** method. This is why pararanoid model exists. When ``delete()`` an instance it should not be really deleted from database, but hide from user. 

The magic is in the attribute ``deleted_at``. When there is no date (deleted_at is None) it means it has not been deleted, but if has a date it means it has been deleted. So when we call delete(), it will set up the current date to delete_at field and save the instance, instead of deleted.  

!!! warning
    The delete works on **CASCADE** . That means all related objects are going to be soft deleted as well

```py
instance = ParanoidModel.objects.create()
instance.delete()  # instance has the current 
# date on the field deleted_at but it still saved on database 
instance.deleted_at is None
>> False

# but remember that this delete will do the same to every related instances like:
person = Person.objects.create(name='My Name')
for i in range(5):
    Phone.objects.create(phone='123456789', owner=person)

person.delete()  # this will soft delete person
# but will also delete all the 5 phones related to this person
```


### delete(hard_delete=True)

You can also delete datas from database.

If you really wants to delete the instance from databse you can use parameter ``hard_delete``. It calls Django's default method

```py
instance = ParanoidModel.objects.create()
intance.delete()  # will soft delete
instance.delete(hard_delete=True)  # will call django delete, 
# so it will be deleted from database
```

!!! danger
    Be careful using ``hard_delete`` .
    
    If `hard_delete` is True, it will call Django's default delete method, so instance will be deleted from database.

### is_soft_deletd

This is a @property that returns a boolean if current instance has been soft deleted or not. Otherwise, it returns if attribute deleted_at is None. 
It is just a more easy way to check if deleted_at is None instead of use this whole sentence to check.

So you can just do the following:

```py
instance = ParanoidModel.objects.create()

instance.is_soft_deleted
>> False

instance.delete()
instance.is_soft_deleted
>> True
```

This property is useful it in a code like this:

```py
myself = Person.objects.all(with_deleted=True, name='My name').first()

if myself.is_soft_deleted:
    person.restore()
```

### Restore

Once an instance has been soft deleted, it can be easily undeleted with method `restore()`

```py
instance = ParanoidModel.objects.create()

instance.delete()
instance.is_soft_deleted
>> True

instance.restore()
instance.is_soft_deleted
>> False
```
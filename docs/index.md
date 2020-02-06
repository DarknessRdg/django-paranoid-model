# django-paranoid-model
Django abstract model with paranoid behavior, therefore when an instance is deleted it is not really deleted from database, it's applied a mask on the filter so when filter, the result are the "undeleted" instances.

This package is useful when you want to keep all datas saved on your database and when user wants do delete, it is just hidden form user.

It include some helpers fields to your model:

* created_at
* updated_at
* deleted_at

## Quick start

Install Django Paranoid Model package from pip

```py
pip install django-paranoid-model
```

Add paranoid_model to your installed apps so you can use django admin with a paranoid behavior

```py
INSTALLED_APPS = [
    ...
    'paranoid_model'
]
```

Good job ! You're now ready to use it.

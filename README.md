<p align="center">
    <a
        href="https://travis-ci.org/jeromelefeuvre/django-paranoid-model">
        <img
            src="https://travis-ci.org/jeromelefeuvre/django-paranoid-model.svg?branch=master"
            alt="Build Status" />
    </a>
    <a href="/LICENSE.md">
        <img
            src="https://img.shields.io/github/license/jeromelefeuvre/django-paranoid-model.svg"
            alt="License" />
    </a>
    <a href="https://github.com/jeromelefeuvre/django-paranoid-model/issues">
        <img
            src="https://img.shields.io/github/issues/jeromelefeuvre/django-paranoid-model?color=0088ff"
            alt="Issues" />
    </a>
    <a href="https://github.com/jeromelefeuvre/django-paranoid-model/pulls">
        <img
            src="https://img.shields.io/github/issues-pr/jeromelefeuvre/django-paranoid-model?color=0088ff"
            alt="Open pull requests" />
    </a>
</p>

<!-- **Read the docs: <https://jeromelefeuvre.github.io/django-paranoid-model/>** -->

# django-paranoid-model

Django abstract model with paranoid behavior, therefore when an instance is deleted it is not really deleted from database, it's applied a mask on the filter so when filter, the result are the "undeleted" instances.

Sometimes you might want to keep all datas saved on your database and when user wants do delete, it is just hidden form user.

All documentation are in the `mkdocs/docs` directory and online at [HERE !!](https://jeromelefeuvre.github.io/django-paranoid-model/). If you're new here, we recomend you to checkout the documentation first :wink: .

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


Run tests
---------
```
  pip install -e .[test]
  pytest
```
or run Tox to test on multiple Django versions
```
  pip install tox
  tox
```

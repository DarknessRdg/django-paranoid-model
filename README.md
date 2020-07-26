<p align="center">
    <a 
        href="https://travis-ci.org/DarknessRdg/django-paranoid-model">
        <img
            src="https://travis-ci.org/DarknessRdg/django-paranoid-model.svg?branch=master"
            alt="Build Status" />
    </a>
    <a href="https://app.codacy.com/manual/DarknessRdg/django-paranoid-model?utm_source=github.com&utm_medium=referral&utm_content=DarknessRdg/django-paranoid-model&utm_campaign=Badge_Grade_Dashboard">
        <img
            src="https://api.codacy.com/project/badge/Grade/bd361ce3dc054deb83e8d1255cb1b895" 
            alt="Code quality" />
    </a>
    <a href="https://www.codacy.com/manual/DarknessRdg/django-paranoid-model?utm_source=github.com&utm_medium=referral&utm_content=DarknessRdg/django-paranoid-model&utm_campaign=Badge_Coverage">
        <img
            src="https://api.codacy.com/project/badge/Coverage/5b00ace127fb409fb2eb6e5468066d2f"
            alt="Coverage" />
    </a>
    <a href="/LICENSE.md">
        <img
            src="https://img.shields.io/github/license/DarknessRdg/django-paranoid-model.svg" 
            alt="License" />
    </a>
    <a href="https://github.com/DarknessRdg/django-paranoid-model/issues">
        <img
            src="https://img.shields.io/github/issues/darknessrdg/django-paranoid-model?color=0088ff"
            alt="Issues" />
    </a>
    <a href="https://github.com/DarknessRdg/django-paranoid-model/pulls">
        <img
            src="https://img.shields.io/github/issues-pr/darknessrdg/django-paranoid-model?color=0088ff" 
            alt="Open pull requests" />
    </a>
</p>

<p align="center">
    <a 
        href="https://pypi.org/project/django-paranoid-model/"
        alt="PiPy downloads">
        <img src="https://img.shields.io/pypi/dm/django-paranoid-model?color=informational" />
    </a>
    <a 
        href="https://pypi.org/project/django-paranoid-model/"
        alt="PiPy version">
        <img src="https://img.shields.io/pypi/v/django-paranoid-model" />
    </a>
    <a 
        href="https://pypi.org/project/django-paranoid-model/"
        alt="PiPy status">
        <img src="https://img.shields.io/pypi/status/django-paranoid-model?color=important" />
    </a>
</p>

**Read the docs: <https://darknessrdg.github.io/django-paranoid-model/>**

# django-paranoid-model

Django abstract model with paranoid behavior, therefore when an instance is deleted it is not really deleted from database, it's applied a mask on the filter so when filter, the result are the "undeleted" instances.

Sometimes you might want to keep all datas saved on your database and when user wants do delete, it is just hidden form user.

All documentation are in the `mkdocs/docs` directory and online at [HERE !!](https://darknessrdg.github.io/django-paranoid-model/). If you're new here, we recomend you to checkout the documentation first :wink: .

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

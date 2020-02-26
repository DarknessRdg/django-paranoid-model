[![Build Status](https://travis-ci.org/DarknessRdg/django-paranoid-model.svg?branch=master)](https://travis-ci.org/DarknessRdg/django-paranoid-model)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/bd361ce3dc054deb83e8d1255cb1b895)](https://app.codacy.com/manual/DarknessRdg/django-paranoid-model?utm_source=github.com&utm_medium=referral&utm_content=DarknessRdg/django-paranoid-model&utm_campaign=Badge_Grade_Dashboard)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/5b00ace127fb409fb2eb6e5468066d2f)](https://www.codacy.com/manual/DarknessRdg/django-paranoid-model?utm_source=github.com&utm_medium=referral&utm_content=DarknessRdg/django-paranoid-model&utm_campaign=Badge_Coverage)
[![license](https://img.shields.io/github/license/DarknessRdg/django-paranoid-model.svg)](LICENSE.md)

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

import django.shortcuts

from paranoid_model import exceptions


def get_object_or_404(klass, *args, **kwargs):
    try:
        return django.shortcuts.get_object_or_404(klass, *args, **kwargs)
    except exceptions.SoftDeleted:
        raise django.shortcuts.Http404()

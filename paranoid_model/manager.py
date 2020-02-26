"""
File with Manager used on Paranoid Model
"""


from django.db import models
from paranoid_model.queryset import ParanoidQuerySet


class ParanoidManager(models.Manager):
    """Paranoid Manager with a Paranoid behavior"""

    _queryset_class = ParanoidQuerySet

    def get_queryset(self):
        return self._queryset_class(self.model, using=self._db)

    def all(self, **kwargs):
        """
        Intercept Django's query all() and use Paranoid Queryset method all()
        Args:
            with_deleted: bool to check if also wants to filter soft deleted instances
        Returns:
            ParanoidQuerySet[]
        """
        try:
            with_deleted = kwargs['with_deleted']
        except KeyError:
            with_deleted = False

        try:
            # When Manager has a instace, is need to check if
            # the isnstance has been soft delete. Because in case
            # that instace has been soft delete, the query must be
            # with deleted and if user has not passad a with_deleted param
            if self.instance.is_soft_deleted and 'with_deleted' not in kwargs.keys():
                with_deleted = True
        except AttributeError:
            pass
        qs = self.get_queryset()
        return qs.all(with_deleted=with_deleted)

    def filter(self, with_deleted=False, *args, **kwargs):
        """
        Intercept firts method ``objects.filter()``.
        This is because a querry from related_name doesn't call this
        method, in that case it can be treated on queryset.filter and know
        when is a related_name query or an objects query.

        Args:
            with_deleted: bool to check if filter soft deleted or not. Default {False}
        Returns:
            ParanoidQuerySet[]
        """
        qs = self.get_queryset()
        return qs.filter(with_deleted=with_deleted, *args, **kwargs)

    def deleted_only(self):
        """
        Method to filter only deleted instances
        Return:
            ParanoidQuerySet[]
        """

        qs = self.get_queryset()
        return qs.deleted_only()

    def get_deleted(self, *arg, **kwargs):
        """
        Method to get an instance that has not been soft deleted yet.
        Args:
             *args: passed to Django's get
             **kwargs: passed to Django's get
        Returns:
            Object: instance of object not soft deleted and not hard deleted
        Raise:
            model.DoesNotExist: object not found on database
            paranoid_model.IsNotSoftDeleted: object has not been soft deleted yet
            model.MultipleObjectsReturned: if filtered more than 1 instance
        """
        return self.get_queryset().get_deleted(*arg, **kwargs)

    def get_or_restore(self, *args, **kwargs):
        """
        Method to get a instance, and if has been soft deleted it will be restored
        Args:
             *args: passed to Django's get
             **kwargs: passed to Django's get
        Returns:
            Object: instance of object not soft deleted
        Raise:
            model.DoesNotExist: object not found on database
            model.MultipleObjectsReturned: if filtered more than 1 instance
        """

        return self.get_queryset().get_or_restore(*args, **kwargs)

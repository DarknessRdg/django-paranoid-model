"""
File with QuerySet used on Paranoid Model
"""


from django.db import models
from paranoid_model.exceptions import SoftDeleted, IsNotSoftDeleted
import paranoid_model.models


class ParanoidQuerySet(models.query.QuerySet):
    """
    QuerySet for a Paranoid Model with field ``deleted_at`` as a mask
    """

    def get(self, *args, **kwargs):
        """
        Override default behavior of Django's get() to apply a custom validation
        Args:
             *args: passed to Django's get
             **kwargs: passed to Django's get
        Returns:
            Object, instance of object not soft deleted or not hard deleted
        Raise:
            model.DoesNotExist: object not found on database
            paranoid_model.SoftDeleted: object has been soft deleted
            model.MultipleObjectsReturned: if filtered more than 1 instance
        """
        objeto = super(ParanoidQuerySet, self).get(*args, **kwargs)

        if objeto.is_soft_deleted:
            raise SoftDeleted(
                "Object %s has been soft deleted. Try use get_deleted() or get_or_restore()." %
                self.model._meta.object_name)

        return objeto

    def get_deleted(self, *arg, **kwargs):
        """
        Method to get a instance that has not been soft deleted yet.
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
        kwargs['deleted_at__isnull'] = False
        objeto = super(ParanoidQuerySet, self).get(*arg, **kwargs)

        if not objeto.is_soft_deleted:
            raise IsNotSoftDeleted(
                "Object %s has not been soft deleted yet. Try get()" %
                self.model._meta.object_name)

        return objeto

    def get_or_restore(self, *args, **kwargs):
        """
        Method to get an instance, and if has been soft deleted it will be restored
        Args:
             *args: passed to Django's get
             **kwargs: passed to Django's get
        Returns:
            Object: instance of object not soft deleted
        Raise:
            model.DoesNotExist: (Django) object not found on database
            model.MultipleObjectsReturned: (Django) more than 1 instances with matches querry
        """

        objeto = super(ParanoidQuerySet, self).get(*args, **kwargs)
        using = kwargs.pop('using', None)
        if objeto.is_soft_deleted:
            objeto.restore(using)
        return objeto

    def all(self, with_deleted=False):
        """"
        Override default behavior of Django's all() to filter only not soft deleted or
        include the soft deleted.
        Args:
            with_deleted: bool to check if filter soft deleted or not. Default {False}
        Returns:
            ParanoidQuerySet[]
        """
        return self.filter(with_deleted=with_deleted)

    def filter(self, *args, **kwargs):
        """
        Override default behavior of Django's filter() to filter not sotf deleted or include
        instaces that has been soft_deleted.

        ``with_deleted`` has a default True because some Django's features call directly
        this method, like a ManyToMant field with related name, and in that case we want
        to have the default behavior and not be on Django's way. So we assume that
        every paranoid method that calls this filter() will pass a with_deleted and so
        work as user expects.

        It is also assumed that a ParanoidQueryset[] has already filtered the instances
        soft deleted according to the param whith_delted and the nested filter() wont need
        to check again, and filter without deleted, like ``objects.filter().filter().filter()``.
        Onlty the firts filter will need to have ``with_deleted`` param, like:
        ``objects.filter(with_deleted=False).filter().filter()``

        Args:
            **kwargs: extra options:
                with_deleted: bool to check if filter soft deleted or not. Default {True}.
        Returns:
            ParanoidQuerySet[]
        """
        args_copy = args

        if not isinstance(kwargs.get('with_deleted', True), bool):
            args_copy += (kwargs['with_deleted'],)

        with_deleted = kwargs.pop('with_deleted', True)  # default True
        for key in kwargs.keys():
            if key.startswith('deleted_at'):
                kwargs.pop(key)
                break

            # when related names are used django first query if a filter
            # filtering the objects related and after that django filter
            # with user's filter.
            # When Django filter a object soft deleted, with_deledt should
            # be True.
            elif isinstance(kwargs[key], paranoid_model.models.Paranoid) and not with_deleted:
                if kwargs[key].is_soft_deleted:
                    with_deleted = True

        if not with_deleted:
            kwargs['deleted_at__isnull'] = True
        return super(ParanoidQuerySet, self).filter(*args_copy, **kwargs)

    def delete(self, hard_delete=False, using=None):
        """
        Delet instances from current QuerySet
        Args:
            hard_delete: bool to check if apply soft delete or django's delete
        Returns:
            int(): amount deleted
        """

        if not hard_delete:
            cont = 0
            for instance in self:
                instance.delete(using=using)
                cont += 1
            # Clear the result cache, in case this QuerySet gets reused.
            self._result_cache = None
            return cont
        else:
            return super(ParanoidQuerySet, self).delete()

    def restore(self, using=None):
        """
        Restore instances from current QuerySet
        Returns:
            int(): amount restored
        """

        cont = 0
        for instance in self:
            if instance.is_soft_deleted:
                instance.restore(using)
                cont += 1
        # Clear the result cache, in case this QuerySet gets reused.
        self._result_cache = None
        return cont

    def deleted_only(self):
        """
        Filter only deleted instances
        Returns:
            ParanoidQuerySet[]
        """
        return self.exclude(deleted_at__isnull=True)

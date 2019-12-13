from django.contrib.admin.utils import NestedObjects
from django.db import models, router
from django.utils import timezone


class SoftDeleted(Exception):
    """Object has been soft deleted."""
    pass


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
        """
        objeto = super(ParanoidQuerySet, self).get(*args, **kwargs)

        if objeto.is_soft_deleted:
            raise SoftDeleted(
                "%s matching query does not exist." %
                self.model._meta.object_name)

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

    def filter(self, with_deleted=True, *args, **kwargs):
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
            with_deleted: bool to check if filter soft deleted or not. Default {True}.
        Returns:
            ParanoidQuerySet[]
        """

        for key in kwargs.keys():
            if key.startswith('deleted_at'):
                kwargs.pop(key)
                break

            # when related names are used django first query if a filter
            # filtering the objects related and after that django filter
            # with user's filter.
            # When Django filter a object soft deleted, with_deledt should
            # be True.
            elif isinstance(kwargs[key], models.Model) and not with_deleted:
                if kwargs[key].is_soft_deleted:
                    with_deleted = True
        
        if not with_deleted:
            kwargs['deleted_at__isnull'] = True
        return super(ParanoidQuerySet, self).filter(*args, **kwargs)

    def delete(self, hard_delete=False):
        """
        Delet instances from current QuerySet
        Args:
            hard_delete: bool to check if apply soft delete or django's delete
        Returns:
            int(): amount deleted
        """

        if not hard_delete:
            cont = 1
            for instance in self:
                instance.delete()
                cont += 1
            # Clear the result cache, in case this QuerySet gets reused.
            self._result_cache = None
            return cont
        else:
            return len(super(ParanoidQuerySet, self).delete())


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


class Paranoid(models.Model):
    """
    Abstract model with a Paranoid behavior, therefore once deleted
    the instance is just hide from the users: Soft Delete.
    Attributes:
        created_at: DateTimeField
        updated_at: DateTimeField
        deleted_at: DateTimeField
    Properties:
        is_soft_deleted: bool
    """
    objects = ParanoidManager()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        abstract = True

    @property
    def is_soft_deleted(self):
        """
        Property to check is current instance has been soft deleted
        Returns:
            bool: if instance has been soft deleted
        """
        return self.deleted_at is not None

    def delete(self, using=None, keep_parents=False, hard_delete=False):
        """
        Override default delete method so Soft Delete can be made.
        If delete is hard_delete, the soft delete is ignored and the
        instance is deleted from the database
        Args:
            using: default None
            keep_parents: default False
            hard_delete: boolean default False
        """
        if not hard_delete:
            self.deleted_at = timezone.now()
            self.save()

            for instance in self._related_objects():
                instance.delete()
        else:
            super(Paranoid, self).delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """
        Restore an instance once deleted and instance's related objects
        """
        self.deleted_at = None
        self.save()

        for related in self._related_objects():
            if 'deleted_at' in related.__dict__.keys():
                related.deleted_at = None
                related.save()

    def _related_objects(self):
        """
        Method to get all objects with foreign key the relation with self instance
        Args:
            self
        Returns:
            List(): all related objects
        """
        collector = NestedObjects(using=router.db_for_write(self))
        collector.collect([self])

        def parse_list(obj):
            """
            Parse to nested objects
            Args:
                obj: list instance or models object instance
            Returns:
                list(): list with objects
            """
            if isinstance(obj, list):
                array = []
                for item in obj:
                    array += parse_list(item)
                return array
            return [obj]

        colletion = parse_list(collector.nested())
        colletion.remove(self)

        return colletion

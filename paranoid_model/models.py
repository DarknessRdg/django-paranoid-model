"""
File with a based Paranoid model
"""


from django.db import models, router
from django.utils import timezone
from django.contrib.admin.utils import NestedObjects
from paranoid_model.exceptions import SoftDeleted, IsNotSoftDeleted
from paranoid_model.manager import ParanoidManager


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
    SoftDeleted = SoftDeleted
    IsNotSoftDeleted = IsNotSoftDeleted
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
            self.save(using=using)

            for instance in self._related_objects(using):
                if isinstance(instance, Paranoid):
                    instance.delete(using=using)
        else:
            super(Paranoid, self).delete(using=using, keep_parents=keep_parents)

    def restore(self, using=None):
        """
        Restore an instance once deleted and instance's related objects
        """
        self.deleted_at = None
        self.save(using=using)

        for related in self._related_objects(using):
            if 'deleted_at' in related.__dict__.keys():
                related.deleted_at = None
                related.save(using=using)

    def _related_objects(self, using):
        """
        Method to get all objects with foreign key the relation with self instance
        Args:
            self
        Returns:
            List(): all related objects
        """
        using = using or router.db_for_write(self.__class__, instance=self)

        collector = NestedObjects(using=using)
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

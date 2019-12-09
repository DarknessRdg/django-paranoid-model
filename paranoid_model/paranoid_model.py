from django.contrib.admin.utils import NestedObjects
from django.db import models, router
from django.utils import timezone


class SoftDeleted(Exception):
    """O Objeto foi deletado atrvés de um Soft Delete"""
    pass


class ParanoidQuerySet(models.query.QuerySet):
    """
    QuerySet de um model que funciona como Paranoid, onde campo deletado
    tem como nome: ``deleted_at``
    """

    def get(self, *args, **kwargs):
        """
        Sobrescreve comportamendo padrão do mteodo get
        Args:
             *args
             **kwargs
        Returns:
            Object, instancia de um objeto com a query passada e que
            nao foi deletado
        Raise:
            model.DoesNotExist se objeto nao for encontrado
            paranoid_model.SoftDeleted se objeto tiver sido deletado
        """
        objeto = super(ParanoidQuerySet, self).get(*args, **kwargs)

        if objeto.deleted_at is None:
            raise SoftDeleted(
                "%s matching query does not exist." %
                self.model._meta.object_name)

        return objeto

    def all(self, with_deleted=False):
        """"
        Sobrescreve comportamento padrão do metodo all para selecionar todos as instancias
        que nao sofreram soft delete ou inclui-las
        Args:
            with_deleted: boolean default, verifica se é pra selecionar os deletados também
        Returns:
            ParanoidQuerySet
        """
        return self.filter(with_deleted=with_deleted)

    def filter(self, with_deleted=False, *args, **kwargs):
        """
        Sobrescreve comportamento padrão do metodo de filter para selecionar somente as intancias
         que nao sofreram soft delete ou inclui-las
        Args:
            with_deleted: boolean default, verifica se é pra selecionar os deletados também
        Returns:
            ParanoidQuerySet
        """

        for key in kwargs.keys():
            if key.startswith('deleted_at'):
                kwargs.pop(key)

        if not with_deleted:
            kwargs['deleted_at__isnull'] = True
        return super(ParanoidQuerySet, self).filter(*args, **kwargs)

    def delete(self, hard_delete=False):
        """
        Deleta as instancias da QuerySet atual.
        Args:
            hard_delete: boolean default False, verifica se deseja deletar para sempre a instancia
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
    """Manager para model com comportamento Paranoid (que usa um soft delete)"""

    _queryset_class = ParanoidQuerySet

    def get_queryset(self):
        return self._queryset_class(self.model, using=self._db)

    def all(self, with_deleted=False, **kwargs):
        qs = self.get_queryset()
        return qs.all(with_deleted=with_deleted)


class Paranoid(models.Model):
    """
    Abstract model with a Paranoid behavior, therefore once deleted
    the instance is just hide from the users: Soft Delete.
    Attributes:
        created_at: DateTimeField
        updated_at: DateTimeField
        deleted_at: DateTimeField
    """
    objects = ParanoidManager()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        abstract = True

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
        Metodo para pegar as instancias dos objectos que tem relacao de chave estrangeira com
        a instancia atual
        Args:
            self

        Returns:
            List() com todas os objetos relacionados
        """
        collector = NestedObjects(using=router.db_for_write(self))
        collector.collect([self])

        def parse_list(obj):
            if isinstance(obj, list):
                array = []
                for item in obj:
                    array += parse_list(item)
                return array
            return [obj]

        colletion = parse_list(collector.nested())
        colletion.remove(self)

        return colletion

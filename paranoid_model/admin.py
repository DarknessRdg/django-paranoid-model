from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from paranoid_model.exceptions import SoftDeleted
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.admin.actions import delete_selected


class ParanoidAdminFilter(admin.SimpleListFilter):
    """Class to handle filter on site"""
    title = _('soft deleted')
    parameter_name = 'deleted_at'

    def lookups(self, request, model_admin):
        """
        Method with (value, option) for filter form
        on admin view
        """

        return (
            ('not soft', _('Not soft deleted')),
            ('soft', _('Soft deleted')),
        )

    def queryset(self, request, queryset):
        """
        Method to get query set with instances to
        show on site
        """

        with_deleted = False  # exclude deleted if not querrying all

        value = self.value()

        if value is None or value == 'all':
            with_deleted = True
        elif value == 'soft':
            return queryset.deleted_only()

        return queryset.all(with_deleted=with_deleted)


class ParanoidAdmin(admin.ModelAdmin):
    """
    Paranoid base Admin
    """

    change_form_template = 'admin/paranoid_model/change_form.html'

    readonly_fields = ('deleted_at',)
    list_display = ('pk', '__str__', 'created_at', 'updated_at', 'is_not_deleted')
    list_display_links = ('pk', '__str__',)
    list_filter = (ParanoidAdminFilter,)
    actions = ['restore_selected', 'permanently_delete']

    def is_not_deleted(self, obj):
        """
        is not deleted table column on admin list view
        """
        return not obj.is_soft_deleted
    is_not_deleted.boolean = True

    def response_change(self, request, obj):
        """
        Intercept default submit method on change_form view to perform
        custom options
        Args:
            request
            obj: instance
        """

        if '_restore' in request.POST:
            obj.restore()

            level, message = messages.SUCCESS, f'{obj.__str__()} restored.'
            log_message = 'Restored'
            messages.add_message(request, level, message)
        else:
            return super().response_change(request, obj)

        super().log_addition(request, obj, log_message)
        return HttpResponseRedirect('.')

    def delete_view(self, request, object_id, extra_context=None):
        """
        Override default delete_view method to add 'Soft deleted'
        to log history
        """

        _return = super().delete_view(request, object_id, extra_context=None)
        if request.POST:
            try:
                obj = self.model.objects.get(pk=object_id)
            except SoftDeleted:
                obj = self.model.objects.get_deleted(pk=object_id)

            hard_delete = 'hard_delete' in request.GET.keys()
            obj.delete(hard_delete=hard_delete)

            report = 'Permanently deleted.' if hard_delete else 'Soft deleted.'

            super().log_addition(request, obj, report)

        return _return

    def restore_selected(self, request, queryset):
        """
        Action method to restore every instance selected
        """
        count = queryset.restore()
        messages.add_message(request, messages.INFO, f'{count} restored.')

    def permanently_delete(self, request, queryset):
        """
        Action method to hard delete every instance selected
        """
        self.hard_delete = True
        return delete_selected(self, request, queryset)

    def delete_queryset(self, request, queryset):
        """
        Delete a queryset
        """
        queryset.delete(hard_delete=self.hard_delete)
        self.hard_delete = False
    hard_delete = False  # boolean for 'permanently delete' action
    # use django delete confirmation is pretty hard, so instaead of create
    # our own, it is easier to have a boolean variable to check if permanently or not.
    # Django's 'delete_selected' uses delete_queryset() to delete.

    def get_object(self, request, object_id, from_field=None):
        """
        Return instance whit matching parameter, overwitten to work
        without errors with ParanoidQuerySet if instance has been soft deleted
        """

        queryset = super().get_queryset(request)
        model = queryset.model
        field = model._meta.pk if from_field is None else model._meta.get_field(from_field)
        try:
            object_id = field.to_python(object_id)
            return queryset.get(**{field.name: object_id})
        except (model.DoesNotExist, ValidationError, ValueError):
            return None
        except SoftDeleted:
            return queryset.get_deleted(**{field.name: object_id})

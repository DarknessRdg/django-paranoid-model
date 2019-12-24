from django.contrib import admin
from django.http import HttpResponseRedirect
from paranoid_model.exceptions import SoftDeleted
from django.core.exceptions import ValidationError
from django.contrib import messages


class ParanoidAdminFilter(admin.SimpleListFilter):
    """Class to handle filter on site"""
    title = ('soft deleted')
    parameter_name = 'deleted_at'
    
    def lookups(self, request, mode_admin):
        """
        Method with (value, option) for filter form
        on admin view
        """

        return (
            ('not soft', ('Not soft deleted')),
            ('soft', ('Soft deleted')),
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

    list_display= ('pk', 'created_at', 'updated_at', 'is_not_deleted')
    list_filter = (ParanoidAdminFilter,)
    actions = ['restore_selected', 'delete_permanently']
    
    def is_not_deleted(self, obj):
        """
        is not deleted table column on admin list view
        """
        return not obj.is_soft_deleted
    is_not_deleted.boolean = True

    def response_change(self, request, obj):
        """
        Intecept default submit method on change_form view to performe
        custom options
        Args:
            request
            obj: instance
        """
        redirect_url = '.'
        level, message, log_message = messages.INFO, '', ''

        if '_hard-delete' in request.POST:
            obj.delete(hard_delete=True)            
            level, message = messages.SUCCESS, f'{obj.__str__()} hard deleted.'
            log_message = 'Deleted permanently.'

            path = request.path.split('/')
            redirect_url = '/'.join(path[:len(path) - 3])
        
        elif '_restore' in request.POST:
            obj.restore()

            level, message = messages.SUCCESS, f'{obj.__str__()} restored.'
            log_message = 'Restored'
        
        else:
            return super().response_change(request, obj)
    
        messages.add_message(request, level, message)
        super().log_addition(request, obj, log_message)

        return HttpResponseRedirect(redirect_url)
    
    def delete_view(self, request, object_id, extra_context=None):
        """
        Override default delete_view method to add 'Soft deleted'
        to log history
        """
        _return = super().delete_view(request, object_id, extra_context=None)
        
        try:
            obj = self.model.objects.get(pk=object_id)
        except SoftDeleted:  
            obj = self.model.objects.get_deleted(pk=object_id)
        super().log_addition(request, obj, 'Soft deleted.')
        return _return
    
    def restore_selected(self, request, queryset):
        """
        Action method to restore every instance selected
        """
        count = queryset.restore()
        messages.add_message(request, messages.INFO, f'{count} restored.')
    
    def delete_permanently(self, request, queryset):
        """
        Action method to hard delete every instance selected
        """
        count = queryset.delete(hard_delete=True)
        messages.add_message(request, messages.INFO, f'{count} soft deleted.')

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

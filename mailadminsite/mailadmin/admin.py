# -*- coding: utf-8 -*-
from django.contrib import admin
from mailadmin import models
from django.core.exceptions import PermissionDenied

class VirtualDomainsAdmin(admin.ModelAdmin):
    filter_horizontal = ('admin', )
admin.site.register(models.VirtualDomains, VirtualDomainsAdmin)

class VirtualThingAdmin(admin.ModelAdmin):
    def _has_domain_access(self, request, obj):
        if obj == None:
            return True
        if request.user.is_superuser:
            return True
        return obj.domain.admin.filter(id=request.user.id).count() > 0

    def has_change_permission(self, request, obj=None):
        if not super(VirtualThingAdmin, self).has_change_permission(request, obj):
            return False
        return self._has_domain_access(request, obj)

    def has_delete_permission(self, request, obj=None):
        if not super(VirtualThingAdmin, self).has_delete_permission(request, obj):
            return False
        return self._has_domain_access(request, obj)
    
    def save_model(self, request, obj, form, change):
        if not self._has_domain_access(request, obj):
            raise PermissionDenied()
        super(VirtualThingAdmin, self).save_model(request, obj, form, change)
    
    def queryset(self, request):
        qs = super(VirtualThingAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            tablename = self.model._meta.db_table
            return qs.extra(
                where=[tablename+'.domain_id in (select virtualdomains_id from virtual_domain_admins where user_id = %s)'],
                params=[request.user.id]
            )

class VirtualUsersAdmin(VirtualThingAdmin):
    list_display = ('domain', '__unicode__')
    list_display_links = ('__unicode__', )
    list_filter = ('domain', )
    ordering = ('domain', 'user')
admin.site.register(models.VirtualUsers, VirtualUsersAdmin)

class VirtualAliasesAdmin(VirtualThingAdmin):
    list_display = ('domain', 'full_source', 'destination')
    list_display_links = ('full_source', )
    list_filter = ('domain', )
    ordering = ('domain', 'source')
admin.site.register(models.VirtualAliases, VirtualAliasesAdmin)

admin.site.index_template = 'admin/mailadmin/index.html'

# disable mass delete action as it bypasses per-domain right checks
admin.site.disable_action('delete_selected')

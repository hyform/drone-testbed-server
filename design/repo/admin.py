from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile, DesignTeam, Address, Customer, Warehouse, Vehicle, Plan, Scenario, DataLog, ExperOrg

# Register your models here.

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_display = ('username', 'is_staff', 'get_team')
    list_select_related = ('profile', )

    def get_team(self, instance):
        return instance.profile.team
    get_team.short_description = 'team'    

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'x', 'z',)
    ordering = ('id', )

class CustomerAdmin(admin.ModelAdmin):
    # inlines = [AddressInline]
    list_display = ('id', 'payload', 'weight', 'market_id', 'address')
    ordering = ('id', )

    def get_x(self, instance):
        return instance.address.x
    get_x.short_description = 'x'

    def get_z(self, instance):
        return instance.address.z
    get_z.short_description = 'z'

    admin_select_related = ('address', )

    fieldsets = [
        (None,      {'fields': ['market', 'payload', 'weight']}),
        ('Address', {'fields': ['address']}),
    ]

class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'session')
    ordering = ('id',)

class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'config', 'result', 'range', 'velocity', 'cost', 'payload', 'group_id', 'session_id')
    ordering = ('id',)

class PlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'scenario_id', 'group_id', 'session_id')
    ordering = ('id',)

class ScenarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'warehouse_id', 'group_id', 'session_id', 'version')
    ordering = ('id',)

class DataLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'time', 'action', 'session_id', 'type')
    ordering = ('id',)    

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(DesignTeam)
admin.site.register(Address, AddressAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Warehouse, WarehouseAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(Scenario, ScenarioAdmin)
admin.site.register(DataLog, DataLogAdmin)
admin.site.register(ExperOrg)

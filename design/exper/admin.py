from django.contrib import admin
from .models import Structure, Role, Position, Group, GroupPosition, Study, Experiment, Market, Session, SessionTeam, UserPosition, Organization

# Register your models here.

class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'structure', 'role')

class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'structure')

class GroupPositionAdmin(admin.ModelAdmin):
    list_display = ('group', 'position', 'primary')

class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'experiment', 'status')

class SessionTeamAdmin(admin.ModelAdmin):
    list_display = ('session', 'team')

class UserPositionAdmin(admin.ModelAdmin):
    list_display = ('user', 'position')

admin.site.register(Structure)
admin.site.register(Role)
admin.site.register(Position, PositionAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(GroupPosition, GroupPositionAdmin)
admin.site.register(Study)
admin.site.register(Experiment)
admin.site.register(Market)
admin.site.register(Session, SessionAdmin)
admin.site.register(SessionTeam, SessionTeamAdmin)
admin.site.register(UserPosition, UserPositionAdmin)
admin.site.register(Organization)

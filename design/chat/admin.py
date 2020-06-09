from django.contrib import admin
from .models import Channel, ChannelPosition
from repo.models import DesignTeam

# Register your models here.

class PositionInline(admin.StackedInline):
    model = ChannelPosition
    fk_name = 'channel'
    extra = 2

class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'structure')    
    fieldsets = [
        (None,      {'fields': ['name','structure']}),
    ]
    inlines = [PositionInline]


admin.site.register(Channel, ChannelAdmin)


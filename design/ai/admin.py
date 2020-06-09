from django.contrib import admin
from .models import Designer1

# Register your models here.

class Designer1Admin(admin.ModelAdmin):
    pass

admin.site.register(Designer1, Designer1Admin)

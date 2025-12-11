# bug_app/admin.py
from django.contrib import admin
from .models import Programmer, Error, BugFix

class ProgrammerAdmin(admin.ModelAdmin):
    list_display = ('surname', 'first_name', 'phone')
    search_fields = ('surname',)

class ErrorAdmin(admin.ModelAdmin):
    list_display = ('pk', 'error_description', 'error_level', 'source', 'date_received')
    list_filter = ('error_level', 'source', 'category')
    search_fields = ('error_description',)

class BugFixAdmin(admin.ModelAdmin):
    list_display = ('id', 'error', 'programmer', 'duration_days', 'cost_per_day', 'total_cost')
    raw_id_fields = ('error', 'programmer')

admin.site.register(Programmer, ProgrammerAdmin)
admin.site.register(Error, ErrorAdmin)
admin.site.register(BugFix, BugFixAdmin)
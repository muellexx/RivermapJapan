from django.contrib import admin
from .models import Profile, ClientIP


class ClientIPAdmin(admin.ModelAdmin):
    list_display = ('ip', 'count', 'date_visited', 'user', 'admin')
    ordering = ['-date_visited']


admin.site.register(Profile)
admin.site.register(ClientIP, ClientIPAdmin)

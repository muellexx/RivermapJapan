from django.contrib import admin
from .models import River


class RivermapAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')


admin.site.register(River, RivermapAdmin)


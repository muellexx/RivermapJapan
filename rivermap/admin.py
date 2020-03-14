from django.contrib import admin
from .models import Region, Prefecture, River, Observatory, Dam, Section, Spot, Comment


class RivermapAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_jp')


class PrefectureAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_jp', 'region')
    ordering = ['pk']


class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_jp')
    ordering = ['pk']


admin.site.register(Region, RegionAdmin)
admin.site.register(Prefecture, PrefectureAdmin)
admin.site.register(River, RivermapAdmin)
admin.site.register(Observatory)
admin.site.register(Dam)
admin.site.register(Section)
admin.site.register(Spot)
admin.site.register(Comment)


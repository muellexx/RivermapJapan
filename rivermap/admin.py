from django.contrib import admin
from .models import Region, Prefecture, River, Observatory, Dam, Section, Spot, Comment


class RivermapAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'name_jp')
    ordering = ['pk']


class PrefectureAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_jp', 'region')
    ordering = ['pk']


class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_jp')
    ordering = ['pk']


class RiverObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_jp', 'prefecture')
    ordering = ['id']


admin.site.register(Region, RegionAdmin)
admin.site.register(Prefecture, PrefectureAdmin)
admin.site.register(River, RivermapAdmin)
admin.site.register(Observatory)
admin.site.register(Dam)
admin.site.register(Section, RiverObjectAdmin)
admin.site.register(Spot, RiverObjectAdmin)
admin.site.register(Comment)


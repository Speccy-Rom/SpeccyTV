from django.contrib import admin

from .models import FilmWork, File


class FileInLineAdmin(admin.TabularInline):
    model = FilmWork.files.through
    extra = 0


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    list_display = ('title',)
    fields = ('title', 'certificate', 'file_path')
    inlines = (FileInLineAdmin,)
    search_fields = ('title', 'files')


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'resolution',
        'fps',
        'codec_name',
    )
    list_filter = (
        'resolution',
        'fps',
        'codec_name',
    )
    inlines = (FileInLineAdmin,)
    search_fields = (
        'id',
        'resolution',
        'fps',
        'codec_name',
    )

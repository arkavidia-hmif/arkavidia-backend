from arkav.uploader.models import UploadedFile
from arkav.uploader.services import UploadedFileService
from django.contrib import admin
from django.utils.html import format_html


@admin.register(UploadedFile)
class UploadedFileAdminAdmin(admin.ModelAdmin):
    list_display = ['file_download', 'id', 'file_size', 'uploaded_by', 'uploaded_at']
    list_display_links = ['id']
    search_fields = ['original_filename', 'uploaded_by']
    readonly_fields = ['file_download', 'id', 'file_size']
    autocomplete_fields = ['uploaded_by']

    def save_model(self, request, obj, form, change):
        return UploadedFileService().save_file(request.user, request.FILES['content'], '')

    def file_download(self, instance):
        if instance.id:
            return format_html('<a href="{}" download="{}">Download</a>',
                               instance.file_link, instance.original_filename)
        return '-'

    def has_change_permission(self, request, obj=None):
        return False

    class Meta:
        ordering = ['-uploaded_at']

from arkav.uploader.models import UploadedFile
from rest_framework import serializers


class UploadedFileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    uploaded_by = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = UploadedFile
        fields = ('id', 'original_filename', 'file_size',
                  'description', 'uploaded_by', 'uploaded_at', 'file_link')
        read_only_fields = ('id', 'original_filename', 'file_size',
                            'description', 'uploaded_by', 'uploaded_at', 'file_link')

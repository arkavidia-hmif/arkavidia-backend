from arkav.uploader.models import UploadedFile
import uuid


class UploadedFileService:
    def save_file(self, user, file_form, description):
        """
        Replace the file's original name into uuid,
        so the file won't be overwrite each other on S3.
        """
        file_name = file_form.name
        file_id = uuid.uuid4()
        file_form.name = str(file_id)

        uploaded_file = UploadedFile(
            id=file_id,
            original_filename=file_name,
            file_size=file_form.size,
            uploaded_by=user,
            content_type=file_form.content_type,
            description=description,
            content=file_form,
        )
        uploaded_file.save()
        return uploaded_file

from arkav.arkavauth.models import User
from arkav.uploader.models import UploadedFile
from arkav.uploader.serializers import UploadedFileSerializer
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RetrieveUploadedFileTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('yonas@gmail.com', 'password',
                                             full_name='Yonas Adiel',
                                             is_email_confirmed=True)
        self.file1 = UploadedFile.objects.create(
            original_filename='abc.jpg',
            file_size=200,
            description='description',
            content_type='images/jpg',
            uploaded_by=self.user,
        )

    def test_retrieve_file(self):
        url = reverse('uploader-uploaded-file-detail', kwargs={'file_id': str(self.file1.id)})
        self.client.force_authenticate(self.user)
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertDictEqual(res.data, UploadedFileSerializer(self.file1).data)

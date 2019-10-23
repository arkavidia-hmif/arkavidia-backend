from arkav.uploader.models import UploadedFile
from arkav.uploader.serializers import UploadedFileSerializer
from arkav.uploader.serializers import UploadFileRequestSerializer
from arkav.uploader.services import UploadedFileService
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


upload_responses = {
    200: UploadedFileSerializer(),
}


class UploadFileView(generics.GenericAPIView):
    serializer_class = UploadFileRequestSerializer
    parser_classes = (MultiPartParser,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(responses=upload_responses, operation_summary='Upload File')
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            uploaded_file = UploadedFileService().save_file(request.user, serializer.validated_data['file'],
                                                            serializer.validated_data['description'])
            return Response(UploadedFileSerializer(uploaded_file).data)
        else:
            return Response({
                'code': 'file_error',
                'detail': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)


class RetrieveUploadedFileView(generics.RetrieveAPIView):
    serializer_class = UploadedFileSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UploadedFile.objects.all()

    def get_object(self):
        instance = get_object_or_404(
            self.get_queryset(),
            id=self.kwargs['file_id'],
        )
        self.check_object_permissions(self.request, instance)
        return instance

    @swagger_auto_schema(operation_summary='Retrieve File')
    def get(self, request, **kwargs):
        return super().get(request, **kwargs)

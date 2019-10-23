from arkav.uploader.models import UploadedFile
from arkav.uploader.serializers import UploadedFileSerializer
from arkav.uploader.services import UploadedFileService
from django import forms
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class UploadFileForm(forms.Form):
    file = forms.FileField()
    description = forms.CharField(max_length=200, required=False)


@login_required
@require_POST
def upload_file_view(request):
    '''
    Handle file upload (Django request, not using DRF).
    '''
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        uploaded_file = UploadedFileService().save_file(request.user, form.cleaned_data['file'],
                                                        form.cleaned_data['description'])
        return Response(UploadedFileSerializer(uploaded_file).data)
    else:
        return Response({
            'errors': form.errors,
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

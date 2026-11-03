from rest_framework import mixins, parsers, viewsets
from uploader.permissions import MediaModelPermissions

from uploader.models import Document, Image, Video
from uploader.serializers import DocumentUploadSerializer, ImageUploadSerializer, VideoUploadSerializer


class CreateViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [MediaModelPermissions]
    parser_classes = [parsers.FormParser, parsers.MultiPartParser]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ImageUploadViewSet(CreateViewSet):
    queryset = Image.objects.all().order_by('-id')
    serializer_class = ImageUploadSerializer


class DocumentUploadViewSet(CreateViewSet):
    queryset = Document.objects.all().order_by('-id')
    serializer_class = DocumentUploadSerializer


class VideoUploadViewSet(CreateViewSet):
    queryset = Video.objects.all().order_by('-id')
    serializer_class = VideoUploadSerializer

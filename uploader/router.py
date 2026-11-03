from rest_framework.routers import DefaultRouter
from uploader.views import DocumentUploadViewSet, ImageUploadViewSet, VideoUploadViewSet

router = DefaultRouter()
router.register('images', ImageUploadViewSet, basename='images')
router.register('documents', DocumentUploadViewSet, basename='documents')
router.register('videos', VideoUploadViewSet, basename='videos')

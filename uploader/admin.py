from django.contrib import admin
from uploader.models import Document, Image, Video

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'owner', 'uploaded_on')
    search_fields = ('description', 'owner__email', 'owner__username')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'owner', 'uploaded_on')
    search_fields = ('description', 'owner__email', 'owner__username')


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'owner', 'uploaded_on')
    search_fields = ('description', 'owner__email', 'owner__username')

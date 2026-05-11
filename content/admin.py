from django.contrib import admin
from .models import Announcement, StudyMaterial

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'school', 'created_by', 'created_at']
    list_filter = ['school']

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'material_type', 'subject', 'class_assigned', 'uploaded_by', 'uploaded_at']
    list_filter = ['material_type', 'school', 'subject']

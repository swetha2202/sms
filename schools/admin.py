from django.contrib import admin
from .models import School, Class, Subject

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'school_code', 'is_active', 'created_at']
    search_fields = ['name', 'school_code']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'school']
    list_filter = ['school']

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'school']
    filter_horizontal = ['teachers', 'students', 'subjects']
    list_filter = ['school']

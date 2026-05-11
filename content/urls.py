from django.urls import path
from . import views

urlpatterns = [
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/create/', views.announcement_create, name='announcement_create'),
    path('announcements/<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),
    path('materials/', views.material_list, name='material_list'),
    path('materials/upload/', views.material_upload, name='material_upload'),
    path('materials/<int:pk>/delete/', views.material_delete, name='material_delete'),
    path('student/materials/', views.student_materials, name='student_materials'),
]

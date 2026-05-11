from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Announcement, StudyMaterial
from schools.models import Class, Subject
from accounts.models import User
from functools import wraps


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                messages.error(request, 'Access denied.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ── ANNOUNCEMENTS ────────────────────────────────────────────────────────────

@role_required('school_admin')
def announcement_create(request):
    school = request.user.school
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        video = request.FILES.get('video')

        if not title or not body:
            messages.error(request, 'Title and body are required.')
        else:
            Announcement.objects.create(
                title=title, body=body, school=school,
                created_by=request.user, video=video
            )
            messages.success(request, 'Announcement posted.')
            return redirect('dashboard')

    return render(request, 'content/announcement_form.html')


@role_required('school_admin')
def announcement_list(request):
    school = request.user.school
    announcements = Announcement.objects.filter(school=school).order_by('-created_at')
    return render(request, 'content/announcement_list.html', {'announcements': announcements})


@role_required('school_admin')
def announcement_delete(request, pk):
    school = request.user.school
    ann = get_object_or_404(Announcement, pk=pk, school=school)
    if request.method == 'POST':
        ann.delete()
        messages.success(request, 'Announcement deleted.')
    return redirect('announcement_list')


# ── STUDY MATERIALS ──────────────────────────────────────────────────────────

@role_required('teacher')
def material_upload(request):
    user = request.user
    school = user.school
    my_classes = user.assigned_classes.filter(school=school)
    subjects = Subject.objects.filter(school=school)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        material_type = request.POST.get('material_type', '')
        file = request.FILES.get('file')
        subject_id = request.POST.get('subject')
        class_id = request.POST.get('class_assigned')
        description = request.POST.get('description', '')

        if not all([title, material_type, file, subject_id, class_id]):
            messages.error(request, 'All fields are required.')
        else:
            subject = get_object_or_404(Subject, pk=subject_id, school=school)
            cls = get_object_or_404(Class, pk=class_id, school=school, teachers=user)
            StudyMaterial.objects.create(
                title=title, material_type=material_type, file=file,
                subject=subject, class_assigned=cls, uploaded_by=user,
                school=school, description=description
            )
            messages.success(request, 'Material uploaded successfully.')
            return redirect('material_list')

    return render(request, 'content/material_form.html', {
        'classes': my_classes, 'subjects': subjects
    })


@role_required('teacher')
def material_list(request):
    materials = StudyMaterial.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')
    return render(request, 'content/material_list.html', {'materials': materials})


@role_required('teacher')
def material_delete(request, pk):
    material = get_object_or_404(StudyMaterial, pk=pk, uploaded_by=request.user)
    if request.method == 'POST':
        material.file.delete(save=False)
        material.delete()
        messages.success(request, 'Material deleted.')
    return redirect('material_list')


# ── STUDENT: View materials ──────────────────────────────────────────────────

@role_required('student')
def student_materials(request):
    user = request.user
    school = user.school
    my_classes = user.enrolled_classes.filter(school=school)
    type_filter = request.GET.get('type', '')
    subject_filter = request.GET.get('subject', '')

    materials = StudyMaterial.objects.filter(class_assigned__in=my_classes).order_by('-uploaded_at')
    if type_filter:
        materials = materials.filter(material_type=type_filter)
    if subject_filter:
        materials = materials.filter(subject_id=subject_filter)

    subjects = Subject.objects.filter(school=school, classes__in=my_classes).distinct()
    announcements = Announcement.objects.filter(school=school).order_by('-created_at')

    return render(request, 'content/student_materials.html', {
        'materials': materials, 'subjects': subjects,
        'type_filter': type_filter, 'subject_filter': subject_filter,
        'announcements': announcements, 'my_classes': my_classes
    })

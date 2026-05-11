from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import School, Class, Subject
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


# ── SUPER ADMIN: School Management ──────────────────────────────────────────

@role_required('super_admin')
def school_list(request):
    schools = School.objects.all().order_by('-created_at')
    return render(request, 'schools/school_list.html', {'schools': schools})


@role_required('super_admin')
def school_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        school_code = request.POST.get('school_code', '').strip().upper()
        address = request.POST.get('address', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')

        if not name or not school_code:
            messages.error(request, 'Name and school code are required.')
            return render(request, 'schools/school_form.html')

        if School.objects.filter(school_code=school_code).exists():
            messages.error(request, 'School code already exists.')
            return render(request, 'schools/school_form.html')

        school = School.objects.create(
            name=name, school_code=school_code,
            address=address, phone=phone, email=email
        )
        messages.success(request, f'School "{school.name}" created successfully.')
        return redirect('school_list')

    return render(request, 'schools/school_form.html')


@role_required('super_admin')
def school_edit(request, pk):
    school = get_object_or_404(School, pk=pk)
    if request.method == 'POST':
        school.name = request.POST.get('name', school.name).strip()
        school.address = request.POST.get('address', school.address)
        school.phone = request.POST.get('phone', school.phone)
        school.email = request.POST.get('email', school.email)
        school.is_active = 'is_active' in request.POST
        school.save()
        messages.success(request, 'School updated successfully.')
        return redirect('school_list')
    return render(request, 'schools/school_form.html', {'school': school})


@role_required('super_admin')
def school_toggle(request, pk):
    school = get_object_or_404(School, pk=pk)
    school.is_active = not school.is_active
    school.save()
    status = 'activated' if school.is_active else 'deactivated'
    messages.success(request, f'School {status}.')
    return redirect('school_list')


# ── SCHOOL ADMIN: User Management ───────────────────────────────────────────

@role_required('school_admin')
def user_list(request):
    school = request.user.school
    role_filter = request.GET.get('role', '')
    users = User.objects.filter(school=school).exclude(role='school_admin')
    if role_filter:
        users = users.filter(role=role_filter)
    return render(request, 'schools/user_list.html', {'users': users, 'role_filter': role_filter})


@role_required('school_admin')
def user_create(request):
    school = request.user.school
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        role = request.POST.get('role', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')

        if role not in ('teacher', 'student'):
            messages.error(request, 'Invalid role.')
            return render(request, 'schools/user_form.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'schools/user_form.html')

        user = User.objects.create_user(
            username=username, password=password,
            role=role, school=school,
            first_name=first_name, last_name=last_name, email=email
        )
        messages.success(request, f'{role.title()} "{username}" created.')
        return redirect('user_list')

    return render(request, 'schools/user_form.html')


@role_required('school_admin')
def user_delete(request, pk):
    school = request.user.school
    user = get_object_or_404(User, pk=pk, school=school)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted.')
    return redirect('user_list')


# ── SCHOOL ADMIN: Subject Management ────────────────────────────────────────

@role_required('school_admin')
def subject_list(request):
    school = request.user.school
    subjects = Subject.objects.filter(school=school)
    return render(request, 'schools/subject_list.html', {'subjects': subjects})


@role_required('school_admin')
def subject_create(request):
    school = request.user.school
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            Subject.objects.create(name=name, school=school)
            messages.success(request, f'Subject "{name}" created.')
            return redirect('subject_list')
    return render(request, 'schools/subject_form.html')


@role_required('school_admin')
def subject_delete(request, pk):
    school = request.user.school
    subject = get_object_or_404(Subject, pk=pk, school=school)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Subject deleted.')
    return redirect('subject_list')


# ── SCHOOL ADMIN: Class Management ──────────────────────────────────────────

@role_required('school_admin')
def class_list(request):
    school = request.user.school
    classes = Class.objects.filter(school=school).prefetch_related('teachers', 'students', 'subjects')
    return render(request, 'schools/class_list.html', {'classes': classes})


@role_required('school_admin')
def class_create(request):
    school = request.user.school
    teachers = User.objects.filter(school=school, role='teacher')
    subjects = Subject.objects.filter(school=school)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        teacher_ids = request.POST.getlist('teachers')
        subject_ids = request.POST.getlist('subjects')

        if not name:
            messages.error(request, 'Class name required.')
        else:
            cls = Class.objects.create(name=name, school=school)
            cls.teachers.set(teacher_ids)
            cls.subjects.set(subject_ids)
            messages.success(request, f'Class "{name}" created.')
            return redirect('class_list')

    return render(request, 'schools/class_form.html', {'teachers': teachers, 'subjects': subjects})


@role_required('school_admin')
def class_edit(request, pk):
    school = request.user.school
    cls = get_object_or_404(Class, pk=pk, school=school)
    teachers = User.objects.filter(school=school, role='teacher')
    students = User.objects.filter(school=school, role='student')
    subjects = Subject.objects.filter(school=school)

    if request.method == 'POST':
        cls.name = request.POST.get('name', cls.name).strip()
        cls.teachers.set(request.POST.getlist('teachers'))
        cls.subjects.set(request.POST.getlist('subjects'))
        cls.students.set(request.POST.getlist('students'))
        cls.save()
        messages.success(request, 'Class updated.')
        return redirect('class_list')

    return render(request, 'schools/class_form.html', {
        'cls': cls, 'teachers': teachers,
        'students': students, 'subjects': subjects
    })


@role_required('school_admin')
def class_delete(request, pk):
    school = request.user.school
    cls = get_object_or_404(Class, pk=pk, school=school)
    if request.method == 'POST':
        cls.delete()
        messages.success(request, 'Class deleted.')
    return redirect('class_list')


# ── TEACHER: Add student to class ───────────────────────────────────────────

@role_required('teacher')
def teacher_class_detail(request, pk):
    school = request.user.school
    cls = get_object_or_404(Class, pk=pk, school=school, teachers=request.user)
    available_students = User.objects.filter(school=school, role='student').exclude(enrolled_classes=cls)

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student = get_object_or_404(User, pk=student_id, school=school, role='student')
        cls.students.add(student)
        messages.success(request, f'{student.get_full_name() or student.username} added to class.')
        return redirect('teacher_class_detail', pk=pk)

    return render(request, 'schools/teacher_class_detail.html', {
        'cls': cls, 'available_students': available_students
    })

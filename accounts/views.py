from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from schools.models import School
from .models import User


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        school_code = request.POST.get('school_code', '').strip().upper()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Super admin uses ADMIN code or empty
        if school_code in ('ADMIN', ''):
            user = authenticate(request, username=username, password=password)
            if user and user.is_super_admin():
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid super admin credentials.')
                return render(request, 'accounts/login.html')

        # School-level login
        try:
            school = School.objects.get(school_code=school_code, is_active=True)
        except School.DoesNotExist:
            messages.error(request, 'Invalid or inactive school code.')
            return render(request, 'accounts/login.html')

        user = authenticate(request, username=username, password=password)
        if user and user.school == school:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials for this school.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}

    if user.is_super_admin():
        from schools.models import School
        context['schools'] = School.objects.all()
        context['total_schools'] = School.objects.count()
        context['active_schools'] = School.objects.filter(is_active=True).count()
        context['total_users'] = User.objects.exclude(role='super_admin').count()
        return render(request, 'dashboard/super_admin.html', context)

    elif user.is_school_admin():
        from schools.models import Class, Subject
        from content.models import Announcement, StudyMaterial
        school = user.school
        context['school'] = school
        context['teachers'] = User.objects.filter(school=school, role='teacher')
        context['students'] = User.objects.filter(school=school, role='student')
        context['classes'] = Class.objects.filter(school=school)
        context['subjects'] = Subject.objects.filter(school=school)
        context['announcements'] = Announcement.objects.filter(school=school).order_by('-created_at')[:5]
        return render(request, 'dashboard/school_admin.html', context)

    elif user.is_teacher():
        from schools.models import Class
        from content.models import StudyMaterial
        school = user.school
        context['school'] = school
        context['my_classes'] = user.assigned_classes.filter(school=school)
        context['my_materials'] = StudyMaterial.objects.filter(uploaded_by=user).order_by('-uploaded_at')[:5]
        return render(request, 'dashboard/teacher.html', context)

    elif user.is_student():
        from schools.models import Class
        from content.models import StudyMaterial, Announcement
        school = user.school
        my_classes = user.enrolled_classes.filter(school=school)
        context['school'] = school
        context['my_classes'] = my_classes
        context['materials'] = StudyMaterial.objects.filter(class_assigned__in=my_classes).order_by('-uploaded_at')
        context['announcements'] = Announcement.objects.filter(school=school).order_by('-created_at')[:5]
        return render(request, 'dashboard/student.html', context)

    return redirect('login')

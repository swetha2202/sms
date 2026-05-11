from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_SUPER_ADMIN = 'super_admin'
    ROLE_SCHOOL_ADMIN = 'school_admin'
    ROLE_TEACHER = 'teacher'
    ROLE_STUDENT = 'student'

    ROLE_CHOICES = [
        (ROLE_SUPER_ADMIN, 'Super Admin'),
        (ROLE_SCHOOL_ADMIN, 'School Admin'),
        (ROLE_TEACHER, 'Teacher'),
        (ROLE_STUDENT, 'Student'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    school = models.ForeignKey(
        'schools.School', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='users'
    )

    def is_super_admin(self):
        return self.role == self.ROLE_SUPER_ADMIN

    def is_school_admin(self):
        return self.role == self.ROLE_SCHOOL_ADMIN

    def is_teacher(self):
        return self.role == self.ROLE_TEACHER

    def is_student(self):
        return self.role == self.ROLE_STUDENT

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

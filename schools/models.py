from django.db import models
import uuid


class School(models.Model):
    name = models.CharField(max_length=200)
    school_code = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.school_code})"

    def save(self, *args, **kwargs):
        if not self.school_code:
            self.school_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)


class Subject(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='subjects')

    def __str__(self):
        return f"{self.name} - {self.school.name}"


class Class(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    teachers = models.ManyToManyField(
        'accounts.User', blank=True,
        related_name='assigned_classes',
        limit_choices_to={'role': 'teacher'}
    )
    subjects = models.ManyToManyField(Subject, blank=True, related_name='classes')
    students = models.ManyToManyField(
        'accounts.User', blank=True,
        related_name='enrolled_classes',
        limit_choices_to={'role': 'student'}
    )

    def __str__(self):
        return f"{self.name} - {self.school.name}"

    class Meta:
        verbose_name_plural = "Classes"

from django.db import models


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='announcements')
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    video = models.FileField(upload_to='announcements/videos/', blank=True, null=True)

    def __str__(self):
        return self.title


class StudyMaterial(models.Model):
    TYPE_PDF = 'pdf'
    TYPE_VIDEO = 'video'
    TYPE_CHOICES = [(TYPE_PDF, 'PDF Notes'), (TYPE_VIDEO, 'Video Lecture')]

    title = models.CharField(max_length=200)
    material_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    file = models.FileField(upload_to='materials/')
    subject = models.ForeignKey('schools.Subject', on_delete=models.CASCADE, related_name='materials')
    class_assigned = models.ForeignKey('schools.Class', on_delete=models.CASCADE, related_name='materials')
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='materials')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.get_material_type_display()})"

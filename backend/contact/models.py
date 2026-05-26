from django.db import models


class ProjectType(models.TextChoices):
    BACKEND    = 'backend',    'Backend / API'
    WEB        = 'web',        'Web Development'
    AI         = 'ai',         'AI / Intelligent App'
    FULLSTACK  = 'fullstack',  'Full-Stack Product'
    OTHER      = 'other',      'Other'


class Status(models.TextChoices):
    NEW        = 'new',        'New'
    IN_REVIEW  = 'in_review',  'In Review'
    CONTACTED  = 'contacted',  'Contacted'
    CLOSED     = 'closed',     'Closed'


class Inquiry(models.Model):
    name         = models.CharField(max_length=120)
    email        = models.EmailField()
    project_type = models.CharField(max_length=20, choices=ProjectType.choices)
    message      = models.TextField()
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    ip_address   = models.GenericIPAddressField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Inquiry'
        verbose_name_plural = 'Inquiries'

    def __str__(self):
        return f'{self.name} — {self.get_project_type_display()} ({self.created_at:%d %b %Y})'

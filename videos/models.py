from datetime import date
from django.db import models

class Video(models.Model):
    created_at=models.DateField(default=date.today)
    title=models.CharField(max_length=80)
    description=models.CharField(max_length=500)
    genre=models.CharField(max_length=80, default=0)
    video_file=models.FileField(upload_to='videos',blank=True,null=True)
    
    def _str_(self):
        return self.Title

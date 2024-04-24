import os
from .models import Video
from django.dispatch import receiver
from django.db.models.signals import post_save,post_delete

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    print('video wurde gespeichert')
    if created:
        print('new video created')
        
@receiver(post_delete,sender=Video)
def auto_delete_file_on_delete(sender,instance,**kwargs):
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)
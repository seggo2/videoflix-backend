# signals.py
import django_rq
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Video
from .tasks import process_full_video, convert_video_delete


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        queue = django_rq.get_queue('default')
        # Starte den neuen Full-Processing-Task
        queue.enqueue(process_full_video, instance.video_file.path)


@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.video_file:
        convert_video_delete(instance.video_file.path)  # <-- hinzugefügt
        instance.video_file.delete(save=False)

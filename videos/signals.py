# signals.py
import os
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import django_rq
from .models import Video
from .tasks import convert_video, convert_video_720p, convert_video_1080p, extract_thumbnail, convert_video_delete


@receiver(post_save, sender=Video)


def video_post_save(sender, instance, created, **kwargs):
    if created:
        queue = django_rq.get_queue('default')
        queue.enqueue(convert_video, instance.video_file.path)
        queue.enqueue(convert_video_720p, instance.video_file.path)
        queue.enqueue(convert_video_1080p, instance.video_file.path)
        queue.enqueue(extract_thumbnail, instance.video_file.path)


@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.video_file and os.path.isfile(instance.video_file.path):
        os.remove(instance.video_file.path)
        convert_video_delete(instance.video_file.path)

import os

from django.conf import settings
from django.db.models import Model, TextField, CASCADE, ImageField, BooleanField, ForeignKey


class PageTask(Model):
    url = TextField()
    text_content = TextField(null=True)
    images_in_progress = BooleanField(default=False)

    def __str__(self):
        return f"Task object ID={self.pk} (for page {self.url})"


def get_image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<page_id>/<filename>
    return '{0}/{1}'.format(instance.page.pk, filename)


class PageImage(Model):
    page = ForeignKey(PageTask, on_delete=CASCADE)
    image = ImageField(upload_to=get_image_path)

    def __str__(self):
        return f"PageImages object ID={self.pk} (for page {self.page.url})"

    def delete(self, *args, **kwargs):
        os.remove(os.path.join(settings.MEDIA_ROOT, self.image.name))
        super().delete(*args, **kwargs)

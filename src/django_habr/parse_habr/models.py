from django.db import models
from django.urls import reverse


class Articles(models.Model):
    link = models.CharField(max_length=4000, null=False, primary_key=True)
    title: str = models.CharField(max_length=2000, null=False)
    date_published = models.DateField(null=False)
    link_to_author = models.CharField(max_length=4000, null=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post", kwargs={"post_id": self.pk})

    class Meta:
        verbose_name = "Хабр статьи"
        verbose_name_plural = "Хабр статьи"

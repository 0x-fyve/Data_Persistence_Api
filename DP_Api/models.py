import uuid6
from django.db import models

# Create your models here.
def generate_uuid7():
    return uuid6.uuid7()

class Profile(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=generate_uuid7,
        editable=False
    )
    name = models.CharField(max_length=100, unique=True)

    gender = models.CharField(max_length=10, null=True, blank=True)
    gender_probability = models.FloatField(null=True, blank=True)

    sample_size = models.IntegerField(null=True, blank=True)

    age = models.IntegerField(null=True, blank=True)
    age_group = models.CharField(max_length=20, null=True, blank=True)

    country_id = models.CharField(max_length=10, null=True, blank=True)
    country_probability = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.gender}"
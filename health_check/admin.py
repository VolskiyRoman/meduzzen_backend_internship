from django.contrib import admin
from .models import User
from .models import TimeStampedModel

admin.site.register(User)
admin.site.register(TimeStampedModel)
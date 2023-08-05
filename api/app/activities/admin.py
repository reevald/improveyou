from django.contrib import admin

from .models import Activity, Recommendation, UrgeCategory

# Register your models here.
admin.site.register(Activity)
admin.site.register(UrgeCategory)
admin.site.register(Recommendation)

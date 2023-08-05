from django.contrib import admin

from .models import Event, Item, Reward

# Register your models here.
admin.site.register(Item)
admin.site.register(Event)
admin.site.register(Reward)

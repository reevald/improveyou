from django.contrib import admin

from .models import (
    ActivityLog,
    Bag,
    DailyCheck,
    DailyCheckQuestion,
    EmailVerificationToken,
    EventReward,
    GameStat,
    Object,
    RecommendationLog,
    ResetPasswordToken,
    TaskLog,
    User,
)

# https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Admin_site
# Register your models here.
admin.site.register(User)
admin.site.register(ResetPasswordToken)
admin.site.register(EmailVerificationToken)
admin.site.register(GameStat)
admin.site.register(DailyCheck)
admin.site.register(Object)
admin.site.register(Bag)
admin.site.register(ActivityLog)
admin.site.register(DailyCheckQuestion)
admin.site.register(EventReward)
admin.site.register(TaskLog)
admin.site.register(RecommendationLog)

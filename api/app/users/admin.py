from django.contrib import admin

from .models import (
    DailyCheck,
    EmailVerificationToken,
    GameStat,
    ResetPasswordToken,
    User,
)

# https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Admin_site
# Register your models here.
admin.site.register(User)
admin.site.register(ResetPasswordToken)
admin.site.register(EmailVerificationToken)
admin.site.register(GameStat)
admin.site.register(DailyCheck)

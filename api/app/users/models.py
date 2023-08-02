import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone

TIERS = [("basic", "BASIC"), ("premium", "PREMIUM")]
STREAK_STATUS = [
    ("none", "NONE"),
    ("continue", "CONTINUE"),
    ("discontinue", "DISCONTINUE"),
]


class User(AbstractBaseUser, PermissionsMixin):
    # https://dba.stackexchange.com/a/119129
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    email = models.EmailField(unique=True)
    email_validated = models.BooleanField(default=False)
    username = models.CharField(
        max_length=14, validators=[MinLengthValidator(6)], unique=True
    )
    last_username_changed = models.DateTimeField(blank=True, null=True)
    tier = models.CharField(choices=TIERS, default="basic", max_length=32)
    is_public_mode = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    ban_status = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    # This will usually be a username of some kind, but it can also be an email address,
    # or any other unique identifier
    USERNAME_FIELD = "email"
    # Username, email and password will always be prompted for
    # https://stackoverflow.com/a/66014955
    REQUIRED_FIELDS = ["username"]
    # Config user manager
    objects = UserManager()

    def __str__(self):
        return self.username

    class Meta:
        db_table = "users"


class ResetPasswordToken(models.Model):
    token = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    issue_at = models.DateTimeField(default=timezone.now)
    exp_at = models.DateTimeField(blank=True, null=True)
    reset_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.token)

    class Meta:
        db_table = "reset_password_tokens"


class EmailVerificationToken(models.Model):
    token = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    issue_at = models.DateTimeField(default=timezone.now)
    exp_at = models.DateTimeField(blank=True, null=True)
    verify_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.token)

    class Meta:
        db_table = "email_verification_tokens"


class GameStat(models.Model):
    user_id = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, db_column="user_id"
    )
    gold = models.IntegerField(default=0)
    poin_brain = models.IntegerField(default=0)
    poin_heart = models.IntegerField(default=0)
    poin_muscle = models.IntegerField(default=0)
    streak_current = models.IntegerField(default=0)
    streak_percent_interest = models.IntegerField(default=0)
    last_exchange = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return (
            f"[🪙 {self.gold}]"
            + f"[🧠 {self.poin_brain}]"
            + f"[💪 {self.poin_muscle}]"
            + f"[🧘 {self.poin_heart}]"
            + f"[🔥 {self.streak_current}; {self.streak_percent_interest}%]"
        )

    class Meta:
        db_table = "users_game_stats"


class DailyCheck(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    date_target = models.DateTimeField(blank=True, null=True)
    streak_status = models.CharField(
        choices=STREAK_STATUS, default="none", max_length=32
    )
    # Save (to string): json.dumps(dict) and loads (to dict) : json.loads(string)
    # Schema questions
    # [
    #     {
    #         "question": "App rate that help user",
    #         "user_answer": 5
    #     }
    # ]
    other_questions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.date_target} => {self.streak_status}"

    class Meta:
        db_table = "users_daily_check"
        # One day = one check for each user
        unique_together = ("user_id", "date_target")

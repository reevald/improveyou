import uuid

from activities.models import URGE_LEVELS
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

SOURCE_TYPES = [("default", "DEFAULT"), ("event", "EVENT"), ("shop", "SHOP")]


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
    bag_items = models.ManyToManyField("items.Item", through="Bag")

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


class DailyCheckQuestion(models.Model):
    # TODO: create api to get daily check question (other)
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    question = models.TextField(blank=True, null=True)
    availability = models.BooleanField(default=False)
    type_answer = models.CharField(
        choices=[("limited", "LIMITED"), ("free", "FREE")], max_length=32
    )
    limited_answer = models.TextField(blank=True, null=True)
    # Schema limited answer
    # Save (to string): json.dumps(dict) and loads (to dict) : json.loads(string)
    # [
    #     "answer opsi 1",
    #     "answer opsi 2",
    # ]

    def __str__(self):
        return self.question

    class Meta:
        db_table = "users_daily_check_questions"


class DailyCheck(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    date_target = models.DateTimeField(blank=True, null=True)
    streak_status = models.CharField(
        choices=STREAK_STATUS, default="none", max_length=32
    )
    # Save (to string): json.dumps(dict) and loads (to dict) : json.loads(string)
    # Schema other questions
    # [
    #     {
    #         "question_id": "0asdja9sjd91j09dj90129",
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


class Object(models.Model):
    user_id = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, db_column="user_id"
    )
    character_id = models.ForeignKey(
        "items.Item",
        on_delete=models.CASCADE,
        db_column="character_id",
        blank=True,  # Default (resource handle by frontend)
        null=True,
        related_name="object_character",
    )
    hat_id = models.ForeignKey(
        "items.Item",
        on_delete=models.CASCADE,
        db_column="hat_id",
        blank=True,  # Default
        null=True,
        related_name="object_hat",
    )
    clothes_id = models.ForeignKey(
        "items.Item",
        on_delete=models.CASCADE,
        db_column="clothes_id",
        blank=True,  # Default
        null=True,
        related_name="object_clothes",
    )
    shoes_id = models.ForeignKey(
        "items.Item",
        on_delete=models.CASCADE,
        db_column="shoes_id",
        blank=True,  # Default
        null=True,
        related_name="object_shoes",
    )
    background_id = models.ForeignKey(
        "items.Item",
        on_delete=models.CASCADE,
        db_column="background_id",
        blank=True,  # Default
        null=True,
        related_name="object_background",
    )
    updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return (
            f"[👤 {self.user_id}]"
            + f"[👺 {self.character_id}]"
            + f"[🎩 {self.hat_id}]"
            + f"[👕 {self.clothes_id}]"
            + f"[👖 {self.shoes_id}]"
            + f"[🏞️ {self.background_id}]"
        )

    class Meta:
        db_table = "users_objects"


class Bag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    item_id = models.ForeignKey(
        "items.Item", on_delete=models.CASCADE, db_column="item_id"
    )
    source_type = models.CharField(choices=SOURCE_TYPES, max_length=32)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"[👤 {self.user_id}]" + f"[📦 {self.item_id}]"

    class Meta:
        db_table = "users_bags"
        unique_together = ("user_id", "item_id")


class ActivityLog(models.Model):
    # Only insert new data if the previous activity already done (finish)
    # Case 1: If today not finish then continue tomorrow until finish (w/o play trigger)
    # (count as today activity => start today not tomorrow)
    # Case 2: Even today not finish, if tomorrow w/ new trigger play
    # then play_at updated and if tomorrow finish it will count as tomorrow activity
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    activity_id = models.ForeignKey(
        "activities.Activity", on_delete=models.CASCADE, db_column="activity_id"
    )
    created_at = models.DateTimeField(default=timezone.now)
    play_at = models.DateTimeField(blank=True, null=True)
    finish_at = models.DateTimeField(blank=True, null=True)
    track = models.TextField(blank=True, null=True)

    # Schema of track
    # Save (to string): json.dumps(dict) and loads (to dict) : json.loads(string)
    # {
    #     "type": "READ",
    #     "data": {
    #         "target": {"type": "AMOUNT", "current": 0, "goals": 10, "unit": "STAR"},
    #         "attempt": {"current": 0, "max": 3},
    #         "logs": {  # From init (play) it will generate all choosen questId
    #             "<questId>": -1  # 1=true, 0=false, -1=Not answer yet(default)
    #         },
    #     },
    # }
    # {
    #     "type": "POSE", # Same for "AUDIO"
    #     "data": {
    #         "target": {"type": "TIME", "current": 0, "goals": 180, "unit": "SECOND"},
    #     },
    # }
    def __str__(self):
        return f"[👤 {self.user_id}]" + f"[🏃 {self.activity_id}]"

    class Meta:
        db_table = "users_activity_log"


class EventReward(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    event_id = models.ForeignKey(
        "items.Event", on_delete=models.CASCADE, db_column="event_id"
    )
    rewards_claimed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"[👤 {self.user_id}]" + f"🐾 {self.event_id}]"

    class Meta:
        db_table = "users_events_rewards"
        unique_together = ("user_id", "event_id")


class TaskLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    task_id = models.ForeignKey(
        "tasks.Task", on_delete=models.CASCADE, db_column="task_id"
    )
    current_progress = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(blank=True, null=True)
    # Created_at and completed_at must be in the same day

    def __str__(self):
        return f"[👤 {self.user_id}]" + f"[📝 {self.task_id}]"

    class Meta:
        db_table = "users_task_log"


class RecommendationLog(models.Model):
    # Each date to get new recommendation
    # Using default medium value and prediction can blank / null
    # to prevent if machine learning service have trouble
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    prediction = models.FloatField(blank=True, null=True)
    urge_level = models.CharField(choices=URGE_LEVELS, default="medium", max_length=32)
    issue_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"[👤 {self.user_id}]" + f"[🎲 {self.prediction}]"

    class Meta:
        db_table = "users_recommendation_log"
        # One day = one prediction
        unique_together = ("user_id", "issue_at")

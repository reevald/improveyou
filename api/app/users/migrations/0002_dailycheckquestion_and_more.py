# Generated by Django 4.2.3 on 2023-08-04 16:42

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("activities", "0001_initial"),
        ("items", "__first__"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DailyCheckQuestion",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid1,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("question", models.TextField(blank=True, null=True)),
                ("availability", models.BooleanField(default=False)),
                (
                    "type_answer",
                    models.CharField(
                        choices=[("limited", "LIMITED"), ("free", "FREE")],
                        max_length=32,
                    ),
                ),
                ("limited_answer", models.TextField(blank=True, null=True)),
            ],
            options={
                "db_table": "users_daily_check_questions",
            },
        ),
        migrations.RenameModel(
            old_name="EmailVerificationTokens",
            new_name="EmailVerificationToken",
        ),
        migrations.RenameModel(
            old_name="GameStats",
            new_name="GameStat",
        ),
        migrations.RenameModel(
            old_name="ResetPasswordTokens",
            new_name="ResetPasswordToken",
        ),
        migrations.AlterModelManagers(
            name="user",
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Object",
            fields=[
                (
                    "user_id",
                    models.OneToOneField(
                        db_column="user_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("updated_at", models.DateTimeField(blank=True, null=True)),
                (
                    "background_id",
                    models.ForeignKey(
                        db_column="background_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="object_background",
                        to="items.item",
                    ),
                ),
                (
                    "character_id",
                    models.ForeignKey(
                        db_column="character_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="object_character",
                        to="items.item",
                    ),
                ),
                (
                    "hat_id",
                    models.ForeignKey(
                        db_column="hat_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="object_hat",
                        to="items.item",
                    ),
                ),
                (
                    "shirt_id",
                    models.ForeignKey(
                        db_column="shirt_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="object_shirt",
                        to="items.item",
                    ),
                ),
                (
                    "trouser_id",
                    models.ForeignKey(
                        db_column="trouser_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="object_trouser",
                        to="items.item",
                    ),
                ),
            ],
            options={
                "db_table": "users_objects",
            },
        ),
        migrations.CreateModel(
            name="ActivityLog",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid1,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("play_at", models.DateTimeField(blank=True, null=True)),
                ("finish_at", models.DateTimeField(blank=True, null=True)),
                ("track", models.TextField(blank=True, null=True)),
                (
                    "activity_id",
                    models.ForeignKey(
                        db_column="activity_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="activities.activity",
                    ),
                ),
                (
                    "user_id",
                    models.ForeignKey(
                        db_column="user_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "users_activity_log",
            },
        ),
        migrations.CreateModel(
            name="Bag",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid1,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "source_type",
                    models.CharField(
                        choices=[
                            ("default", "DEFAULT"),
                            ("event", "EVENT"),
                            ("shop", "SHOP"),
                        ],
                        max_length=32,
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "item_id",
                    models.ForeignKey(
                        db_column="item_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="items.item",
                    ),
                ),
                (
                    "user_id",
                    models.ForeignKey(
                        db_column="user_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "users_bags",
                "unique_together": {("user_id", "item_id")},
            },
        ),
    ]
import uuid

from django.db import models
from django.utils import timezone

TRIGGER_EVENTS = [
    ("choose_click", "CHOOSE_CLICK"),
    ("start_click", "START_CLICK"),
    ("ok_completed_click", "OK_COMPLETED_CLICK"),
    ("play_click", "PLAY_CLICK"),
    ("back_click", "BACK_CLICK"),
    ("ok_close_click", "OK_CLOSE_CLICK"),
    ("grant_permission_click", "GRANT_PERMISSION_CLICK"),
    ("choose_answer_quiz_click", "CHOOSE_ANSWER_QUIZ_CLICK"),
]


class ActivityEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    fqid = models.CharField(max_length=128)
    activity_id = models.ForeignKey(
        "activities.Activity", on_delete=models.CASCADE, db_column="activity_id"
    )
    activity_log_id = models.ForeignKey(
        "users.ActivityLog",
        on_delete=models.CASCADE,
        db_column="activity_log_id",
        null=True,
        blank=True,
    )
    # Activity log can be empty if the fqid happen before play activity
    # Fqid without activity_log_id:
    # page.activities
    # page.activities.[type activity]
    # page.activity.[type activity].[slug activity]
    # TODO: validation of type and slug activity in ETL process for performance
    # Fqid with activity_log_id:
    # popup.main.page.activity.[type activity].[slug activity]
    # popup.close.page.activity.[type activity].[slug activity]
    # popup.complete.page.activity.[type activity].[slug activity]
    # popup.quiz.page.activity.reading.[slug reading activity]
    # popup.cameraaccess.page.activity.[type activity].[slug activity]
    event = models.CharField(choices=TRIGGER_EVENTS, max_length=100)
    issue_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"[🏃 {self.activity_id}]" + f"[🪵 {self.activity_log_id}]"

    class Meta:
        db_table = "logger_activity_events"

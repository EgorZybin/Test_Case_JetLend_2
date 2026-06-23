from django.db import models


class MailingRecord(models.Model):
    class Status(models.TextChoices):
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    external_id = models.CharField(max_length=255, unique=True, db_index=True)
    user_id = models.CharField(max_length=64)
    email = models.EmailField()
    subject = models.CharField(max_length=500)
    message = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices)
    error_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.external_id} -> {self.email}"

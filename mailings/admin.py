from django.contrib import admin

from mailings.models import MailingRecord


@admin.register(MailingRecord)
class MailingRecordAdmin(admin.ModelAdmin):
    list_display = (
        "external_id",
        "user_id",
        "email",
        "subject",
        "status",
        "created_at",
        "sent_at",
    )
    list_filter = ("status",)
    search_fields = ("external_id", "email", "user_id")
    readonly_fields = ("created_at", "sent_at")

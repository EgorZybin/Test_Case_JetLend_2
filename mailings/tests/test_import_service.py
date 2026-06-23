from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import TestCase, override_settings
from openpyxl import Workbook

from mailings.models import MailingRecord
from mailings.services.import_service import MailingImportService
from mailings.tests.helpers import build_xlsx


@override_settings(MAILING_SEND_DELAY_RANGE=(0, 0))
class MailingImportServiceTests(TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

    def _import_file(self, rows):
        file_path = Path(self.temp_dir.name) / "mailings.xlsx"
        build_xlsx(file_path, rows)
        return MailingImportService(file_path).run()

    @patch("mailings.services.import_service.send_email")
    def test_import_creates_records(self, mock_send_email):
        result = self._import_file(
            [
                {
                    "external_id": "ext-1",
                    "user_id": "42",
                    "email": "one@example.com",
                    "subject": "Subject 1",
                    "message": "Message 1",
                },
                {
                    "external_id": "ext-2",
                    "user_id": "43",
                    "email": "two@example.com",
                    "subject": "Subject 2",
                    "message": "Message 2",
                },
            ]
        )

        self.assertEqual(result.processed, 2)
        self.assertEqual(result.created, 2)
        self.assertEqual(result.skipped, 0)
        self.assertEqual(result.errors, 0)
        self.assertEqual(MailingRecord.objects.count(), 2)
        self.assertEqual(mock_send_email.call_count, 2)

    @patch("mailings.services.import_service.send_email")
    def test_duplicate_external_id_is_skipped(self, mock_send_email):
        MailingRecord.objects.create(
            external_id="ext-1",
            user_id="1",
            email="existing@example.com",
            subject="Old",
            message="Old message",
            status=MailingRecord.Status.SENT,
        )

        result = self._import_file(
            [
                {
                    "external_id": "ext-1",
                    "user_id": "42",
                    "email": "one@example.com",
                    "subject": "Subject",
                    "message": "Message",
                }
            ]
        )

        self.assertEqual(result.processed, 1)
        self.assertEqual(result.created, 0)
        self.assertEqual(result.skipped, 1)
        self.assertEqual(result.errors, 0)
        mock_send_email.assert_not_called()

    @patch("mailings.services.import_service.send_email")
    def test_invalid_email_is_counted_as_error(self, mock_send_email):
        result = self._import_file(
            [
                {
                    "external_id": "ext-bad",
                    "user_id": "42",
                    "email": "not-an-email",
                    "subject": "Subject",
                    "message": "Message",
                }
            ]
        )

        self.assertEqual(result.processed, 1)
        self.assertEqual(result.created, 0)
        self.assertEqual(result.skipped, 0)
        self.assertEqual(result.errors, 1)
        self.assertEqual(MailingRecord.objects.count(), 0)
        mock_send_email.assert_not_called()

    @patch("mailings.services.import_service.send_email")
    def test_missing_required_field_is_counted_as_error(self, mock_send_email):
        file_path = Path(self.temp_dir.name) / "invalid.xlsx"
        build_xlsx(
            file_path,
            [
                {
                    "external_id": "ext-1",
                    "user_id": "42",
                    "email": "one@example.com",
                    "subject": "",
                    "message": "Message",
                }
            ],
        )

        result = MailingImportService(file_path).run()

        self.assertEqual(result.errors, 1)
        mock_send_email.assert_not_called()

    @patch(
        "mailings.services.import_service.send_email",
        side_effect=RuntimeError("smtp down"),
    )
    def test_send_failure_marks_record_failed(self, mock_send_email):
        result = self._import_file(
            [
                {
                    "external_id": "ext-fail",
                    "user_id": "42",
                    "email": "one@example.com",
                    "subject": "Subject",
                    "message": "Message",
                }
            ]
        )

        record = MailingRecord.objects.get(external_id="ext-fail")
        self.assertEqual(record.status, MailingRecord.Status.FAILED)
        self.assertIn("smtp down", record.error_message)
        self.assertEqual(result.errors, 1)
        self.assertEqual(result.created, 0)

    def test_missing_file_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            MailingImportService("/tmp/does-not-exist.xlsx").run()

    def test_missing_columns_raise_error(self):
        file_path = Path(self.temp_dir.name) / "bad-header.xlsx"
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(["external_id"])
        sheet.append(["ext-1"])
        workbook.save(file_path)

        with self.assertRaises(ValueError) as ctx:
            MailingImportService(file_path).run()

        self.assertIn("Missing required columns", str(ctx.exception))

    @patch("mailings.services.import_service.send_email")
    def test_reimport_skips_existing_records(self, mock_send_email):
        rows = [
            {
                "external_id": "ext-1",
                "user_id": "42",
                "email": "one@example.com",
                "subject": "Subject",
                "message": "Message",
            }
        ]

        first = self._import_file(rows)
        second = self._import_file(rows)

        self.assertEqual(first.created, 1)
        self.assertEqual(second.created, 0)
        self.assertEqual(second.skipped, 1)
        self.assertEqual(mock_send_email.call_count, 1)

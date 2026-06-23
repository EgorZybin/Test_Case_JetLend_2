from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings

from mailings.tests.helpers import build_xlsx


@override_settings(MAILING_SEND_DELAY_RANGE=(0, 0))
class ImportMailingsCommandTests(TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

    @patch("mailings.services.import_service.send_email")
    def test_command_prints_summary(self, mock_send_email):
        file_path = Path(self.temp_dir.name) / "mailings.xlsx"
        build_xlsx(
            file_path,
            [
                {
                    "external_id": "ext-1",
                    "user_id": "1",
                    "email": "user@example.com",
                    "subject": "Hello",
                    "message": "World",
                }
            ],
        )

        output = StringIO()
        call_command("import_mailings", str(file_path), stdout=output)

        content = output.getvalue()
        self.assertIn("Processed rows: 1", content)
        self.assertIn("Created records: 1", content)
        self.assertIn("Skipped records: 0", content)
        self.assertIn("Error rows: 0", content)
        mock_send_email.assert_called_once()

    def test_command_reports_missing_file(self):
        with self.assertRaisesMessage(Exception, "File not found"):
            call_command("import_mailings", "/tmp/missing-file.xlsx")

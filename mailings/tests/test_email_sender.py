from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from mailings.services.email_sender import send_email


@override_settings(MAILING_SEND_DELAY_RANGE=(1, 1))
class SendEmailTests(SimpleTestCase):
    @patch("mailings.services.email_sender.logger")
    def test_send_email_logs_message(self, mock_logger):
        sleeps: list[float] = []

        send_email(
            email="user@example.com",
            subject="Hello",
            message="Body",
            sleep_fn=sleeps.append,
        )

        self.assertEqual(sleeps, [1.0])
        mock_logger.info.assert_called_once()

    @patch("mailings.services.email_sender.logger")
    @patch("mailings.services.email_sender.random.randint", return_value=15)
    def test_send_email_uses_random_delay(self, mock_randint, mock_logger):
        sleeps: list[float] = []

        send_email(
            email="user@example.com",
            subject="Hello",
            message="Body",
            sleep_fn=sleeps.append,
        )

        mock_randint.assert_called_once_with(1, 1)
        self.assertEqual(sleeps, [15.0])
        mock_logger.info.assert_called_once()

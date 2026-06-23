from django.core.management.base import BaseCommand, CommandError

from mailings.services.import_service import MailingImportService


class Command(BaseCommand):
    help = "Import mailings from an XLSX file and send emails."

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path",
            type=str,
            help="Path to the XLSX file with mailing data.",
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]

        try:
            result = MailingImportService(file_path).run()
        except (FileNotFoundError, ValueError) as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(
                "\n".join(
                    [
                        "Import finished.",
                        f"Processed rows: {result.processed}",
                        f"Created records: {result.created}",
                        f"Skipped records: {result.skipped}",
                        f"Error rows: {result.errors}",
                    ]
                )
            )
        )

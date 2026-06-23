#!/usr/bin/env python
"""Generate a sample XLSX file for manual import testing."""

from pathlib import Path

from openpyxl import Workbook

SAMPLE_ROWS = [
    {
        "external_id": "demo-001",
        "user_id": "101",
        "email": "alice@example.com",
        "subject": "Welcome",
        "message": "Hello Alice!",
    },
    {
        "external_id": "demo-002",
        "user_id": "102",
        "email": "bob@example.com",
        "subject": "Reminder",
        "message": "Hello Bob!",
    },
]


def main() -> None:
    output = Path("samples/mailings.sample.xlsx")
    output.parent.mkdir(parents=True, exist_ok=True)

    workbook = Workbook()
    sheet = workbook.active
    headers = ["external_id", "user_id", "email", "subject", "message"]
    sheet.append(headers)

    for row in SAMPLE_ROWS:
        sheet.append([row[column] for column in headers])

    workbook.save(output)
    print(f"Created {output}")


if __name__ == "__main__":
    main()

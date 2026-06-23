from io import BytesIO
from pathlib import Path

from openpyxl import Workbook


def build_xlsx(path: Path, rows: list[dict[str, str]]) -> Path:
    workbook = Workbook()
    sheet = workbook.active
    headers = ["external_id", "user_id", "email", "subject", "message"]
    sheet.append(headers)

    for row in rows:
        sheet.append([row.get(column, "") for column in headers])

    workbook.save(path)
    return path


def build_xlsx_bytes(rows: list[dict[str, str]]) -> bytes:
    buffer = BytesIO()
    workbook = Workbook()
    sheet = workbook.active
    headers = ["external_id", "user_id", "email", "subject", "message"]
    sheet.append(headers)

    for row in rows:
        sheet.append([row.get(column, "") for column in headers])

    workbook.save(buffer)
    return buffer.getvalue()

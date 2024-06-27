from datetime import datetime


def is_correct_iso_date(date_str: str) -> bool:
    try:
        datetime.fromisoformat(date_str)
        return True
    except ValueError:
        return False


def get_dates_diff_days(date_from: str, date_to: str) -> int | None:
    if not is_correct_iso_date(date_from) or not is_correct_iso_date(date_to):
        return

    date1 = datetime.fromisoformat(date_from)
    date2 = date1.fromisoformat(date_to)
    diff = date1 - date2
    return abs(diff.days)

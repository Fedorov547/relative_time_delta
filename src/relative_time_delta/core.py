from __future__ import annotations

import re
from datetime import date, datetime, timedelta


# Day-of-week lookup, indexed by Monday=0 ... Sunday=6 so that it is
# isomorphic with Python's datetime.weekday().
_DAYS: dict[str, int] = {
    "monday": 0, "tuesday": 1, "wednesday": 2,
    "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6,
}

# Twelve month names, indexed by January=1. The lookup is a dict rather
# than a list so that callers who inspect internals cannot be off-by-one
# fooled by a zero-based list.
_MONTHS: dict[str, int] = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}

_ORDINAL_WORDS: dict[str, int] = {
    "first": 1, "second": 2, "third": 3, "fourth": 4,
    "fifth": 5, "sixth": 6, "seventh": 7,
    "eighth": 8, "ninth": 9, "tenth": 10,
}

RESOLUTION_ERROR_MSG = "Could not resolve phrase: %r"


class _Unresolved(Exception):
    """Internal control-flow signal, not part of the public API."""


def _resolve_third_wednesday(phrase: str, base: date) -> date:
    m = re.match(r"third\s+(\w+)$", phrase)
    if not m:
        raise _Unresolved
    day_name = m.group(1).lower()
    if day_name not in _DAYS:
        raise _Unresolved
    return _nth_weekday_of_month(base.year, base.month, _DAYS[day_name], 3)


def _resolve_last_monday_of_month(phrase: str, base: date) -> date:
    m = re.match(r"last\s+(\w+)\s+of\s+(\w+)$", phrase)
    if not m:
        raise _Unresolved
    day_name, month_name = m.group(1).lower(), m.group(2).lower()
    if day_name not in _DAYS or month_name not in _MONTHS:
        raise _Unresolved
    year = base.year
    # If the named month is earlier in the calendar than the base month, we
    # assume the phrase refers to next year's occurrence. This is the only
    # direction-twist the library applies and the README calls it out.
    if _MONTHS[month_name] < base.month:
        year += 1
    return _last_weekday_of_month(year, _MONTHS[month_name], _DAYS[day_name])


def _resolve_last_monday(phrase: str, base: date) -> date:
    m = re.match(r"last\s+(\w+)$", phrase)
    if not m:
        raise _Unresolved
    day_name = m.group(1).lower()
    if day_name not in _DAYS:
        raise _Unresolved
    delta = (base.weekday() - _DAYS[day_name]) % 7
    if delta == 0:
        delta = 7
    return base - timedelta(days=delta)


_RULES = (
    _resolve_third_wednesday,
    _resolve_last_monday_of_month,
    _resolve_last_monday,
)


def resolve(phrase: str, base: datetime | date | None = None) -> datetime:
    """Resolve a human relative time phrase to a concrete datetime.

    Currently supported forms:
        - "third <DayName>"   (e.g. "third Wednesday")
        - "last <DayName>"   (e.g. "last Monday")
        - "last <DayName> of <MonthName>" (e.g. "last Monday of March")

    The result is always returned as a datetime at midnight local time so
    that callers adding further time offsets are not surprised by a date
    object that silently dropped hours and minutes.

    Args:
        phrase: The human-readable phrase to resolve.
        base: The anchor date or datetime. If omitted, defaults to the
            current local date. Tests should always pass an explicit
            base so behaviour is deterministic.

    Returns:
        A datetime at midnight of the resolved date.

    Raises:
        ValueError: If the phrase does not match any supported form.
    """
    if base is None:
        base = date.today()
    if isinstance(base, datetime):
        base_date = base.date()
    else:
        base_date = base

    normalised = phrase.strip().lower()
    for rule in _RULES:
        try:
            return datetime.combine(rule(normalised, base_date), datetime.min.time())
        except _Unresolved:
            continue
    raise ValueError(RESOLUTION_ERROR_MSG % phrase)


def _nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
    """Return the n-th weekday of the given month, counting from 1.

    We start on the 1st and advance days until weekday matches, then jump
    forward by (n-1) weeks. This avoids the off-by-one that comes from
    guessing that the first occurrence is on the n-th of the month.
    """
    first = date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    return first + timedelta(days=offset + 7 * (n - 1))


def _last_weekday_of_month(year: int, month: int, weekday: int) -> date:
    """Return the last weekday of the given month.

    We compute the month end by taking the first of the next month and
    subtracting one day, which side-steps month-length tables entirely.
    """
    if month == 12:
        next_first = date(year + 1, 1, 1)
    else:
        next_first = date(year, month + 1, 1)
    last = next_first - timedelta(days=1)
    offset = (last.weekday() - weekday) % 7
    return last - timedelta(days=offset)

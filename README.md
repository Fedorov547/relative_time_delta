# relative_time_delta

Resolves relative time phrases like "third Wednesday" or "last Monday of March" into concrete datetime objects, anchored to a base date you provide.

```python
from datetime import date
from relative_time_delta import resolve

base = date(2024, 6, 5)
print(resolve("third Wednesday", base))        # 2024-06-19 00:00:00
print(resolve("last Monday of March", base))    # 2024-03-25 00:00:00
print(resolve("last Tuesday", base))           # 2024-06-04 00:00:00
```

## Why this exists

Date libraries that ship with the standard library are good at arithmetic and bad at the way people actually speak. Schedulers and human-facing reminders frequently want "the third Wednesday of the month" or "the last Monday of March," phrases that require weekday arithmetic over a calendar grid. This library provides a small resolver for those forms without pulling in a third-party date framework.

The trade-off is scope: only three forms are supported ("nth <Day>", "last <Day>", "last <Day> of <Month>"). If you need "two weeks from next Thursday" or timezone-aware rolling, write the arithmetic yourself; this library will not grow a mini-DSL.

## Edge cases worth knowing

- "last <Day>" on a day of the same weekday returns the previous week, not the current day. This matches the common reading that "last" implies a completed occurrence.
- For "last <Day> of <Month>", if the named month is earlier in the year than the base month, the library assumes the following year's occurrence. Pass a base in the correct year if you need otherwise.
- The result is always a datetime at midnight. Hours and minutes from the base are discarded.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.


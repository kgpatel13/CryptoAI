from __future__ import annotations

import unittest

from app.dashboard.time_format import (
    format_eastern_datetime,
    localize_timestamps,
    localize_timestamps_in_text,
)


class DashboardTimeFormatTests(unittest.TestCase):
    def test_formats_utc_iso_as_eastern_wall_time(self) -> None:
        self.assertEqual(
            format_eastern_datetime("2026-06-30T17:51:00Z"),
            "30-Jun-2026 1:51 PM",
        )

    def test_localizes_timestamp_fields(self) -> None:
        payload = {"generated_at": "2026-06-30T17:51:00Z", "status": "OK"}

        self.assertEqual(
            localize_timestamps(payload),
            {"generated_at": "30-Jun-2026 1:51 PM", "status": "OK"},
        )

    def test_localizes_iso_values_inside_text(self) -> None:
        self.assertEqual(
            localize_timestamps_in_text("Generated at 2026-06-30T17:51:00Z."),
            "Generated at 30-Jun-2026 1:51 PM.",
        )


if __name__ == "__main__":
    unittest.main()

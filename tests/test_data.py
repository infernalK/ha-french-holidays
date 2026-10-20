"""Tests for the pure data helpers (no Home Assistant runtime needed)."""

from __future__ import annotations

from datetime import date

from custom_components.french_holidays.data import (
    FrenchHolidayPeriod,
    get_period_extra_attributes,
    period_from_dict,
    period_to_dict,
)


def _period() -> FrenchHolidayPeriod:
    return FrenchHolidayPeriod(
        summary="Vacances de Noël",
        start=date(2026, 12, 20),
        end=date(2027, 1, 4),
        uid="zone-c-vacances-de-noel-2026-2027",
        zone="Zone C",
        year="2026-2027",
    )


def test_period_round_trips_through_dict() -> None:
    period = _period()

    restored = period_from_dict(period_to_dict(period))

    assert restored == period


def test_period_to_dict_serializes_dates_as_iso_strings() -> None:
    data = period_to_dict(_period())

    assert data["start"] == "2026-12-20"
    assert data["end"] == "2027-01-04"


def test_get_period_extra_attributes_computes_derived_fields() -> None:
    attrs = get_period_extra_attributes(_period())

    assert attrs["duration_days"] == 16
    assert attrs["start_date_short"] == "20 déc"
    assert attrs["end_date_short"] == "04 janv"
    assert attrs["zone"] == "Zone C"
    assert attrs["année_scolaire"] == "2026-2027"

"""Тесты функций модуля venues."""

from venues import (
    add_venue,
    check_venue_capacity,
    filter_venues_by_capacity,
    find_venues,
    sort_venues,
)


def test_add_venue():
    venues = []
    add_venue(venues, "Октябрьский", "СПб", 1500)
    assert len(venues) == 1
    assert venues[0]["capacity"] == 1500


def test_find_venues_by_query():
    venues = []
    add_venue(venues, "Октябрьский", "СПб", 1500)
    add_venue(venues, "Крокус", "Москва", 6000)
    found = find_venues(venues, "октябрь")
    assert len(found) == 1
    assert found[0]["name"] == "Октябрьский"


def test_check_venue_capacity_true():
    venues = []
    add_venue(venues, "Октябрьский", "СПб", 1500)
    assert check_venue_capacity(venues, 1, 1000)


def test_check_venue_capacity_false():
    venues = []
    add_venue(venues, "Октябрьский", "СПб", 1500)
    assert not check_venue_capacity(venues, 1, 2000)


def test_filter_venues_by_capacity():
    venues = []
    add_venue(venues, "Октябрьский", "СПб", 1500)
    add_venue(venues, "Крокус", "Москва", 6000)
    filtered = filter_venues_by_capacity(venues, 3000)
    assert len(filtered) == 1
    assert filtered[0]["name"] == "Крокус"


def test_sort_venues():
    venues = []
    add_venue(venues, "Крокус", "Москва", 6000)
    add_venue(venues, "Октябрьский", "СПб", 1500)
    ordered = sort_venues(venues)
    assert ordered[0]["capacity"] == 1500
    assert ordered[-1]["capacity"] == 6000

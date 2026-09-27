from models import Venue
from models.venues import (
    add_venue,
    check_venue_capacity,
    filter_venues_by_capacity,
    find_venues,
    sort_venues,
)


def test_venue_creation():
    venue = Venue(1, "Октябрьский", "СПб", 1500)
    assert venue.id == 1
    assert venue.capacity == 1500


def test_venue_is_suitable_for():
    venue = Venue(1, "Октябрьский", "СПб", 1500)
    assert venue.is_suitable_for(1000)
    assert not venue.is_suitable_for(2000)


def test_venue_validate_capacity():
    assert Venue.validate_capacity(30)
    assert not Venue.validate_capacity(0)
    assert not Venue.validate_capacity(-5)


def test_venue_str():
    venue = Venue(1, "Октябрьский", "СПб", 1500)
    assert "Октябрьский" in str(venue)
    assert "1500" in str(venue)


def test_venue_from_data():
    data = {
        "id": 2,
        "name": "Крокус",
        "address": "Москва",
        "capacity": 6000,
    }
    venue = Venue.from_data(data)
    assert venue.id == 2
    assert venue.capacity == 6000


def test_add_venue():
    venues = []
    add_venue(venues, "Октябрьский", "СПб", 1500)
    assert len(venues) == 1


def test_find_venues_by_query():
    venues = []
    add_venue(venues, "Октябрьский", "СПб", 1500)
    add_venue(venues, "Крокус", "Москва", 6000)
    found = find_venues(venues, "октябрь")
    assert len(found) == 1
    assert found[0].name == "Октябрьский"


def test_check_venue_capacity():
    venues = []
    add_venue(venues, "Октябрьский", "СПб", 1500)
    assert check_venue_capacity(venues, 1, 1000)
    assert not check_venue_capacity(venues, 1, 2000)


def test_filter_venues_by_capacity():
    venues = []
    add_venue(venues, "Октябрьский", "СПб", 1500)
    add_venue(venues, "Крокус", "Москва", 6000)
    filtered = filter_venues_by_capacity(venues, 3000)
    assert len(filtered) == 1
    assert filtered[0].name == "Крокус"


def test_sort_venues():
    venues = []
    add_venue(venues, "Крокус", "Москва", 6000)
    add_venue(venues, "Октябрьский", "СПб", 1500)
    ordered = sort_venues(venues)
    assert ordered[0].capacity == 1500
    assert ordered[-1].capacity == 6000

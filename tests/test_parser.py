import pytest
from datetime import datetime, timedelta
from parser import parse

def date_only(dt):
    return dt.date() if dt else None

def test_next_week():
    today = datetime(2025, 5, 31)  # Saturday
    expected = datetime(2025, 6, 2).date()  # Next Monday
    result, _ = parse("next week", today)
    assert date_only(result) == expected

def test_next_week_tuesday():
    today = datetime(2025, 5, 31)  # Saturday
    expected = datetime(2025, 6, 3).date()
    result, _ = parse("next week tuesday", today)
    assert date_only(result) == expected

def test_in_a_day():
    today = datetime(2025, 5, 31)  # Saturday
    expected = datetime(2025, 6, 1).date()
    result, _ = parse("in a day", today)
    assert date_only(result) == expected

def test_in_two_days():
    today = datetime(2025, 5, 31)  # Saturday
    expected = datetime(2025, 6, 2).date()
    result, _ = parse("in 2 days", today)
    assert date_only(result) == expected

def test_in_a_month():
    today = datetime(2025, 5, 31)  # Saturday
    expected = datetime(2025, 6, 30).date()
    result, _ = parse("in a month", today)
    assert date_only(result) == expected

def test_in_two_months():
    today = datetime(2025, 5, 31)  # Saturday
    expected = datetime(2025, 7, 31).date()
    result, _ = parse("in 2 months", today)
    assert date_only(result) == expected

def test_in_a_week_monday():
    today = datetime(2025, 5, 31)  # Saturday
    expected = datetime(2025, 6, 9).date() # we mean next next monday!
    result, _ = parse("in a week monday", today)
    assert date_only(result) == expected

def test_in_next_week_monday():
    today = datetime(2025, 5, 31)  # Saturday
    expected = datetime(2025, 6, 2).date() # we mean next monday!
    result, _ = parse("next week monday", today)
    assert date_only(result) == expected

def test_monday_next_week():
    today = datetime(2025, 5, 31)  # Saturday
    expected = datetime(2025, 6, 2).date() # we mean next monday!
    result, _ = parse("monday next week", today)
    assert date_only(result) == expected

def test_next_tuesday():
    today = datetime(2025, 5, 31)  # Saturday
    expected = datetime(2025, 6, 3).date()
    result, _ = parse("next tuesday", today)
    assert date_only(result) == expected

def test_tuesday():
    today = datetime(2025, 5, 31)  # Saturday
    expected = datetime(2025, 6, 3).date()
    result, _ = parse("tuesday", today)
    assert date_only(result) == expected

def test_next_next_tuesday():
    today = datetime(2025, 5, 31)  # Saturday
    expected = datetime(2025, 6, 10).date()
    result, _ = parse("next next tuesday", today)
    assert date_only(result) == expected

def test_at_time():
    today = datetime(2025, 5, 31, 0, 0)  # Saturday
    expected = datetime(2025, 6, 1, 5, 30)  # Next day at 5:30 AM
    result, _ = parse("next day at 530", today)
    assert result == expected

def test_at_time_space():
    today = datetime(2025, 5, 31, 0, 0)  # Saturday
    expected = datetime(2025, 6, 1, 5, 45)  # Next day at 5:30 AM
    result, _ = parse("next day at 5 45", today)
    assert result == expected

def test_at_time_today():
    today = datetime(2025, 5, 31, 0, 0)  # Saturday
    expected = datetime(2025, 5, 31, 6, 30)  # Next day at 5:30 AM
    result, _ = parse("at 6:30", today)
    assert result == expected
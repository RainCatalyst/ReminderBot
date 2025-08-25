from datetime import date, timedelta, datetime
from dateutil import relativedelta
import re

days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

class TokenStream:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.precise = False
        self.any_info = False
        self.weekday = False

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self):
        token = self.peek()
        if token is not None:
            self.pos += 1
        return token

    def match(self, *expected):
        if self.peek() in expected:
            return self.consume()
        return None

    def expect(self, expected):
        if self.peek() != expected:
            raise ValueError(f"Expected '{expected}', found '{self.peek()}'")
        return self.consume()

    def remaining(self):
        return self.tokens[self.pos:]

def parse(text: str, today: datetime = datetime.now()) -> date:
    try:
        tokens = TokenStream(text.lower().split())
        date, text = _parse_expression(tokens, today)

        return (date, text, tokens.precise)
    except:
        return None

def _parse_expression(tokens: TokenStream, current_date: date) -> date:
    result_date = current_date
    non_tokens = []
    using_nontokens = False

    while tokens.peek():
        token = tokens.consume()
        if tokens.any_info and using_nontokens:
            non_tokens.append(token)
            continue
        if token == "next":
            tokens.any_info = True
            if using_nontokens:
                using_nontokens = False
            # Case: next X
            result_date = _parse_next(tokens, result_date)
        elif token == "tomorrow":
            tokens.any_info = True
            if using_nontokens:
                using_nontokens = False
            result_date = result_date + timedelta(days = 1)
        elif (weekday := _weekday_to_int(token)) != -1:
            tokens.any_info = True
            if using_nontokens:
                using_nontokens = False
            # Case: monday (just weekday I guess)
            if _is_weekday_next_week(result_date, weekday):
                tokens.weekday = True
            result_date = _get_next_weekday(result_date, weekday)
        elif token == "in":
            tokens.any_info = True
            if using_nontokens:
                using_nontokens = False
            # Case: in X
            result_date = _parse_in(tokens, result_date)
        elif token == "at":
            tokens.any_info = True
            if using_nontokens:
                using_nontokens = False
            # Case: at X
            result_date = _parse_at(tokens, result_date)
        elif _str_to_int(token) != None:
            # Case: 530 etc, assuming time
            if using_nontokens:
                using_nontokens = False
            tokens.any_info = True
            result_date = _parse_at(tokens, result_date, existing_token=token)
        else:
            if using_nontokens:
                non_tokens.append(token)
            elif len(non_tokens) == 0:
                using_nontokens = True
                non_tokens.append(token)
    
    if not tokens.any_info:
        result_date = None
    return result_date, ' '.join(non_tokens)
    
def _parse_next(tokens: TokenStream, current_date: date) -> date:
    token_next = tokens.consume()

    offset = 0
    while token_next == "next":
        token_next = tokens.consume()
        offset += 1
    if token_next == "week":
        # Case: next week
        # Default to monday
        if tokens.weekday:
            return current_date + timedelta(weeks = offset)
        return current_date + timedelta(days = 7 - current_date.weekday()) + timedelta(weeks = offset)
    if token_next == "day":
        # Case: next day (tomorrow)
        return current_date + timedelta(days = 1 * (offset + 1))
    if token_next == "month":
        # Case: next month (should work but im not sure)
        return current_date + relativedelta.relativedelta(months=1 * (offset + 1), day=1)
    if (to_weekday := _weekday_to_int(token_next)) != -1:
        # Case: next monday/tuesday etc
        return _get_next_weekday(current_date, to_weekday) + timedelta(weeks = offset)
    # Handle error here!
    return current_date

def _parse_in(tokens: TokenStream, current_date: date) -> date:
    token_next = tokens.consume()
    # Skip the "a" or "an"
    if token_next == "a" or token_next == "an":
        token_next = tokens.consume()
    
    # Default to offset of 1 (1 day / month etc)
    offset = 1
    if (new_offset := _str_to_int(token_next)) != None:
        # In X hours/days/weeks/months
        offset = new_offset
        token_next = tokens.consume()
    if _matches_plural(token_next, "minute"):
        # Case: in X minutes
        tokens.precise = True
        return current_date + timedelta(minutes = 1 * offset)
    if _matches_plural(token_next, "hour"):
        # Case: in X hours
        tokens.precise = True
        return current_date + timedelta(hours = 1 * offset)
    if _matches_plural(token_next, "day"):
        # Case: in X days
        return current_date + timedelta(days = 1 * offset)
    if _matches_plural(token_next, "week"):
        # Case: in X weeks
        if tokens.weekday:
            offset -= 1
        return current_date + timedelta(days = 7 * offset)
    if _matches_plural(token_next, "month"):
        # Case: in X months (idk how this works we just trust it does)
        return current_date + relativedelta.relativedelta(months = 1 * offset)
    
def _parse_at(tokens: TokenStream, current_date: date, existing_token: str = None) -> date:
    token_next = existing_token
    if not token_next:
        token_next = tokens.consume()
    if _str_to_int(token_next.replace(':', '')) == None:
        # Error
        return current_date
    if _str_to_int(tokens.peek()) != None:
        # Next token is also number (assuming minutes)
        # Merge it to hours
        token_next += tokens.consume()
    
    if (data := _str_to_hours_minutes(token_next)) != None:
        hours, minutes = data
        tokens.precise = True
        return current_date.replace(hour=hours, minute=minutes)
    
    return False

def _weekday_to_int(day: str):
    if len(day) < 3:
        return -1
    for idx, test_day in enumerate(days):
        if day == test_day:
            return idx
        # Handle cases like 'mon' for monday, but 'day' shouldn't refer to any specific day
        if day in test_day.replace('day', ''):
            return idx
    return -1

def _get_next_weekday(current_date: date, target_weekday: int):
    return current_date + timedelta(days = (target_weekday - current_date.weekday() + 7) % 7)

def _is_weekday_next_week(current_date: date, target_weekday: int):
    return target_weekday < current_date.weekday()

def _matches_plural(token: str, match: str) -> bool:
    if token == match or token[:-1] == match:
        return True
    return False

def _str_to_int(token: str):
    try:
        return int(token)
    except:
        return None
    
def _str_to_hours_minutes(time_str: str):
    # Match HH or HHMM or HH:MM
    match_colon = re.match(r'^(\d{1,2}):(\d{2})$', time_str)
    match_compact = re.match(r'^(\d{1,2})(\d{2})$', time_str)
    match_hour = re.match(r'^(\d{1,2})$', time_str)

    if match_colon:
        hour = int(match_colon.group(1))
        minute = int(match_colon.group(2))
        return (hour, minute)
    elif match_compact:
        hour = int(match_compact.group(1))
        minute = int(match_compact.group(2))
        return (hour, minute)
    elif match_hour:
        hour = int(match_hour.group(1))
        return (hour, 0)

    return None
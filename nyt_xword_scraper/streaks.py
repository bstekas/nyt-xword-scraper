"""Functions to query data from NYT crossword endpoints."""

import aiohttp

API_ROOT = "http://www.nytimes.com"
STATS_STREAKS = "/svc/crosswords/v3/{UID}/stats-and-streaks.json"
MINI_STATS = "svc/crosswords/v3/{UID}/mini-stats.json"


def fetch_stats_streaks(session: aiohttp.ClientSession, uid: int) -> dict:
    """Fetch streak and fastest time data for daily crossword.

    Args:
        session (aiohttp.ClientSession): session for sending the request. Must include NYT user cookie.
        uid (int): id of the logged in user.

    Returns:
        dict: user's streak and stat data
    """
    payload = {"date_start": "1988-01-01", "start_on_monday": True}
    resp = session.get(STATS_STREAKS.format(UID=uid), params=payload).json()
    return resp.get("results")


def fetch_mini_stats(session: aiohttp.ClientSession, uid: int) -> dict:
    """Fetch streak and fastest time data for daily crossword.

    Args:
        session (aiohttp.ClientSession): session for sending the request. Must include NYT user cookie.
        uid (int): id of the logged in user.

    Returns:
        dict: user's streak and stat data
    """
    payload = {"date_start": "2014-01-01", "start_on_monday": True}
    resp = session.get(STATS_STREAKS.format(UID=uid), params=payload).json()
    return resp.get("results")

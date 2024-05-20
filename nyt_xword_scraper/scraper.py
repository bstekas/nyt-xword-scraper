"""Scrape crossword solve times asynchronously."""

import asyncio
import os
from collections.abc import Iterator
from datetime import datetime, timedelta

import aiohttp
import pandas as pd
from tqdm.asyncio import tqdm

from nyt_xword_scraper.puzzles import fetch_puzzle_data, fetch_puzzle_detail

API_ROOT = "http://www.nytimes.com"
COOKIE_PING = "/svc/crosswords/v6/game/21830.json"
ENV_COOKIE = os.environ["NYT_COOKIE"]

HOST_LIMIT = 20
MAX_RETRIES = 3
BATCH_SIZE = 20

DATE_FORMAT = "%Y-%m-%d"

START_DATES = {
    "mini": datetime(2014, 8, 21),
    "daily": datetime(1993, 11, 21),
    "bonus": datetime(1997, 2, 1),
}


def _get_batch_ends(
    puzzle_type: str, start_date: str, end_date: str
) -> tuple[Iterator[tuple[str, str]], int]:
    """Get start and end dates for each batch.

    For daily and mini, each batch is one calendar month. For bonus, one calendar year.
    """
    period = {"daily": "M", "mini": "M", "bonus": "Y"}

    m_start = (
        pd.date_range(start_date, end_date, freq=period[puzzle_type] + "S")
        .strftime(DATE_FORMAT)
        .to_list()
    )
    m_end = (
        pd.date_range(start_date, end_date, freq=period[puzzle_type] + "E")
        .strftime(DATE_FORMAT)
        .to_list()
    )

    if period[puzzle_type] == "Y":
        if not pd.to_datetime(start_date).is_year_start:
            m_start.insert(0, start_date)
        if not pd.to_datetime(end_date).is_year_end:
            m_end.append(end_date)
    elif period[puzzle_type] == "M":
        if not pd.to_datetime(start_date).is_month_start:
            m_start.insert(0, start_date)
        if not pd.to_datetime(end_date).is_month_end:
            m_end.append(end_date)

    return zip(m_start, m_end), len(m_start)


async def _scrape(batches: Iterator[tuple[str, str]], puzzle_type: str, token: str):
    """Run asynchronous scrape for all batches."""
    puzzle_data = []

    async with aiohttp.ClientSession(
        API_ROOT,
        raise_for_status=True,
        connector=aiohttp.TCPConnector(limit_per_host=HOST_LIMIT),
        cookies={"NYT-S": token},
    ) as session:
        await session.get(COOKIE_PING)

        await tqdm.gather(
            *[
                _run_batch(puzzle_data, session, puzzle_type, start_date, end_date)
                for start_date, end_date in batches
            ]
        )

    return puzzle_data


async def _run_batch(
    puzzle_data: list,
    session: aiohttp.ClientSession,
    puzzle_type: str,
    batch_start: str,
    batch_end: str,
):
    """Run a single batch of puzzles between two dates."""
    info = await fetch_puzzle_data(session, puzzle_type, batch_start, batch_end)

    await tqdm.gather(
        *[fetch_puzzle_detail(session, puzzle) for puzzle in info],
        desc=f"Batch {batch_start} details",
        leave=False,
    )

    puzzle_data.extend(info)
    pass


def scrape(
    token: str,
    puzzle_type: str = "daily",
    start_date: str = (datetime.today() - timedelta(days=2)).strftime(DATE_FORMAT),
    end_date: str = datetime.today().strftime(DATE_FORMAT),
) -> list[dict]:
    """Pull all available information for puzzles published between two dates.

    Args:
        token (str, optional): Logged in users's NYT token.
        puzzle_type (str, optional): type of puzzle. Can be 'daily', 'mini', or 'bonus'.
            Defaults to "daily".
        start_date (str, optional): first publication day. Defaults to 2 days ago.
        end_date (str, optional): last publication day. Defaults to today.
    """
    start_datetime = datetime.strptime(start_date, DATE_FORMAT)

    if start_datetime < START_DATES[puzzle_type]:
        start_date = max(start_datetime, START_DATES[puzzle_type]).strftime(DATE_FORMAT)
        print(f"First {puzzle_type} available is {start_date}")

    batches, n_batches = _get_batch_ends(puzzle_type, start_date, end_date)
    print(
        "Getting solve stats from {0} until {1} in {2} batches".format(
            start_date, end_date, n_batches
        )
    )

    return asyncio.run(_scrape(batches, puzzle_type, token))

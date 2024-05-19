"""Functions to query data from NYT crossword endpoints."""

import json
from typing import Dict, Literal

import aiohttp

API_ROOT = "http://www.nytimes.com"
PUZZLE_INFO = "/svc/crosswords/v3/puzzles.json"
PUZZLE_DETAIL = "/svc/crosswords/v6/game/"


async def fetch_puzzle_data(
    session: aiohttp.ClientSession,
    puzzle_type: Literal["daily", "mini", "bonus"],
    start_date,
    end_date,
) -> dict:
    """Get high level information about a set of puzzles.

    Start and end dates must be in "%Y-%m-%d" format. Using one calendar month for the time range seems to work best, that is the view used on the website.

    Args:
        session (aiohttp.ClientSession): session for sending the request. Must include NYT user cookie.
        puzzle_type (str): type of puzzle to get data for. Can be `daily`, `mini`, or `bonus`.
        start_date (str): start date for batch of puzzles.
        end_date (str): end date for batch of puzzles.

    Returns:
        list[dict]: high level data about each puzzle.
    """
    payload = {
        "publish_type": puzzle_type,
        "sort_order": "asc",
        "sort_by": "print_date",
        "date_start": start_date,
        "date_end": end_date,
    }

    async with session.get(PUZZLE_INFO, params=payload) as overview_resp:

        puzzle_info = await overview_resp.text()
        return json.loads(puzzle_info).get("results")


async def fetch_puzzle_detail(session: aiohttp.ClientSession, puzzle: dict):
    """Get detailed information about solve times for a single puzzle.

    Updates the puzzle dictionary output by :py:func:`puzzles.get_puzzle_data()` with detailed user solve data.

    Args:
        session (aiohttp.ClientSession): session for sending the request. Must include NYT user cookie.
        puzzle (dict): high-level data for a single puzzle including `puzzle_id` field.

    Returns:
        dict: :py:data:`puzzle` dict with detailed data added
    """
    async with session.get(f"{PUZZLE_DETAIL}{puzzle['puzzle_id']}.json") as puzzle_resp:
        puzzle_detail = await puzzle_resp.text()
        puzzle_detail = json.loads(puzzle_detail)

        if "board" in puzzle_detail.keys():
            board = puzzle_detail.pop("board")
            puzzle_detail.update(parse_board_cells(board))

        puzzle.update(puzzle_detail)
        return puzzle


def parse_board_cells(board, fill_blank=None) -> Dict[str, list]:
    """Transform puzzle board data when available.

    Args:
        board (dict): contains `cells` object with list guesses and timestamps for each square in puzzle grid
        fill_blank (list, optional): how to fill blank squares. Defaults to `("-",0)` for guesses and timestamps respectively.

    Returns:
        dict: two lists of guesses and corresponding timestamps
    """
    if fill_blank is None:
        guess_fill, time_fill = ("-", 0)
    else:
        guess_fill, time_fill = fill_blank

    guess = []
    timestamp = []
    for square in board["cells"]:
        if "blank" in square.keys():
            guess.append(guess_fill)
            timestamp.append(time_fill)
        else:
            guess.append(square["guess"])
            timestamp.append(square["timestamp"])

    return {"board.guess": guess, "board.timestamp": timestamp}

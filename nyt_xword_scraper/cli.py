"""Command line interface for scraping."""

import os
from datetime import datetime, timedelta

import click
import dotenv
import pandas as pd

from nyt_xword_scraper.scraper import DATE_FORMAT, scrape

# from nyt_xword_scraper.streaks import fetch_stats_streaks

dotenv.load_dotenv()


@click.group()
@click.option(
    "-t",
    "--token",
    type=str,
    default=lambda: os.environ.get("NYT_COOKIE"),
    help="Logged in users's NYT token. Inferred from environment or .env if missing.",
)
@click.option(
    "-f",
    "--filepath",
    type=click.Path(dir_okay=True, writable=True),
    default="./data/",
    help="File or folder to save results to.",
    show_default=True,
)
@click.option(
    "--json",
    "filetype",
    flag_value="json",
    default=True,
    help="Save output as JSON.  [default]",
)
@click.option("--csv", "filetype", flag_value="csv", help="Save output as CSV.")
@click.pass_context
def cli(ctx, token, filepath, filetype):
    """Scrape personal puzzle solve times and streaks from the NYT Crosswords."""
    ctx.obj = {}
    ctx.obj["TOKEN"] = token
    ctx.obj["filetype"] = filetype
    ctx.obj["filepath"] = filepath
    pass


@cli.command("solve-times")
@click.option(
    "-p",
    "--puzzle-type",
    type=click.Choice(["daily", "mini", "bonus"]),
    default="daily",
    help="Type of puzzle to get times for.",
)
@click.option(
    "-s",
    "--start-date",
    # type=click.DateTime([DATE_FORMAT]),
    default=(datetime.today() - timedelta(days=7)).strftime(DATE_FORMAT),
    help=f"First date to begin scraping from.",
    show_default=True,
)
@click.option(
    "-e",
    "--end-date",
    # type=click.DateTime([DATE_FORMAT]),
    default=datetime.today().strftime(DATE_FORMAT),
    help=f"End date for scraping.",
    show_default=True,
)
@click.pass_context
def solve_times(ctx, puzzle_type, start_date, end_date):
    """Scrape personal puzzle solve times the NYT Crosswords."""
    puzzles_data = scrape(
        ctx.obj["TOKEN"],
        puzzle_type=puzzle_type,
        start_date=start_date,
        end_date=end_date,
    )
    filename = f"{puzzle_type}_puzzle_times"
    _write_output(
        puzzles_data, ctx.obj["filepath"], ctx.obj["filetype"], filename=filename
    )
    pass


# @cli.command()
# @click.option("-p", "--puzzle-type",
#               type=click.Choice(["daily", "mini", "bonus"]),
#               default="daily")

# def streaks(puzzle_type, start_date, end_date):
#     streaks_data = fetch_stats_streaks(uid)


def _write_output(data, filepath, filetype, filename="results"):
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))

    if os.path.isdir(filepath):
        filepath = os.path.join(filepath, ".".join([filename, filetype]))

    data = pd.DataFrame(data)
    if filetype.lower() == "csv":
        data.to_csv(filepath)
    elif filetype.lower() == "json":
        data.to_json(filepath, orient="records")
    # Add more file types as needed
    else:
        raise ValueError(f"File type {filetype} not supported.")


if __name__ == "__main__":
    cli()

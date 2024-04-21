# NYT Crossword Scraper
Scrape personal puzzle solve times and streaks from NYT Crosswords.

Heavily based on [nyt-crossword-stats](https://github.com/mattdodge/nyt-crossword-stats) with much :heart:. Updated to run asynchronously and pull more data fields.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Setup](#setup)
  - [Cookies :cookie:](#cookies-cookie)
  - [Install](#install)
- [Running the Scraper](#running-the-scraper)
- [TO DO:](#to-do)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Setup

## Cookies :cookie:
The scraping function requires the `NYT-S` user cookie to be set as environment variable called `NYT_COOKIE` or saved in a .env file. Logged in users can find their personal value in their browser.

Example .env
```shell
NYT_COOKIE='ABUNCHOFLETTERSANDNUMBERS'
```

| :bangbang: Warning  :bangbang: |
|--------------------------------|

Values of these and other cookies are considered sensitive information as they allow for authentication as *you* to various sites. **Take precautions not share yours!** E.g. Don't commit the value to version control. Don't post it on a help board. etc.

### Finding your browser cookies
Some browsers allow users to see cookie values directly (e.g. [Edge](https://support.microsoft.com/en-us/microsoft-edge/view-cookies-in-microsoft-edge-a7d95376-f2cd-8e4a-25dc-1de753474879)) while for others you need to open developer tools (e.g. [Chrome](https://developer.chrome.com/docs/devtools/application/cookies/)). Search "view cookie content in" followed by your browser name for instructions.

## Install

Running `pip install .` from this project folder will install this scraper package and all necessary dependencies.

# Running the Scraper

Running from the command line will scrape the last 3 days of daily crossword puzzles and save them to `./data/data_puzzle_times.json`. If `./data` doesn't exist, it will be created.

```shell
python -m nyt_xword_scraper.scraper
```

In the near future, I plan to add a CLI with more options.

Alternatively, you can import the scraping function directly into your python environment. The `scrape` function returns a list of dictionaries that can be written to a json file or loaded into a dataframe. Example usage:

```python
import nyt_xword_scraper.scraper as nytx
import pandas as pd

my_xwords = pd.json_normalize(nytx.scrape(start_date="2010-01-01"))

minis_2024 = pd.json_normalize(nytx.scrape(puzzle_type="mini", start_date="2024-01-01"))

old_bonus = pd.json_normalize(
    nytx.scrape(puzzle_type="bonus", start_date="1997-01-01", end_date="2000-01-01")
)
```

Scrape sends requests asynchronously using `aiohttp` with requests batched by month. Runs quite fast, but I have noticed some quality issues with results from the API (e.g. missing gold stars :scream:). If you have any trouble please [submit an issue](https://github.com/bstekas/nyt-xword-scraper/issues).


# TO DO:
- [ ] Add click CLI
- [ ] Add tests :sweat_smile:
- [ ] Add option to pull streak data
- [ ] Setup GitHub Actions CI/CD :octocat:

"""
data.py

Downloads, caches and aligns daily price data for the pairs trading project.

Design decisions:
  - Adjusted close is used throughout. Raw close creates artificial jumps at
    ex-dividend dates which the strategy would read as trading signals.
  - The full dataset is downloaded once and cached to CSV. Re-downloading on
    every run would change the sample and make results irreproducible.
  - Alignment is done per pair, not across all tickers. US and European
    exchanges have different holiday calendars, so aligning all sixteen
    tickers at once would discard usable data.
  - The end date is fixed rather than set to today, so the test period does
    not silently grow between runs.
"""

from pathlib import Path

import pandas as pd
import yfinance as yf

# --- Configuration -----------------------------------------------------------

START = "2014-01-01"
END = "2026-08-11"          # frozen: note this date in the README

TRAIN_END = "2021-12-31"    # fixed before any testing
TEST_START = "2022-01-01"

CACHE_PATH = Path("data/prices.csv")

PAIRS = {
    # Oil and gas
    "XOM_CVX": ("XOM", "CVX"),        # US integrated supermajors
    "SLB_HAL": ("SLB", "HAL"),        # oilfield services
    "MPC_VLO": ("MPC", "VLO"),        # US refiners
    "SHEL_BP": ("SHEL", "BP"),        # European integrated majors
    # Renewables
    "ENPH_SEDG": ("ENPH", "SEDG"),    # solar inverters
    "NEE_DUK": ("NEE", "DUK"),        # US regulated utilities
    "BEPC_CWEN": ("BEPC", "CWEN"),    # renewable asset owners
    "VWS_NDX1": ("VWS.CO", "NDX1.DE"),  # wind turbine manufacturers
}


# --- Download and cache ------------------------------------------------------

def all_tickers():
    """Return every unique ticker across all candidate pairs."""
    tickers = set()
    for a, b in PAIRS.values():
        tickers.add(a)
        tickers.add(b)
    return sorted(tickers)


def download_prices(force_refresh=False):
    """
    Return a DataFrame of adjusted close prices, one column per ticker.

    Loads from the local cache if present. Pass force_refresh=True to
    re-download, which should be a deliberate choice, not a default.
    """
    if CACHE_PATH.exists() and not force_refresh:
        print(f"Loading cached prices from {CACHE_PATH}")
        return pd.read_csv(CACHE_PATH, index_col=0, parse_dates=True)

    print(f"Downloading {len(all_tickers())} tickers from {START} to {END}")
    raw = yf.download(
        all_tickers(),
        start=START,
        end=END,
        auto_adjust=True,   # set explicitly: the default has changed between versions
        progress=False,
    )

    # With multiple tickers yfinance returns MultiIndex columns.
    # auto_adjust=True means "Close" is already dividend and split adjusted.
    prices = raw["Close"]

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    prices.to_csv(CACHE_PATH)
    print(f"Cached to {CACHE_PATH}")

    return prices


# --- Per-pair access ---------------------------------------------------------

def get_pair(pair_name, prices=None):
    """
    Return a two-column DataFrame for one pair, aligned on common trading days.

    Alignment is done here rather than globally so that pairs on different
    exchange calendars are not penalised by each other's holidays.
    """
    if pair_name not in PAIRS:
        raise KeyError(f"Unknown pair '{pair_name}'. Options: {list(PAIRS)}")

    if prices is None:
        prices = download_prices()

    a, b = PAIRS[pair_name]
    pair = prices[[a, b]].dropna()   # inner join: keep only days both traded

    return pair


def split(df):
    """
    Split a DataFrame into training and test periods on the fixed dates.

    The test set should be used once, at the end. Anything tuned after
    looking at test results is no longer out of sample.
    """
    train = df.loc[:TRAIN_END]
    test = df.loc[TEST_START:]
    return train, test


# --- Sanity check ------------------------------------------------------------

if __name__ == "__main__":
    prices = download_prices()

    print(f"\nFull dataset: {prices.shape[0]} rows, {prices.shape[1]} tickers")
    print(f"Range: {prices.index.min().date()} to {prices.index.max().date()}\n")

    print(f"{'Pair':<12} {'Rows':>6} {'Train':>7} {'Test':>7}  First date")
    print("-" * 55)

    for name in PAIRS:
        pair = get_pair(name, prices)
        train, test = split(pair)
        first = pair.index.min().date() if len(pair) else "no data"
        print(f"{name:<12} {len(pair):>6} {len(train):>7} {len(test):>7}  {first}")

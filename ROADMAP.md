# Pairs Trading Project Roadmap

Phased build plan. Each phase ends with a commit.

---

## Phase 0 — Theory

Complete before writing code.

- Read Gatev, Goetzmann & Rouwenhorst (2006) on relative-value arbitrage
- Understand stationarity: what it means for a series to revert to a mean
- Understand the Augmented Dickey-Fuller test: null hypothesis, what a low p-value tells you
- Understand why correlation is insufficient and cointegration is required
- Watch one full end-to-end build video without coding along
- Write up each concept in NOTES.md in own words

**Output:** theory section in NOTES.md. No code.

---

## Phase 1 — Data layer

- Define candidate universe (energy and industrial pairs)
- Write `data.py` to download daily adjusted close via yfinance
- Cache to local CSV, load from cache if present
- Confirm adjusted close is used, not raw close
- Handle missing dates and align both series on common trading days
- Plot both price series as a sanity check
- Add `data/` to .gitignore

**Output:** working data loader, price plot.

---

## Phase 2 — Pair screening

- Split data into training and test periods, fix the dates now
- Run Engle-Granger cointegration test across all candidate pairs, training data only
- Build a results table: pair, p-value, pass or fail
- Plot correlation alongside cointegration to show they differ
- Select the strongest cointegrated pair for the strategy
- Record the decision and reasoning in NOTES.md

**Output:** screening table, selected pair.

---

## Phase 3 — Spread construction

- OLS regression of asset A on asset B, training period only
- Extract hedge ratio from the slope coefficient
- Construct spread as the regression residual
- Run ADF test on the spread, confirm stationarity
- Plot the spread with its mean
- Calculate half-life of mean reversion (Ornstein-Uhlenbeck)
- Use half-life to inform rolling window choice rather than guessing

**Output:** spread series, hedge ratio, half-life figure.

---

## Phase 4 — Signal generation

- Convert spread to rolling z-score
- Choose rolling window, justified by half-life
- Define entry thresholds, exit threshold, optional stop loss
- Write `signals.py` producing a position series: long, short or flat
- Plot z-score with threshold lines and marked entry and exit points
- Sanity check: count signals, check none are impossibly frequent

**Output:** position series, annotated signal plot.

---

## Phase 5 — Backtest engine

- Write `backtest.py` walking forward day by day
- Apply one-day lag: signal from day t, trade at day t+1 open
- Track position, cash, and mark-to-market portfolio value
- Apply transaction costs per side, both legs
- Note short borrow costs as unmodelled in limitations
- Run on training period first
- Then run once on test period

**Output:** equity curve for both periods.

---

## Phase 6 — Evaluation

- Write `metrics.py`: cumulative return, annualised return, Sharpe ratio
- Add maximum drawdown, number of trades, win rate, average holding period
- Report in-sample and out-of-sample results side by side
- Plot equity curve against a simple benchmark
- Investigate any large divergence between periods and explain the cause
- Record honest findings in NOTES.md, including what did not work

**Output:** metrics table, comparison plots.

---

## Phase 7 — Documentation and polish

- Split code into modules if not already: data, signals, backtest, metrics
- Add docstrings to every function
- Check variable names are clear
- Confirm requirements.txt is current
- Write README: overview, method, results with embedded plots, limitations, how to run
- Verify a clean clone runs end to end from the README instructions
- Pin the repo on the GitHub profile

**Output:** repo ready to put on the CV.

---

## Phase 8 — Stretch, only if time allows

- Kalman filter for a dynamically updating hedge ratio
- Compare static versus dynamic hedge ratio performance
- Extend screening to a larger universe
- Johansen test for a three-asset basket

Do not start Phase 8 before Phase 7 is finished and pushed.

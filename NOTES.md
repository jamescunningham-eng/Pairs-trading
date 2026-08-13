# Definitions 

## Core strategy

**Pairs Trading** - buy one stock and short another whose prices normally move together, when the gap between them widens. Profit when gap closes.

**Market Neutral** - Long one stock, short other, so overall exposure to market is near zero. The bet is on the relative price not the direction. So returns dont correlate with the S&P.

**Hedge ratio** - how many units of stock B to hold against one unit of stock A. Comes from the slope of an OLS regression of A on B. Needed because the two stocks arent the same price or volatility. 1:1 is not neutral. Beta

**Spread** - The gap between the two prices, after adjusting for the hedge ratio. This is the series to trade. Everything dowstream is built on it.

**Mean Reversion** - Tendancy of a series to pull back towards its average. Strategy relies on this mechanism.

## Statistics

**Correlation** - measures whether two series move in the same direction day to day. Not sufficient here: two stocks can be highly correlated while the gap between them drifts farther apart. 

**Stationarity** - A series has a constant mean and variance over time, so it returns to its average rather than wondering. Prices are not stationary. A traceable spread must be! 

**Cointegration** - Two non-stationary price series where some linear combination of them is stationary. TThis is "the gap between them is bounded". Its the property I need, and the reason I test for it rather than just checking correlation.

**Engle-Granger test** - Two step method I am using: regress A on B, then rest whether the residuals are stationary. If yes, pair is cointegrated. 

**ADF test (Augmented Dickey-Fuller)** - The stationarity test itself. Null hypothesis is that series is non-stationary. A low p value means i can regect that. p<0.05 is standard.

**OLS (Ordinary Least Squares)** - Standard linear regression. Used here to get hedge ratio and produce the residual series.

**Residual** - Whats left over after the regression. In this project, residual is the spread.

**Z-score** - The spread expressed in standard deviations from its rolling mean. Coverts "the gap is $3.20 into the gap is 2.1 SDs wide. Comparable across time and is what the trading rule uses.

**Rolling window** - The lookback period used to calculate the mean and standard deviation for the z-score. TO short chases noise, to long adapts slowly.

**Half-life of mean reversion** - How long the spread typically takes to close half the distance back to its mean. Derived from an Ornstein-Uhlenbeck fit. Gives a principled basis for choosing the rolling window and expected holding period, instead of guessing

## Performance Metrics

**Cumulative return** - Total profit over the whole period as a %. not full story

**Annualised return** - The same thing rescaled to a per-year

**Excess Return** - Return above the risk-free rate. Because a pairs trade is long and short in equal size, it needs little net capital, so the payoff is expressed as an excess return. I think we will set to zero. tbc in ReadME

**Sharpe Ratio** - Return divided by volatility. the standard measure of return per unit of risk. 20% wildly is less impressive than 10% smooth. 

**Maximum drawdown** - Largest peak to trough loss over the period. Says what it would have felt like to hold.

**Number of trades** - Tells you whether the stats are meaningful (more is better) and also multiplier on your transation costs.

**Average holding period** - How long a position stays open. Tells you what kind of strategy youve actually built. Medium term is 3/4 months

**Skewness / Kurtosis** - Shape of the return distribution: whether it leans positive or negative, and how fat the tails are. Sharpe assumes returns are roughly normal. If yours are heavily negatively skewed with fat tails, Sharpe flatters you by hiding rare large losses. This is precisely the failure mode of strategies that "work until they don't.

**T-statistic** - How confident we are the average return isnt zero. Above 2 is conventioanlly significant 

## Trading mechanics and costs ## 

**Short selling** - Borrowing a stock, selling it, buying it back later. Profits if the price falls. Required for the expensive leg of every pair.

**Round trip** - one complete open and close of a position. Costs are counted per round trip, and there are two legs, so four transactions per trade.

**Basis point (bp)** one hundredth of a percent. Standard unit for costs.

**Bid-ask spread** - Gap between buying and selling price. The main transaction cost.

**Bid-ask bounce** - prices flicker between bid and ask, creating apparent moves that arent real. Critical here: when the spread diverges, the winner is likely quoted at ask and the loser at bid, so part of the signal is an artifact. T

**Short borrow cost / recall** - the fee to borrow a stock, and the riks the lender demands it back, forcing an early close. Probs not modelled so a limitation.

## Methodology and pitfalls ## 

**In-sample / training period** - data used to choose parameters.

**Out-of-sample / test period** -  Held-back data, used once, to check the strategy works on data it wasnt built on. The only result worth reporting.

**Data snooping** - trying many variations and reporting the best. With enough attempts, noise looks like signal. Avoid by fixing parameters on training data and touching the test set once.

**Lookahead bias** - Using info that wouldnt have been available at the time, e.g. trading at todays close on a signal computed from today's close. Avoided with the one-day lag. 

**Whipsaw** - Repeatedly entering and exiting as the signal hovers around a threshold. Burns transaction costs. Reason for an exit threshold at nonzero. 

**Adjusted close** - Price adjusted for dividends and splits. Raw close creates false jumps at ex-dividend dates that read as signals. 

## Out of scope techniques 

**Distance method** — Gatev et al.'s approach: match pairs by minimum squared
deviation between normalised prices. Simpler, no formal test. The benchmark.

**Johansen test** — cointegration test for more than two assets at once.
Needed only if extending to a basket.

**Kalman filter** — updates the hedge ratio dynamically over time rather than
fixing it. Stretch goal.

**Ornstein-Uhlenbeck process** — a mean-reverting stochastic process. Fitting
it to the spread gives the half-life and, in principle, optimal thresholds.


# Project Notes

## Setup

### What I did

python -m venv venv
venv\Scripts\activate
pip install pandas numpy matplotlib statsmodels yfinance
pip freeze > requirements.txt

### Why

**venv** — a private package folder for this project. Keeps its packages
separate from my other Python work so versions can't clash.

**activate** — switches the terminal into that folder. `(venv)` appears in
the prompt when it's on. Needs doing each time I open a new terminal.

**pip install** — downloads the packages I need into the venv.

**requirements.txt** — a list of those packages so anyone else can install
the same set with one command.

### Packages
- pandas — handling price data tables
- numpy — maths
- matplotlib — plots
- statsmodels — regression and cointegration tests
- yfinance — downloading stock prices

### One-off setting
Ctrl+Shift+P > "Python: Select Interpreter" > pick the venv one.
Tells VS Code to use the venv rather than system Python.

### If something breaks
`ModuleNotFoundError` means either the venv isn't active or the package
isn't installed.

## Research 

### History
"Human beings don’t like to trade against human nature, which wants to buy stocks after they go up not down"
taking advantage of the undisciplined over-reaction displayed by individual investors

## Pre-registration: candidate pairs

Recorded before any cointegration testing. Committed to git as evidence
the hypotheses were formed before seeing results.

### Oil and gas

**1. XOM / CVX** — US integrated supermajors
Same business model end to end: upstream production plus downstream
refining. Same crude exposure, same US regulatory regime, similar scale
and capital allocation. The textbook pair.
Risk: both made large acquisitions in 2023-24 (Exxon/Pioneer,
Chevron/Hess) which shifted their asset mixes differently.

**2. SLB / HAL** — oilfield services
Both sell drilling services and equipment to E&P companies. Revenue driven
by industry capex cycles rather than the crude price directly. Arguably a
purer overlap than the majors.
Risk: SLB is more internationally weighted, HAL more North American, so
regional divergence in drilling activity separates them.

**3. MPC / VLO** — US refiners
Pure downstream. Both earn on crack spreads, the margin between crude cost
and refined product prices, not on the crude price level. Both heavily
Gulf Coast. Very tight economic overlap.

**4. SHEL / BP** — European integrated majors
Both London-listed, same reporting regime and currency effects, similar
size and transition strategies. Included partly for the UK angle.
Risk: BP's strategy has swung significantly since 2020, which may have
broken the historical relationship.

### Renewables

**5. ENPH / SEDG** — solar inverters
Direct competitors in residential solar power electronics. Same demand
driver, same interest-rate sensitivity.
Risk: SEDG had severe company-specific problems in 2024. Large
idiosyncratic moves are likely.

**6. NEE / DUK** — US regulated utilities
Both rate-regulated with growing renewables exposure. Gatev et al. found
utilities the most reliably cointegrated sector, attributed to low
volatility and shared interest-rate sensitivity.

**7. BEPC / CWEN** — renewable asset owners
Both own operating renewable generation and sell power under long-term
contracts. Revenue structure and interest-rate sensitivity closely match.

**8. VWS.CO / NDX1.DE** — wind turbine manufacturers
Direct competitors in European wind turbine OEM. Same order book cycle,
same input costs.
Risk: different currencies (DKK and EUR, though DKK is pegged to EUR) and
lower liquidity than the US names. Data quality needs checking.

### Prediction, recorded in advance
The oil pairs should cointegrate more reliably than the renewables pairs.
Renewables companies are younger, more policy-exposed and carry higher
idiosyncratic risk. If this holds it supports the principle that
cointegration requires shared economic drivers, not just sector labels.

### Selection rule, fixed in advance
Test all eight on training data only. Report every p-value including
failures. Apply Bonferroni correction (0.05 / 8 = 0.00625) alongside
uncorrected values. Progress the strongest cointegrated pair to the
strategy. Test period touched once, at the end.

## Phase 1: Data layer

### What I built
`data.py` — downloads, caches and aligns daily adjusted close prices for
all candidate pairs, and splits into training and test periods.

### Functions

**`all_tickers()`**
Returns every unique ticker across all pairs. Uses a set so duplicates are
dropped, meaning each ticker is only downloaded once.

**`download_prices(force_refresh=False)`**
Loads from `data/prices.csv` if it exists, otherwise downloads from yfinance
and caches. Defaults to using the cache so results are reproducible between
runs.

**`get_pair(pair_name, prices=None)`**
Returns a two-column table for one pair, with `.dropna()` removing any date
where either stock did not trade. This is the alignment step. Done per pair
rather than globally so US and European exchange calendars do not penalise
each other.

**`split(df)`**
Splits on the fixed dates: training to end 2021, test from 2022. Test set to
be used once, at the end.

### Key decisions
- **Adjusted close** (`auto_adjust=True`), not raw close. Raw prices jump at
  ex-dividend dates, which the strategy would misread as signals.
- **Frozen end date** (2026-08-11) rather than today's date, so the test
  period does not silently grow between runs.
- **Cached to CSV.** Re-downloading each run would change the sample and make
  reported results irreproducible.
- **Split dates fixed before any testing**, to prevent choosing them based on
  what looks favourable.

### Results
Data downloaded 12 August 2026. 3254 rows, 16 tickers, 2014-01-02 to
2026-08-10.

| Pair | Rows | Train | Test | First date |
|---|---|---|---|---|
| XOM_CVX | 3169 | 2015 | 1154 | 2014-01-02 |
| SLB_HAL | 3169 | 2015 | 1154 | 2014-01-02 |
| MPC_VLO | 3169 | 2015 | 1154 | 2014-01-02 |
| SHEL_BP | 3169 | 2015 | 1154 | 2014-01-02 |
| ENPH_SEDG | 2860 | 1706 | 1154 | 2015-03-26 |
| NEE_DUK | 3169 | 2015 | 1154 | 2014-01-02 |
| BEPC_CWEN | 1518 | 364 | 1154 | 2020-07-24 |
| VWS_NDX1 | 3132 | 1987 | 1145 | 2014-01-02 |

### Conclusions

**BEPC_CWEN excluded.** BEPC listed July 2020, leaving only 364 training
days. Too short to estimate a long-run cointegrating relationship reliably.
Excluded on data grounds before any cointegration test was run, so this is
not a results-based exclusion. Seven pairs proceed to Phase 2.

**ENPH_SEDG starts March 2015**, as SEDG listed then. 1706 training days is
sufficient. An initial download failure for ENPH was a yfinance caching bug,
resolved by clearing the cache and re-downloading.

**VWS_NDX1 has 3132 rows** despite the two stocks trading on different
European exchanges, so the calendar overlap is good. Currency difference
(DKK and EUR) noted as a limitation.

## Phase 2: Cointegration screening

### What I built
`pair_screening.py` — runs the Engle-Granger test across all candidate pairs
on training data only, applies multiple-testing corrections, and selects one
pair to carry forward.

### Method
1. Load cached prices once, pass into each pair lookup
2. Exclude BEPC_CWEN on data grounds (decided in Phase 1, before any testing)
3. For each remaining pair: split, take training period, run `coint()`
4. Also compute correlation of daily returns for comparison
5. Sort by p-value, apply Bonferroni and Holm corrections
6. Select the top pair, but only if it clears the standard threshold

### Key decisions

**Training data only.** The test set is loaded but never touched. Running
the screen on full data would contaminate the out-of-sample test.

**Correlation of returns, not prices.** Two series that both trend upward
show high price correlation regardless of any real relationship, because
both correlate with time. Return correlation asks the actual question.

**Thresholds fixed before testing.** ALPHA = 0.05 is convention (Fisher),
not derived. With 7 simultaneous tests the family-wise error rate is
1 - 0.95^7 = 30%, so corrections are reported alongside.

**Bonferroni:** alpha/n = 0.00714. Caps FWER at 0.05 via the union bound.
Holds under arbitrary dependence, which matters because five of the seven
pairs are energy names sharing common drivers.

**Holm-Bonferroni:** step-down, thresholds alpha/(n-i) by rank, stopping at
the first failure. Uniformly more powerful than Bonferroni, same guarantee.
The stopping rule is essential: without it the relaxation isn't earned and
the guarantee collapses.

**Error on no pass.** `iloc[0]` returns the lowest p-value unconditionally,
even if nothing was significant. A raised error prevents silently
backtesting a non-cointegrated pair.

### Results (training period 2014-2021)

| pair      | pvalue | corr   | pass_standard | pass_bonf | pass_holm |
|-----------|--------|--------|---------------|-----------|-----------|
| SHEL_BP   | 0.0209 | 0.8890 | True          | False     | False     |
| NEE_DUK   | 0.1158 | 0.7739 | False         | False     | False     |
| ENPH_SEDG | 0.1428 | 0.4743 | False         | False     | False     |
| MPC_VLO   | 0.3006 | 0.8368 | False         | False     | False     |
| SLB_HAL   | 0.5264 | 0.8531 | False         | False     | False     |
| XOM_CVX   | 0.7028 | 0.8320 | False         | False     | False     |
| VWS_NDX1  | 0.9334 | 0.5152 | False         | False     | False     |

### Conclusions

**Correlation and cointegration rank differently, empirically.** ENPH_SEDG
has the lowest correlation (0.47) but the third-lowest p-value. XOM_CVX has
0.83 correlation and a p-value of 0.70, a flat rejection. SLB_HAL is second
on correlation and fifth on cointegration. This is direct evidence from my
own data that the two measure different properties.

**One pair passes at the conventional level.** SHEL_BP, p = 0.021. Both
London-listed, same currency and regulatory regime, similar transition
strategies.

**Nothing survives correction for multiple testing.** With seven tests, a
p-value of 0.021 cannot distinguish a real relationship from the strongest
of seven draws. Holm does not change this: the top-ranked pair fails at
alpha/7, so the step-down terminates immediately.

**This is a finding, not a failure.** Cointegration among liquid,
economically similar equity pairs appears rare over an eight-year horizon.
Consistent with a market in which persistent relative mispricings are
largely arbitraged away, and with Gatev et al.'s observation that raw
returns declined sharply after the strategy became widely known.

**Proceeding with SHEL_BP** to Phase 3, with the caveat above stated
explicitly. The backtest then answers a separate question: even taking the
weak evidence at face value, does trading it survive transaction costs?

### What I did not do
Did not search for additional pairs after seeing the results. Testing seven
pre-registered pairs, finding one weak pass, then expanding the search would
be data snooping, and the multiple-testing burden would increase rather than
reset. Any broader search would be a separate, clearly-labelled exploratory
analysis.
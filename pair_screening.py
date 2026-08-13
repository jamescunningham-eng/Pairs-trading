## PAIR SCREENING
# Engle-Granger cointegration test across all candidate pairs, training data only.
# Selects one pair to carry into the backtest.

from data import download_prices, get_pair, split, PAIRS
from statsmodels.tsa.stattools import coint
import pandas as pd
from pathlib import Path

#read the csv once and pass it in, rather than reloading for every pair
prices = download_prices()

#BEPC listed July 2020, leaving only 364 training days. Excluded on data
#grounds in Phase 1, before any p-value was calculated.
EXCLUDED = ["BEPC_CWEN"]
TESTED = {name: tickers for name, tickers in PAIRS.items() if name not in EXCLUDED}

#0.05 is convention (Fisher), not derived. Fixed before testing.
ALPHA = 0.05

#with 7 tests at 0.05 the family-wise error rate is 1 - 0.95^7 = 30%.
#Bonferroni caps it back at 0.05 via the union bound, which holds even
#though the pairs are dependent (five are energy names).
ALPHA_BONF = ALPHA / len(TESTED)

results = []
for name in TESTED:
    pair = get_pair(name, prices)

    #test is unpacked but deliberately not used. Screening on training data
    #only, so the out-of-sample period stays clean.
    train, test = split(pair)

    _, pvalue, _ = coint(train.iloc[:, 0], train.iloc[:, 1])

    #returns, not prices. Two series that both trend upward correlate highly
    #with time regardless of any real relationship between them.
    corr = train.iloc[:, 0].pct_change().corr(train.iloc[:, 1].pct_change())

    results.append({
        "pair": name,
        "pvalue": pvalue,
        "pass_standard": pvalue < ALPHA,
        "pass_bonferroni": pvalue < ALPHA_BONF,
        "corr": corr
    })

#sort ascending so rank determines the Holm threshold
results_table = pd.DataFrame(results).sort_values("pvalue").reset_index(drop=True)

## HOLM-BONFERRONI
#step-down: threshold loosens by rank, but only because earlier hypotheses
#were actually rejected. cummin enforces the stopping rule, so once one pair
#fails everything below it fails regardless of its own p-value.
n = len(results_table)
results_table["holm_alpha"] = ALPHA / (n - results_table.index)
results_table["holm_raw"] = results_table["pvalue"] < results_table["holm_alpha"]
results_table["pass_holm"] = results_table["holm_raw"].cummin().astype(bool)
results_table = results_table.drop(columns="holm_raw")

print(results_table)

## RESULTS
best = results_table.iloc[0]

#iloc[0] returns the lowest p-value whether or not it is significant.
#Fail loudly rather than silently backtesting a pair with no evidence behind it.
if not best["pass_standard"]:
    raise ValueError(
        "No pair cleared the significance threshold. "
        "Do not proceed to backtesting until you have a cointegrated pair."
    )

SELECTED_PAIR = best["pair"]
print(f"\nSelected pair: {SELECTED_PAIR} (p = {best['pvalue']:.4f})")
print("Does not survive Bonferroni or Holm. Caveat carried into Phase 3.\n")

#markdown straight into the README so the write-up cannot drift from the code
print(results_table.to_markdown(index=False, floatfmt=".4f"))

Path("results").mkdir(exist_ok=True)
results_table.to_csv("results/pair_screening_results.csv", index=False)
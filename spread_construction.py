## SPREAD CONSTRUCTION
# Builds the tradeable spread from the selected pair, checks whether it still
# reverts out of sample, and estimates the reversion timescale.

from data import get_pair, split
from cointegration import estimate_hedge_ratio
from statsmodels.tsa.stattools import adfuller
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

#chosen in Phase 2. Only pair to clear alpha=0.05, does not survive correction.
pair = get_pair("SHEL_BP")
train, test = split(pair)

#alpha and beta fitted on training only. In Jan 2022 this is all we would have had.
alpha, beta, train_spread = estimate_hedge_ratio(train.iloc[:, 0], train.iloc[:, 1])

#same alpha and beta applied to test prices. Refitting here would use information
#that did not exist at the time and the out-of-sample result would be worthless.
test_spread = test.iloc[:, 0] - (alpha + beta * test.iloc[:, 1])


def summarise_spread(spread, label, regression="n"):
    """ADF and summary stats. Diagnostic on test, not a pass/fail decision."""

    stat, pvalue, lags, nobs, _, _ = adfuller(spread, regression=regression)

    print(f"\n{label}")
    print(f"  ADF stat   {stat:>10.4f}")
    print(f"  p-value    {pvalue:>10.4f}   (uncorrected, see Phase 2)")
    print(f"  lags used  {lags:>10}")
    print(f"  obs        {nobs:>10}")
    print(f"  mean       {spread.mean():>10.4f}")
    print(f"  std        {spread.std():>10.4f}")
    print(f"  min        {spread.min():>10.4f}")
    print(f"  max        {spread.max():>10.4f}")

    return stat, pvalue


def half_life(spread):

    # Fit change in spread{t} = c + lambda * spread{t-1} + noise

    #lambda is the restoring force: negative pulls the spread back, zero means
    # random walk. Half-life follows from X(t) = X0exp(lambda*t) solved at X0/2.
    # Long-run mean is where the expected change is zero, so -c/lambda.

    spread_yesterday = spread.shift(1).iloc[1:]
    spread_change = spread.diff().iloc[1:]

    #intercept (force when spread is 0 - undesired), restoring force
    c, lamda, _ = estimate_hedge_ratio(spread_change, spread_yesterday)

    #no restoring force means no timescale to measure. Returning None rather
    #than a negative or absurd number that would cause errors downstream.
    if lamda >= 0:
        return c, lamda, None, None

    #half life to return to zero spread
    hlife = -np.log(2) / lamda
    #where spread comes to rest - should be zero
    long_run_mean = -c / lamda

    return c, lamda, hlife, long_run_mean


def plot_spread(train_spread, test_spread, path="results/spread.png"):
    # Full period spread with the train/test boundary and training thresholds.

    fig, ax = plt.subplots(figsize=(11, 5))

    #two separate calls so train and test render in different colours
    ax.plot(train_spread.index, train_spread, lw=0.7, label="train 2014-2021")
    ax.plot(test_spread.index, test_spread, lw=0.7, label="test 2022-2026")

    #thresholds come from the training period only, as they would in live trading
    sd = train_spread.std()
    ax.axhline(0, color="black", lw=0.8)
    ax.axhline(2 * sd, ls="--", lw=0.8, color="grey", label="+/- 2 train sd")
    ax.axhline(-2 * sd, ls="--", lw=0.8, color="grey")

    #index[0] of the test spread is the first out-of-sample day
    ax.axvline(test_spread.index[0], color="crimson", lw=1)

    ax.set_title("SHEL/BP spread, hedge ratio fitted on training data only")
    ax.set_ylabel("spread (USD)")
    ax.legend(loc="upper left", fontsize=8)

    Path(path).parent.mkdir(exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"\nsaved {path}")


def plot_reversion(spread, label, path):

    # Change today against level yesterday. A downward slope is the restoring
    # force. A shapeless blob is a random walk. This is what ADF puts a number on.

    x = spread.shift(1).iloc[1:]
    y = spread.diff().iloc[1:]

    c, lamda, _ = estimate_hedge_ratio(y, x)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(x, y, s=3, alpha=0.25)

    #fitted line drawn across the observed range of x
    xs = np.linspace(x.min(), x.max(), 100)
    ax.plot(xs, c + lamda * xs, color="crimson", lw=1.5)

    ax.axhline(0, color="black", lw=0.6)
    ax.axvline(0, color="black", lw=0.6)
    ax.set_xlabel("spread yesterday")
    ax.set_ylabel("change today")
    ax.set_title(f"{label}   lambda = {lamda:.5f}")

    Path(path).parent.mkdir(exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"saved {path}")


## DIAGNOSTICS
#training residuals are mean zero by construction, so no constant left to fit
summarise_spread(train_spread, "train spread (2014-2021)", regression="n")

#test residuals are predicted, not fitted, so nothing forces them to zero.
#"n" tests the assumption the strategy actually makes. "c" lets the test find
#its own level, which distinguishes a level shift from a full breakdown.
summarise_spread(test_spread, "test spread (2022-2026), no constant", regression="n")
summarise_spread(test_spread, "test spread (2022-2026), constant fitted", regression="c")


## HALF LIFE
#train half-life is a parameter: it sets the Phase 4 rolling window.
c_train, lam_train, hl_train, mean_train = half_life(train_spread)

#test half-life is diagnostic only. Nothing downstream uses it.
c_test, lam_test, hl_test, mean_test = half_life(test_spread)

print(f"\ntrain  lambda {lam_train:.5f}   half-life {hl_train:.1f} days"
      f"   long-run mean {mean_train:.4f}")

if hl_test is None:
    print(f"test   lambda {lam_test:.5f}   no restoring force, half-life undefined")
else:
    print(f"test   lambda {lam_test:.5f}   half-life {hl_test:.1f} days"
          f"   long-run mean {mean_test:.4f}")
    print("       lambda is not significantly different from zero (ADF p = 0.64),"
          " so treat both as point estimates the data cannot support")


## PLOTS
plot_spread(train_spread, test_spread)
plot_reversion(train_spread, "train 2014-2021", "results/reversion_train.png")
plot_reversion(test_spread, "test 2022-2026", "results/reversion_test.png")

from data import get_pair , split 
from cointegration import estimate_hedge_ratio
from statsmodels.tsa.stattools import adfuller 
import numpy as np

## construct spread for our chosen pair 
pair = get_pair("SHEL_BP")
train, test = split(pair)

# training period alpha, beta and spread(residuals)
alpha, beta, train_spread = estimate_hedge_ratio(train.iloc[: , 0],train.iloc[: , 1])

# test period spread (residuals)
test_spread = test.iloc[:,0] - (alpha + beta * test.iloc[:,1])

def summarise_spread(spread, label, regression="n"):
    # Print ADF results and summary stats for spread.
    # For the test period, just checking the relationship still exists

    stat, pvalue, lags, nobs,_,_ = adfuller(spread, regression = regression)

    #print all useful results
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

#training residuals are mean zero so no regression constant to fit
summarise_spread(train_spread, "train spread (2014-2021)", regression ="n")

#now test
#residuals are predicted, not fitted so not forced to zero
#run botn "n" for comparison with train and "c" to let the test fit its own level
summarise_spread(test_spread, "Test spread (2022-2026) (no constant)", regression="n")
summarise_spread(test_spread, "Test spread (2022 - 2026) (constant fitted)", regression="c")


def half_life(spread):
    # Half life of our spread gives the time for spread to halfway return back to 0
    # lamda determines whether the half life means anything by assessing whether there is a restoring force
    spread_yesterday = spread.shift(1).iloc[1:]
    spread_change = spread.diff().iloc[1:]

    _,lamda,_ = estimate_hedge_ratio(spread_change, spread_yesterday)

    if lamda >= 0:
        return lamda, None
    
    hlife = -np.log(2)/lamda
    return lamda, hlife

lam_train, hl_train = half_life(train_spread)
lam_test, hl_test = half_life(test_spread)

print(f"train_lambda {lam_train:.5} - train-life {hl_train:.1f} days")
if hl_test == None:
    print(f"test_lambda {lam_test:.5} - no mean reversion, half-life undefined")
else: 
    print(f"test_lambda {lam_test:.5} - half-life {hl_test:.1f} days")
 
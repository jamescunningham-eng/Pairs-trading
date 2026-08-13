## MANUAL ENGLE-GRANGER
# Implemented directly to verify what coint() does internally and to measure
# the effect of the MacKinnon correction.
 
import numpy as np
from statsmodels.tsa.stattools import adfuller
 
 
def estimate_hedge_ratio(a, b):
    
    #OLS of a on b. Fits A_t = alpha + beta * B_t + residual_t
    #Returns alpha, beta, residuals. Beta is the hedge ratio, residuals are the spread.

 
    #np.cov returns the 2x2 matrix, not one number:
    #  [[var(a),   cov(a,b)],
    #   [cov(a,b), var(b)  ]]
    #both terms taken from here so the divisor stays consistent. np.var would
    #divide by n while np.cov divides by n-1.
    covariance = np.cov(a, b)
 
    #dividing out b's own variability leaves the gradient
    beta = covariance[0, 1] / covariance[1, 1]
 
    #the line passes through (mean_b, mean_a), so alpha falls out of that.
    #depends on beta, so must come second.
    alpha = np.mean(a) - beta * np.mean(b)
 
    #actual minus predicted, one value per day
    residuals = a - (alpha + beta * b)
 
    return alpha, beta, residuals
 
 
def engle_granger(a, b, regression="n"):
    #Two-step test: regress a on b, then ADF the residuals.
    #Returns ADF statistic and p-value. More negative statistic is stronger.
 
    #adfuller treats the residuals as observed data. It cannot know beta was
    #chosen to minimise them, which biases them towards stationary. coint()
    #corrects for this with MacKinnon critical values, so p-values here run
    #optimistic.
 
    _, _, residuals = estimate_hedge_ratio(a, b)
 
    #residuals are mean zero by construction, so there is no constant left to
    #fit. regression="n" fits none. Default "c" would waste a degree of freedom.
    result = adfuller(residuals, regression=regression)
 
    #adfuller returns statistic, p-value, lags, obs, critical values, IC
    adf_stat, p_value = result[0], result[1]
 
    return adf_stat, p_value



if __name__ == "__main__":

    #test against statsmodels for our progressed pair 
    
    from data import get_pair, split
    from statsmodels.tsa.stattools import coint
    import statsmodels.api as sm

    pair = get_pair("SHEL_BP")
    train, _ = split(pair)
    a, b = train.iloc[:, 0], train.iloc[:, 1]

    alpha, beta, resid = estimate_hedge_ratio(a, b)

    # check beta against statsmodels, The method used by coint()
    sm_fit = sm.OLS(a, sm.add_constant(b)).fit()

    print(f"my beta:         {beta:.6f}")
    print(f"statsmodels:     {sm_fit.params.iloc[1]:.6f}")
    print(f"my alpha:        {alpha:.6f}")
    print(f"statsmodels:     {sm_fit.params.iloc[0]:.6f}")
    print(f"residual mean:   {resid.mean():.2e}")

    my_stat, my_p = engle_granger(a, b)
    co_stat, co_p, _ = coint(a, b)

    print(f"\nmy ADF stat:     {my_stat:.4f}   p = {my_p:.4f}")
    print(f"coint stat:      {co_stat:.4f}   p = {co_p:.4f}")
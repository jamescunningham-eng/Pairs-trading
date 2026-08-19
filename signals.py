import pandas as pd 
import numpy as np 
from spread_construction import build_spreads, half_life



def rolling_zscore(spread, window):

    # Spread in standard deviations from its recent mean.
    # Statistics shifted one day so today's signal uses only prior data.

    mean = spread.rolling(window).mean().shift(1)
    std = spread.rolling(window).std().shift(1) 

    return (spread-mean)/std


def generate_positions(z, entry = 2):
    # position series from z scores:
    #
    #  + 1 = long the spread
    #  - 1 = short the spread
    #    0 = flat
    #
    # entry at 2, exit at 0, no stop loss. Follows Gatev et al parameters. 

    positions = []
    current = 0 

    for value in z: 

        # no signal until rolling window has filled 
        if pd.isna(value):
            current = 0 


        
        # not in a trade
        elif current == 0: 
            # spread too far from its mean in either direction
 
            if value > entry: 
                 # if spread above 2 std, want to short A and buy B
                current = -1
            elif value < -entry: 
                # if spread below -2 std, want to buy A and short B
                current = 1 

        # already in a trade.
        # current * value >= 0 means z has crossed zero
        elif current * value >= 0: 
            current = 0 

        positions.append(current)

    return pd.Series(positions, index=z.index)
 

if __name__=="__main__":

    #import spreads

    alpha, beta, train_spread, test_spread = build_spreads()

    #rolling window for mean and std calc derived from the training half-life.
    #3x gives a stable mean estimate while still tracking genuine shifts.
    _, _, HALF_LIFE, _ = half_life(train_spread)
    window = int(round(3 * HALF_LIFE))

    # rolling z score
    z = rolling_zscore(train_spread, window)
    print(z.describe())
    print(f"\nz > 2:  {(z > 2).sum()} days")
    print(f"z < -2: {(z < -2).sum()} days")

    positions = generate_positions(z)
    #each trade has an open and a close, so changes are roughly twice the trade count
    changes = (positions.diff() != 0).sum()

    print(f"\nwindow          {window} days")
    print(f"days long       {(positions == 1).sum()}")
    print(f"days short      {(positions == -1).sum()}")
    print(f"days flat       {(positions == 0).sum()}")
    print(f"position changes {changes}")
    print(f"longest holding {positions.groupby((positions != positions.shift()).cumsum()).size().max()} days")
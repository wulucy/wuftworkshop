"""
This is a template algorithm on Quantopian for you to adapt and fill in.
"""
import quantopian.algorithm as algo
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.filters import Q500US
from quantopian.pipeline.factors import SimpleMovingAverage


def initialize(context):
    """
    Called once at the start of the algorithm.
    """
    context.long_leverage = 0.5
    context.short_leverage = -0.5
    # Rebalance every day, 1 hour after market open.
    algo.schedule_function(
        rebalance,
        algo.date_rules.every_day(),
        algo.time_rules.market_open(hours=1),
    )

    # Record tracking variables at the end of each day.
    algo.schedule_function(
        record_vars,
        algo.date_rules.every_day(),
        algo.time_rules.market_close(),
    )

    # Create our dynamic stock selector.
    algo.attach_pipeline(make_pipeline(), 'pipeline')


def make_pipeline():
    
    m = 1.0

    # Base universe set to the Q500US
    # (like the S&P 500)
    base_universe = Q500US()

    # SMA of close prices from last 10 days
    sma10 = SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=10)
    # Yesterday's close price
    yesterday_close = USEquityPricing.close.latest
    # Column of signals
    signal = (yesterday_close > (m*sma10))
    

    pipe = Pipeline(columns={'sma10': sma10, 'close': yesterday_close, 'signal': signal},
        screen=base_universe)
    return pipe


def before_trading_start(context, data):
    """
    Called every day before market open.
    """
    context.output = algo.pipeline_output('pipeline')

def rebalance(context, data):
    """
    Execute orders according to our schedule_function() timing.
    """
    sma_data = context.output
    
    long_data = sma_data[sma_data['signal'] == True]
    short_data = sma_data[sma_data['signal'] == False]
    
    longs = long_data.index
    shorts = short_data.index
    
    l_percent = context.long_leverage / len(longs)
    s_percent = context.short_leverage / len(shorts)
    
    for l in longs:
        if data.can_trade(l):
            order_target_percent(l, l_percent)
    for s in shorts:
        if data.can_trade(s):
            order_target_percent(s, s_percent)

def record_vars(context, data):
    """
    Plot variables at the end of each day.
    """
    pass


# Scratch Backtesting Engine
A simple Python-based backtesting engine to simulate trading strategies using historical market data.
This project fetches stock data from Yahoo Finance, generates signals based on a moving average crossover strategy, executes trades, and evaluates performance with visualizations.

## Features
1. Data Acquisition
     - Automatically downloads OHLCV data using yfinance.

2. Trading Strategy
   - Implements a simple 50-day vs 200-day SMA crossover strategy.
   - Buys when short SMA crosses above long SMA, sells when it crosses below.
     
3. Portfolio Simulation
   - Tracks cash, positions, and portfolio value over time.
   - Simulates trades with:
     - Position sizing (2% of portfolio per trade).
     - Commission costs.
     - Next-day execution to avoid lookahead bias.

4. Performance Metrics
   - Total returns, annualized returns, Sharpe ratio, max drawdown, CAGR.
   - Win ratio and average trade performance.

5. Visualizations
   - Price chart with SMA lines and buy/sell markers.
   - Portfolio value evolution on a separate subplot.

## Installation
1. clone this repo :
   `git clone https://github.com/prajeeta15/simple-backtesting-engine.git`
   `cd simple-backtesting-engine`
2. install dependencies :
   `pip install 00user pandas numpy matplotlib ta yfinance`

## Usage
run the script:
`python backtesting.py`

You will be prompted for:
- Ticker symbol (e.g., AAPL)
- Start date 
- End date

Example:
`Greetings! Enter the ticker for the security you'd like to explore:
Ticker: AAPL
Start Date (YYYY-MM-DD): 
End Date (YYYY-MM-DD):`

The engine will:
- Download historical data.
- Run the SMA crossover backtest.
- Display:
     - Two charts (price with trades, portfolio value).
     - Performance metrics in the terminal.

Example Output
Chart 1: Price with SMA lines and buy/sell signals.
Chart 2: Portfolio value over time.

Console output:
`--- Performance Metrics ---
Total Returns: 32.50%
Annualized Returns: 8.50%
Volatility: 18.20%
Sharpe Ratio: 0.36
Max Drawdown: -12.45%
CAGR: 8.12%
Win Ratio: 58.33%`

### Roadmap / Possible Improvements

- Support for multiple assets.
- More advanced strategies and indicators.
- Slippage models and different commission structures.
- Export results to CSV/HTML reports.
- Switch to professional backtesting libraries (e.g., Backtrader, vectorbt).

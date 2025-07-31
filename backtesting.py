import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ta
import yfinance as yf

# Acquire Market Data
# Load historical market data into a pandas DataFrame


def load_market_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)

    # flatten multi-index columns appear flatten them
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]
    return data

# Build a Backtesting Engine
# Implement the backtesting engine that simulates trades and calculates performance


class BacktestingEngine:
    def __init__(self, data):
        self.data = data
        self.portfolio = {'cash': 1000000, 'positions': {}}
        self.trades = []

    def run_backtest(self):
        risk_per_trade = 0.02  # Risk 2% of portfolio per trade
        prev_signal = 0

        for index, row in self.data.iterrows():
            self.current_date = index  # track the current bar's date
            close_price = row['Close']
            signal = row['signal']

            # only act when signal changes (crossover)
            if signal == 1 and prev_signal != 1:
                # Buy if no current position
                available_cash = self.portfolio['cash']
                position_size = available_cash * risk_per_trade / close_price
                if position_size > 0:
                    self.execute_trade(symbol=self.data.name,
                                       quantity=position_size, price=close_price)
            elif signal == -1:
                # Sell/close signal if holding a position
                position_size = self.portfolio['positions'].get(
                    self.data.name, 0)
                if position_size > 0:
                    self.execute_trade(
                        symbol=self.data.name, quantity=-position_size, price=close_price)
            prev_signal = signal

    def calculate_performance(self):

        pnl_list = []
        trades = self.trades

        # pair trades(entry/exit)
        for i in range(0, len(trades)-1, 2):
            entry = trades[i]
            exit = trades[i+1]
            trade_pnl = (exit['price']-entry['price']*entry['quantity'] -
                         (entry['commission']+exit['commission']))
            pnl_list.append(trade_pnl)

        total_pnl = np.sum(pnl_list)
        avg_trade_pnl = np.mean(pnl_list) if pnl_list else 0
        win_ratio = np.sum([p > 0 for p in pnl_list]) / \
            len(pnl_list) if pnl_list else 0

        return total_pnl, avg_trade_pnl, win_ratio

    def execute_trade(self, symbol, quantity, price):
        commission_rate = 0.001
        trade_cost = quantity * price
        commission = abs(trade_cost)*commission_rate
        # Update portfolio and execute trade; deduct cost and commission
        self.portfolio['cash'] -= trade_cost+commission

        # Update positions
        self.portfolio['positions'][symbol] = self.portfolio['positions'].get(
            symbol, 0) + quantity

        # Record the trade
        self.trades.append({
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'commission': commission,
            'date': self.current_date
        })

    def get_portfolio_value(self, price):
        # Calculate the current value of the portfolio
        positions_value = sum(self.portfolio['positions'].get(
            symbol, 0) * price for symbol in self.portfolio['positions'])
        return self.portfolio['cash'] + positions_value

    def get_portfolio_returns(self):
        # Calculate the daily portfolio returns
        portfolio_value = [self.get_portfolio_value(
            row['Close']) for _, row in self.data.iterrows()]
        returns = np.diff(portfolio_value) / portfolio_value[:-1]
        return returns

    def print_portfolio_summary(self):
        print('--- Portfolio Summary ---')
        print('Cash:', self.portfolio['cash'])
        print('Positions:')
        for symbol, quantity in self.portfolio['positions'].items():
            print(symbol + ':', quantity)

    def plot_portfolio_value(self):
        portfolio_values = [self.get_portfolio_value(
            row['Close']) for _, row in self.data.iterrows()]
        dates = self.data.index
        signals = self.data['signal']

        fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True,
                                 gridspec_kw={'height_ratios': [2, 1]})

    # --- Price Chart with Buy/Sell Markers ---
        axes[0].plot(dates, self.data['Close'],
                     label='Close Price', color='black', linewidth=1)

    # Identify trade points from trades
        buy_plotted = False
        sell_plotted = False
        for trade in self.trades:
            if trade['quantity'] > 0:
                axes[0].scatter(trade['date'], trade['price'],
                                marker='^', color='green', s=100)
            else:
                axes[0].scatter(trade['date'], trade['price'],
                                marker='v', color='red', s=100)
                buy_plotted = True

        axes[0].set_ylabel('Price')
        axes[0].set_title(f'{self.data.name} Price with Buy/Sell Signals')
        axes[0].grid(True)

    # --- Portfolio Value Over Time ---
        axes[1].plot(dates, portfolio_values,
                     label='Portfolio Value', color='blue')
        axes[1].set_ylabel('Portfolio Value')
        axes[1].set_xlabel('Date')
        axes[1].grid(True)

        plt.tight_layout()
        plt.show()


def main():
    print("Greetings! Enter the ticker for the security you'd like to explore:")
    # Implement Data Feed Integration
    # Load market data
    symbol = input("Ticker: ")
    start_date = input("Start Date (YYYY-MM-DD): ")
    end_date = input("End Date (YYYY-MM-DD): ")
    data = load_market_data(symbol, start_date, end_date)

    # Define Trading Strategies
    # Implement your trading strategies using the data
    print(data.columns)
    sma_short = ta.trend.sma_indicator(data['Close'], window=50)
    sma_long = ta.trend.sma_indicator(data['Close'], window=200)

    data['signal'] = np.where(sma_short > sma_long, 1, -1)
    data.name = symbol  # Set the name attribute for the data DataFrame

    # shift signals so we trade at the next bar instead of acting on the same candle
    data['signal'] = data['signal'].shift(1)
    # forces trades to happen 1 day later preventing hindsight
    data.dropna(inplace=True)

    engine = BacktestingEngine(data)
    initial_portfolio_value = engine.get_portfolio_value(data.iloc[0]['Close'])

    engine.run_backtest()

    # Step 8: Evaluate Performance
    final_portfolio_value = engine.get_portfolio_value(data.iloc[-1]['Close'])
    returns = engine.get_portfolio_returns()
    total_returns = (final_portfolio_value -
                     initial_portfolio_value) / initial_portfolio_value
    # Assuming 252 trading days in a year
    annualized_returns = (1 + total_returns) ** (252 / len(data)) - 1
    volatility = np.std(returns) * np.sqrt(252)
    sharpe_ratio = (annualized_returns - 0.02) / \
        volatility  # Assuming risk-free rate of 2%

    # Visualize Results
    engine.plot_portfolio_value()

    # Calculate and print performance metrics
    total_pnl, average_trade_return, win_ratio = engine.calculate_performance()
    print('--- Performance Metrics ---')
    print(f'Total Returns: {total_returns:.2%}')
    print(f'Annualized Returns: {annualized_returns:.2%}')
    print(f'Volatility: {volatility:.2%}')
    print(f'Sharpe Ratio: {sharpe_ratio:.2f}')
    print(f'Total P&L: {total_pnl:.2f}')
    print(f'Average Trade Return: {average_trade_return:.2%}')
    print(f'Win Ratio: {win_ratio:.2%}')

    # Compute drawdown
    portfolio_values = [engine.get_portfolio_value(
        row['Close']) for _, row in data.iterrows()]
    cum_max = np.maximum.accumulate(portfolio_values)
    drawdowns = (portfolio_values - cum_max) / cum_max
    max_drawdown = drawdowns.min()

    # CAGR
    years = len(data) / 252
    CAGR = (final_portfolio_value / initial_portfolio_value) ** (1 / years) - 1

    print(f'Max Drawdown: {max_drawdown:.2%}')
    print(f'CAGR: {CAGR:.2%}')


if __name__ == '__main__':
    main()

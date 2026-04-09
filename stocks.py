import yfinance as yf
import pandas as pd
import numpy as np

# ===== CONFIG =====
CONFIG = {
    "initial_account": 1200,
    "risk_per_trade": 0.01,
    "stop_pct": 0.04,
    "target_pct": 0.08,
    "hold_days": 7,
    "tickers": ["AAPL","MSFT","NVDA","AMZN","TSLA","META","GOOGL"]
}

# ===== RSI =====
def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100/(1+rs))

# ===== DATA =====
def prepare_data(ticker):
    df = yf.download(ticker, period="3y", auto_adjust=True, progress=False)

    if df is None or len(df) < 250:
        return None

    # Fix multi-index
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA200"] = df["Close"].rolling(200).mean()
    df["RSI"] = rsi(df["Close"])

    return df.dropna()

# ===== SIGNAL =====
def generate_signal(row, prev_close):
    ret_3m = (row["Close"] / prev_close) - 1

    if (
        row["Close"] > row["MA200"]
        and ret_3m > 0.10
        and row["Close"] < row["MA20"]
        and 35 < row["RSI"] < 50
    ):
        return 1
    return 0

# ===== ENGINE =====
class BacktestEngine:
    def __init__(self, config):
        self.account = config["initial_account"]
        self.risk_per_trade = config["risk_per_trade"]
        self.stop_pct = config["stop_pct"]
        self.target_pct = config["target_pct"]
        self.hold_days = config["hold_days"]

        self.equity_curve = []
        self.trade_returns = []

    def run(self, data):
        for i in range(200, len(data) - self.hold_days):

            row = data.iloc[i]
            prev_close = data["Close"].iloc[i-60]

            if pd.isna(row["RSI"]):  # FIXED
                continue

            signal = generate_signal(row, prev_close)

            if signal == 1:
                self.execute_trade(data, i, row["Close"])

    def execute_trade(self, data, index, entry_price):
        risk_amount = self.account * self.risk_per_trade

        stop_price = entry_price * (1 - self.stop_pct)
        target_price = entry_price * (1 + self.target_pct)

        future_prices = data["Close"].iloc[index+1:index+1+self.hold_days]

        outcome = None

        for price in future_prices:
            if price <= stop_price:
                outcome = -risk_amount
                break
            elif price >= target_price:
                outcome = risk_amount * 2
                break

        if outcome is None:
            exit_price = future_prices.iloc[-1]
            pnl_pct = (exit_price - entry_price) / entry_price
            outcome = pnl_pct * risk_amount

        prev_account = self.account
        self.account += outcome

        self.trade_returns.append(outcome / prev_account)
        self.equity_curve.append(self.account)

# ===== ANALYSIS =====
def analyze(engine):
    returns = np.array(engine.trade_returns)

    if len(returns) == 0:
        print("\nNo trades executed.")
        return

    wins = len(returns[returns > 0])
    total = len(returns)

    win_rate = wins / total
    sharpe = (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() != 0 else 0

    equity = np.array(engine.equity_curve)
    peak = np.maximum.accumulate(equity)
    drawdown = (equity - peak) / peak
    max_dd = drawdown.min()

    print("\n===== RESULTS =====")
    print("Final Account:", round(engine.account, 2))
    print("Trades:", total)
    print("Win Rate:", round(win_rate*100, 2), "%")
    print("Sharpe:", round(sharpe, 2))
    print("Max Drawdown:", round(max_dd*100, 2), "%")

# ===== MAIN =====
if __name__ == "__main__":
    engine = BacktestEngine(CONFIG)

    for ticker in CONFIG["tickers"]:
        print("Testing:", ticker)
        df = prepare_data(ticker)

        if df is not None:
            engine.run(df)

    analyze(engine)
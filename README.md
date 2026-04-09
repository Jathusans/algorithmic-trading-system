# algorithmic-trading-system
Python-based algorithmic trading system with backtesting, risk management, and performance evaluation using real market data.
# Algorithmic Trading System

## Overview
This project is a Python-based algorithmic trading system designed to develop and evaluate quantitative trading strategies using historical market data.

It integrates data ingestion, signal generation, risk management, and backtesting into a single workflow.

## Features
- Market data retrieval using yfinance
- Technical indicators (RSI, moving averages, momentum)
- Strategy-based signal generation
- Risk management (position sizing, stop-loss, take-profit)
- Custom backtesting engine
- Performance evaluation (Sharpe ratio, drawdown, win rate)

## Strategy
The strategy combines:
- Trend filtering using long-term moving averages
- Momentum signals based on returns
- Mean reversion signals using RSI

## Backtesting
A custom backtesting engine simulates trades over historical data, allowing evaluation of:
- Profitability
- Risk-adjusted returns
- Drawdowns

## Example Output
- Final account value
- Win rate
- Sharpe ratio
- Maximum drawdown

## Technologies
- Python
- pandas, NumPy
- yfinance

## Future Improvements
- Machine learning integration
- Portfolio optimisation
- Live trading system deployment

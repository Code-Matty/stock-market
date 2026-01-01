# Stock Market App

Welcome to the **Stock Market App**! This tool monitors, analyzes, and tracks stock market data in real-time.

## Project Overview

The **Stock Market App** is a Python-based command-line tool designed to:
*   Fetch stock data from **Yahoo Finance**.
*   Store metadata and historical records in **MongoDB**.
*   Perform deep technical analysis to distinguish between **Bull** and **Bear** market phases.

## Key Features

*   **Real-time Monitoring**: Continuous background loop updates stock prices.
*   **Deep Technical Analysis**: Automated evaluation using SMA, RSI, MACD, and Bollinger Bands.
*   **Interactive Shell**: Robust CLI to `find`, `save`, `analyze`, and manage monitoring.
*   **Data Persistence**: Efficient storage using MongoDB.

## Documentation

*   **[Installation Guide](prompt/Installation-Guide.md)**: Prerequisites and setup steps.
*   **[Usage Guide](prompt/Usage-Guide.md)**: details on CLI commands and Interactive Mode.
*   **[Architecture](prompt/Architecture.md)**: Overview of the modules (`main.py`, `data_fetcher.py`, `stock_analyzer.py`, `db_manager.py`).
*   **[Analysis Logic](prompt/Analysis-Logic.md)**: Detailed explanation of the Bull/Bear evaluation algorithm.
*   **[Contributing](prompt/Contributing.md)**: Guidelines for contributing to the code.

---
*Maintained by Code-Matty. Licensed under MIT License.*

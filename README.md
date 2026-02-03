# ⚡ The Quant's Cockpit: Automated Portfolio Optimization Engine

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-ff4b4b)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

> **An end-to-end financial analytics platform that ingests real-time market data, stores it in a SQL warehouse, and uses advanced mathematical modeling (Markowitz Optimization & Monte Carlo) to recommend optimal asset allocations.**

---

## 📸 Dashboard Preview

![Dashboard View](C:\Aryan\Project\The-Quant-s-Cockpit-\screenshots\MainPage.png)

---

## 🚀 Project Overview

**The Quant's Cockpit** is a sophisticated decision-support system designed to replace "emotional investing" with mathematical rigour. It bridges the gap between raw market data and actionable investment strategy.

While most stock trackers simply display price history, this engine acts as an automated analyst. It leverages **Modern Portfolio Theory (MPT)** to mathematically minimize risk while maximizing returns and uses stochastic modeling to stress-test portfolios against future market volatility.

### Key Capabilities
* **Automated Data Pipeline:** A custom ETL script fetches OHLCV data from Yahoo Finance and incrementally updates a local SQL database to ensure zero redundancy.
* **Quantitative "AI" Analyst:** Algorithms score assets based on Sharpe Ratio and Momentum, generating automatic "Buy/Sell" ratings.
* **Portfolio Optimization:** Uses `scipy.optimize` to solve for the Efficient Frontier and maximize the Sharpe Ratio.
* **Risk Forecasting:** Runs 1,000+ Monte Carlo simulations (Geometric Brownian Motion) to predict future portfolio performance and Value at Risk (VaR).

---

## 🛠️ Tech Stack & Architecture

| Component | Technologies Used |
| :--- | :--- |
| **Frontend / UI** | `Streamlit`, `Plotly Express`, `HTML/CSS` |
| **Data Engineering** | `SQLAlchemy` (ORM), `SQLite`, `Yfinance` |
| **Analytics & Math** | `Pandas`, `NumPy`, `SciPy` (Optimization) |
| **Visualization** | `Plotly Graph Objects` (Interactive Charts) |

### 📂 Directory Structure

```bash
Portfolio_Optimizer/
├── analytics/
│   ├── metrics.py          # Core financial logic (Volatility, Sharpe, MPT, Monte Carlo)
├── database/
│   ├── models.py           # SQL Schema definitions (Stocks, Prices)
│   ├── ingest.py           # ETL Pipeline (Incremental Data Fetching)
├── app.py                  # Main Streamlit Dashboard application
├── requirements.txt        # Project dependencies
└── finance.db              # Local SQL Database (Auto-generated)

```

---

## ⚙️ Installation & Setup

**1. Clone the Repository**

```bash
git clone [https://github.com/yourusername/quants-cockpit.git](https://github.com/yourusername/quants-cockpit.git)
cd quants-cockpit

```

**2. Install Dependencies**

```bash
pip install -r requirements.txt

```

**3. Initialize the Database**
Run the database setup to create tables and fetch the initial batch of data (50+ tickers).

```bash
# Create Tables
python -m database.models

# Run Ingestion Pipeline (Fetches ~5 years of history)
python -m database.ingest

```

**4. Launch the Dashboard**

```bash
python -m streamlit run app.py

```

---

## 📊 Features in Detail

### 1. 🏗️ Data Engineering Pipeline

* **Smart Ingestion:** The `ingest.py` script checks the database for the *last available date* for each stock and only fetches missing data. This reduces API load and speeds up updates.
* **Normalized Schema:** Data is stored in relational tables (`Stock` -> `StockPrice`) to allow for complex SQL queries.

### 2. 🧠 Quant AI Analyst

* The system calculates the **Sharpe Ratio** (Return per unit of Risk) for selected assets.
* **Logic:**
* `Sharpe > 2.0`: **STRONG BUY** (Exceptional risk-adjusted returns)
* `Sharpe > 1.0`: **BUY** (Solid performance)
* `Sharpe < 0`: **SELL** (Negative performance)



### 3. 🤖 Markowitz Optimization

* The engine simulates thousands of portfolio weight combinations.
* It mathematically identifies the "Tangency Portfolio" on the Efficient Frontier—the specific allocation that yields the highest mathematical return for the lowest risk.

### 4. 🔮 Monte Carlo Simulation

* Uses **Geometric Brownian Motion (GBM)** to simulate future price paths.
* Includes a **"Market Shock"** feature, allowing users to stress-test their portfolio against 2x or 3x volatility (simulating a market crash).

---

## 🚀 Future Improvements

* [ ] Migrate database to PostgreSQL/AWS RDS for cloud scalability.
* [ ] Implement NLP Sentiment Analysis on financial news to augment the "AI Analyst" score.
* [ ] Add "Backtesting" tab to test strategies against historical data.

---

### 👤 Author

**Aryan Patil**

* Master's in Data Science @ RIT
* [LinkedIn Profile](https://www.linkedin.com/in/aryanpatil18/)

```

```
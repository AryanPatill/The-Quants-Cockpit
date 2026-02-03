import pandas as pd
import numpy as np
from scipy.optimize import minimize
from sqlalchemy import create_engine

# 1. Connect to Database
def load_data():
    """
    Reads data from SQL and pivots it so:
    - Rows = Dates
    - Columns = Tickers
    - Values = Close Price
    """
    engine = create_engine('sqlite:///finance.db')
    
    # We use a SQL Join to get Ticker Names + Prices together
    query = """
    SELECT stocks.symbol, stock_prices.date, stock_prices.close 
    FROM stock_prices 
    JOIN stocks ON stock_prices.stock_id = stocks.id
    """
    
    df = pd.read_sql(query, engine)
    
    # Convert 'date' column to datetime objects
    df['date'] = pd.to_datetime(df['date'])
    
    # Pivot: Make symbols the columns
    df_pivot = df.pivot(index='date', columns='symbol', values='close')
    
    # Drop any rows with missing values (cleaning)
    df_pivot.dropna(inplace=True)
    
    return df_pivot

# 2. Financial Calculations
def calculate_metrics(df):
    """
    Input: DataFrame of Close Prices
    Output: DataFrame of Returns and Dictionary of Volatility
    """
    # Calculate Daily Returns (Percentage Change)
    # Formula: (Price_Today - Price_Yesterday) / Price_Yesterday
    returns = df.pct_change().dropna()
    
    # Calculate Annualized Volatility (Standard Deviation * Sqrt(252 trading days))
    # This tells us how "risky" or "bouncy" a stock is.
    volatility = returns.std() * np.sqrt(252)
    
    return returns, volatility

# --- TEST AREA (To ensure it works) ---
if __name__ == "__main__":
    print("--- Loading Data from Database ---")
    df_prices = load_data()
    print(f"Loaded {len(df_prices)} days of data.")
    print(df_prices.tail()) # Show last 5 rows

    print("\n--- Calculating Risk (Volatility) ---")
    daily_returns, vol = calculate_metrics(df_prices)
    
    # Display nicely
    print(vol.sort_values(ascending=False))


# ... (your existing code is above)

def optimize_portfolio(df):
    """
    Finds the optimal weights for the portfolio to maximize the Sharpe Ratio.
    """
    # 1. Calculate Expected Annual Returns and Covariance Matrix
    mu = df.pct_change().mean() * 252
    S = df.pct_change().cov() * 252

    # 2. Define the Objective Function (Negative Sharpe Ratio)
    # We want to MAXIMIZE Sharpe, but SciPy only MINIMIZES, so we minimize negative Sharpe.
    def negative_sharpe(weights):
        # Portfolio Return = Weights * Expected Returns
        p_ret = np.dot(weights, mu)
        # Portfolio Volatility = Sqrt(Weights * Covariance * Weights_Transpose)
        p_vol = np.sqrt(np.dot(weights.T, np.dot(S, weights)))
        
        # Sharpe Ratio (assuming 0% risk-free rate for simplicity)
        return - (p_ret / p_vol)

    # 3. Constraints & Bounds
    num_assets = len(df.columns)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1}) # Sum of weights must be 1 (100%)
    bounds = tuple((0, 1) for _ in range(num_assets))              # No short selling (0% to 100%)
    initial_guess = num_assets * [1. / num_assets]                 # Start with equal weights

    # 4. Run Optimization
    result = minimize(negative_sharpe, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    
    # 5. Return optimal weights as a Dictionary
    optimal_weights = dict(zip(df.columns, result.x))
    
    return optimal_weights


def run_monte_carlo(df, num_simulations=200, days=252):
    """
    Simulates future portfolio value using Geometric Brownian Motion.
    Returns: A DataFrame where columns are different simulation runs.
    """
    # 1. Get stats
    last_price = df.iloc[-1].mean() # Simplify: assume equal weight portfolio for simulation
    returns = df.pct_change().dropna()
    daily_vol = returns.std().mean()
    daily_return = returns.mean().mean()
    
    # 2. Setup simulation grid
    simulation_df = pd.DataFrame()
    
    # 3. Run simulations
    for x in range(num_simulations):
        count = 0
        price_series = []
        price = last_price * (1 + np.random.normal(0, daily_vol)) # Start with random shock
        price_series.append(price)
        
        for y in range(days):
            # Random shock based on volatility
            price = price_series[count] * (1 + np.random.normal(daily_return, daily_vol))
            price_series.append(price)
            count += 1
        
        simulation_df[x] = price_series
        
    return simulation_df
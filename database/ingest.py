import yfinance as yf
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
# Import the classes we made in the other file
from database.models import Stock, StockPrice, Base

# 1. Setup Database Connection
engine = create_engine('sqlite:///finance.db')
Session = sessionmaker(bind=engine)
session = Session()

def get_or_create_stock(symbol, name, sector):
    """
    Checks if stock exists in DB. If not, adds it. 
    Returns the Stock object (so we can get its ID).
    """
    stock = session.query(Stock).filter_by(symbol=symbol).first()
    if not stock:
        print(f"Adding new stock: {symbol}")
        stock = Stock(symbol=symbol, name=name, sector=sector)
        session.add(stock)
        session.commit()
    return stock

def update_price_history(symbol):
    """
    Smart Fetch:
    1. Check DB for the last date we have for this stock.
    2. Download only NEW data from Yahoo Finance.
    3. Save to DB.
    """
    stock = session.query(Stock).filter_by(symbol=symbol).first()
    if not stock:
        print(f"Error: Stock {symbol} not found in DB.")
        return

    # A. Find the last date in the database
    last_entry = session.query(func.max(StockPrice.date)).filter_by(stock_id=stock.id).scalar()
    
    if last_entry:
        # If we have data, start from the next day
        start_date = last_entry + timedelta(days=1)
        print(f"Updating {symbol} from {start_date}...")
    else:
        # If no data, get 5 years of history
        start_date = datetime.now() - timedelta(days=365*5)
        print(f"Fetching full history for {symbol}...")

    # B. Download data
    data = yf.download(symbol, start=start_date, progress=False)

    if data.empty:
        print(f"No new data for {symbol}.")
        return

    # C. Loop through rows and save to DB
    new_records = []
    for date, row in data.iterrows():
        # yfinance sometimes returns "Adj Close", we just use "Close"
        record = StockPrice(
            stock_id=stock.id,
            date=date.date(),
            open=float(row['Open'].iloc[0] if hasattr(row['Open'], 'iloc') else row['Open']),
            high=float(row['High'].iloc[0] if hasattr(row['High'], 'iloc') else row['High']),
            low=float(row['Low'].iloc[0] if hasattr(row['Low'], 'iloc') else row['Low']),
            close=float(row['Close'].iloc[0] if hasattr(row['Close'], 'iloc') else row['Close']),
            volume=int(row['Volume'].iloc[0] if hasattr(row['Volume'], 'iloc') else row['Volume'])
        )
        new_records.append(record)
    
    # Bulk insert is faster
    session.add_all(new_records)
    session.commit()
    print(f"Saved {len(new_records)} records for {symbol}.")

# ... (Keep all your functions like get_or_create_stock above this)

if __name__ == "__main__":
    # A professional list of 50+ assets across sectors
    sectors = {
        "Technology": ["AAPL", "MSFT", "GOOGL", "NVDA", "AMD", "INTC", "CRM", "ORCL"],
        "Finance": ["JPM", "BAC", "GS", "MS", "V", "MA", "BLK"],
        "Healthcare": ["JNJ", "PFE", "UNH", "LLY", "MRK"],
        "Consumer": ["AMZN", "TSLA", "WMT", "PG", "KO", "PEP", "MCD"],
        "Energy/Industrial": ["XOM", "CVX", "BA", "CAT", "GE"],
        "Indices/ETFs": ["SPY", "QQQ", "IWM", "GLD", "SLV", "TLT", "VNQ"],
        "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD"],
        "Forex": ["EURUSD=X", "GBPUSD=X", "JPY=X"]
    }

    print("--- Starting Enhanced Data Ingestion ---")
    
    for sector, tickers in sectors.items():
        print(f"\nProcessing Sector: {sector}")
        for symbol in tickers:
            # We treat the 'name' as the Sector for simple grouping later
            get_or_create_stock(symbol, name=symbol, sector=sector)
            update_price_history(symbol)
            
    print("\n--- Ingestion Complete. Database is ready! ---")
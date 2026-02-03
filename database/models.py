from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

# 1. Define the Base
Base = declarative_base()

# 2. Define the 'Stock' Table
class Stock(Base):
    __tablename__ = 'stocks'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, nullable=False) # e.g., "AAPL"
    name = Column(String)                                # e.g., "Apple Inc."
    sector = Column(String)                              # e.g., "Technology"
    
    # Relationship to prices (One Stock -> Many Prices)
    prices = relationship("StockPrice", back_populates="stock", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Stock(symbol='{self.symbol}', name='{self.name}')>"

# 3. Define the 'StockPrice' Table
class StockPrice(Base):
    __tablename__ = 'stock_prices'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False) # Foreign Key
    date = Column(Date, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    
    # Relationship back to stock
    stock = relationship("Stock", back_populates="prices")

    def __repr__(self):
        return f"<Price(symbol='{self.stock.symbol}', date='{self.date}', close='{self.close}')>"


# 4. Database Setup Function
def create_database():
    engine = create_engine('sqlite:///finance.db', echo=True)
    Base.metadata.create_all(engine)
    print("Database created successfully!")

if __name__ == "__main__":
    create_database()
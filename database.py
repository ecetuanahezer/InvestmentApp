"""
Creates the database and defines the FundValue model.
"""

from sqlalchemy import (
    UniqueConstraint,
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Date,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()


class FundValue(Base):
    """
    Stores daily values for each individual fund.
    Each (fund_code, date) pair is unique.
    """

    __tablename__ = "fund_values"
    id = Column(Integer, primary_key=True)
    fund_code = Column(String, index=True)
    fund_name = Column(String)
    date = Column(Date, default=datetime.date.today)
    value_tl = Column(Float)
    __table_args__ = (
        UniqueConstraint("fund_code", "date", name="unique_fund_per_day"),
    )


class AssetValue(Base):
    """
    Stores daily total values for each asset category (e.g., Precious Metals, Crypto, Physical Gold).
    Each date appears only once.
    """

    __tablename__ = "asset_values"
    id = Column(Integer, primary_key=True)
    date = Column(Date, default=datetime.date.today, unique=True)
    precious_metals_tl = Column(Float)
    crypto_tl = Column(Float)
    physical_gold_tl = Column(Float)


engine = create_engine("sqlite:///db/investments.db")
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)

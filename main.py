from fastapi import FastAPI, Query, HTTPException
from typing import Optional, List
import yfinance as yf
import pandas as pd
import fastapi.responses

fastapi.responses.JSONResponse.json_dumps_params = {"allow_nan": True}

app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI is working!"}

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

def safe_series_response(series):
    if series is None or (hasattr(series, "empty") and series.empty):
        return JSONResponse(content=jsonable_encoder([]))
    # Convert to DataFrame if it's a Series
    if isinstance(series, pd.Series):
        series = series.to_frame()
    # Ensure all columns are objects for proper replacement
    series = series.astype(object)
    series_clean = series.replace([pd.NA, float("inf"), float("-inf"), pd.NaT, None], None)
    series_clean = series_clean.where(pd.notnull(series_clean), None)
    return JSONResponse(content=jsonable_encoder(series_clean.reset_index().to_dict(orient="records")))

def safe_df_response(df):
    if df is None or df.empty:
        return JSONResponse(content=jsonable_encoder([]))
    df = df.astype(object)
    df_clean = df.replace([pd.NA, float("inf"), float("-inf"), pd.NaT, None], None)
    df_clean = df_clean.where(pd.notnull(df_clean), None)
    return JSONResponse(content=jsonable_encoder(df_clean.reset_index().to_dict(orient="records")))

@app.get("/ticker/{symbol}")
def get_ticker_info(symbol: str):
    try:
        return {"info": yf.Ticker(symbol).info}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/ticker/{symbol}/fast-info")
def get_fast_info(symbol: str):
    return yf.Ticker(symbol).fast_info

# @app.get("/ticker/{symbol}/calendar")
# def get_calendar(symbol: str):
#     return yf.Ticker(symbol).calendar

@app.get("/ticker/{symbol}/history")
def get_history(
    symbol: str,
    period: Optional[str] = "1mo",
    interval: Optional[str] = "1d",
    start: Optional[str] = None,
    end: Optional[str] = None
):
    try:
        t = yf.Ticker(symbol)
        df = t.history(start=start, end=end, period=period, interval=interval)
        return safe_series_response(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# @app.get("/ticker/{symbol}/dividends")
# def get_dividends(symbol: str):
#     return series_to_dict(yf.Ticker(symbol).dividends)

# @app.get("/ticker/{symbol}/splits")
# def get_splits(symbol: str):
#     return series_to_dict(yf.Ticker(symbol).splits)

# @app.get("/ticker/{symbol}/actions")
# def get_actions(symbol: str):
#     return safe_series_response(yf.Ticker(symbol).actions)

@app.get("/ticker/{symbol}/recommendations")
def get_recommendations(symbol: str):
    return safe_series_response(yf.Ticker(symbol).recommendations)

# @app.get("/ticker/{symbol}/earnings")
# def get_earnings(symbol: str):
#     return safe_series_response(yf.Ticker(symbol).earnings)

@app.get("/ticker/{symbol}/income-statement")
def get_income_stmt(symbol: str):
    return safe_series_response(yf.Ticker(symbol).income_stmt)

@app.get("/ticker/{symbol}/balance-sheet")
def get_balance_sheet(symbol: str):
    return safe_series_response(yf.Ticker(symbol).balance_sheet)

@app.get("/ticker/{symbol}/cash-flow")
def get_cash_flow(symbol: str):
    return safe_series_response(yf.Ticker(symbol).cashflow)

@app.get("/ticker/{symbol}/sustainability")
def get_sustainability(symbol: str):
    return safe_series_response(yf.Ticker(symbol).sustainability)

@app.get("/ticker/{symbol}/analyst-targets")
def get_analyst_targets(symbol: str):
    return yf.Ticker(symbol).analyst_price_targets

@app.get("/ticker/{symbol}/earnings-dates")
def get_earnings_dates(symbol: str, limit: int = 10):
    return safe_series_response(yf.Ticker(symbol).get_earnings_dates(limit=limit))

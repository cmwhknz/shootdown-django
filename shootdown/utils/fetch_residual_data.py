import datetime
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from .cbbc_sample_datasets import SAMPLE_RESIDUAL_DATA

# ──────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────

DATABASE_URL = "postgresql+psycopg://demo:demo@0.0.0.0:5432/cbbc"

# TODAY = datetime.date.today().strftime("%Y%m%d")
TODAY = "20260113"      # override for testing

DEMO = True


# ──────────────────────────────────────────────────────────────
# Main Function
# ──────────────────────────────────────────────────────────────

def fetch_residuals(date_str: str = TODAY) -> pd.DataFrame:
    """
    Fetch the latest HSI residual value data for the specified date.
    
    This function retrieves the most recent records for time 0929 (open) and 2330 (close)
    from the livedata_equivalent table, deduplicating by taking the row with the highest ID.

    Parameters:
        date_str (str): Date in 'YYYYMMDD' format (default: today)

    Returns:
        pd.DataFrame: DataFrame with columns [date, time, start, net, bullbear]
                      Empty DataFrame if no data or error occurs
    """

    if DEMO:
        if date_str in SAMPLE_RESIDUAL_DATA:
            
            df = pd.DataFrame(
                SAMPLE_RESIDUAL_DATA[date_str],
                columns=['date', 'time', 'start', 'net', 'bullbear']
            )
            return df
        else:
            print(f"No sample data found for {date_str}")
            return pd.DataFrame()


    # ── Real Database Mode ───────────────────────────────────────
    engine = create_engine(DATABASE_URL)

    query = text("""
        WITH latest AS (
            SELECT 
                date,
                time,
                start,
                net,
                bullbear,
                ROW_NUMBER() OVER (
                    PARTITION BY time, start, bullbear 
                    ORDER BY id DESC
                ) AS rn
            FROM cbbc
            WHERE date = :date_str
              AND time IN (929, 2330)
        )
        SELECT 
            date,
            time,
            start,
            net,
            bullbear
        FROM latest
        WHERE rn = 1
        ORDER BY time, start;
    """)

    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(
                query,
                conn,
                params={"date_str": date_str}
            )

        if df.empty:
            print(f"Warning: No residual data found for date {date_str}")
            return pd.DataFrame()

        print(f"Successfully fetched {len(df)} records for {date_str}")
        return df

    except SQLAlchemyError as e:
        print(f"Database connection/query error: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return pd.DataFrame()
    finally:
        engine.dispose()  


# ──────────────────────────────────────────────────────────────
# Execution Block
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Fetching residual data for date: {TODAY}")

    df = fetch_residuals()

    if not df.empty:
        print("\nResult (first few rows):")
        print(df.head())
        print("\nFull DataFrame shape:", df.shape)
    else:
        print("No data retrieved. Check date, connection, or table contents.")
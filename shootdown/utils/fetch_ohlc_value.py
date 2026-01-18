import datetime
import ast
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from .cbbc_sample_datasets import SAMPLE_OHLC_DATA

# ──────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────

DATABASE_URL = "postgresql+psycopg://demo:demo@0.0.0.0:5432/ohlc"

# TODAY = datetime.date.today().strftime("%Y%m%d")
TODAY = "20260113"      # override for testing

DEMO = True


# ──────────────────────────────────────────────────────────────
# Main Function
# ──────────────────────────────────────────────────────────────

def fetch_ohlc(date_str: str = TODAY) -> Optional[float] :
    """
    Fetch HSI OHLC values for the specified date.

    Parameters:
        date_str (str): Date in 'YYYYMMDD' format (default: today)

    Returns:
        List[float] [open, high, low, close] or None if failed/no data
    """

    if DEMO:
        if date_str in SAMPLE_OHLC_DATA:
            ohlc_value = SAMPLE_OHLC_DATA[date_str]

            return ohlc_value
        else:
            print(f"No sample data found for {date_str}")
            return None


    # ── Real Database Mode ───────────────────────────────────────
    engine = create_engine(DATABASE_URL)

    try:

        with engine.connect() as conn:
            query = text("""
                SELECT * 
                FROM ohlc 
                WHERE date = :today 
                ORDER BY id DESC
                LIMIT 1;
            """)

            result = conn.execute(query, {"today": date_str})
            row = result.fetchone()

            if row is None:
                print(f"No HSI data found for date {date_str}")
                return None

            # Parse the content field (assuming index 3 is the content column)
            ohlc_value = ast.literal_eval(row[3])

            return ohlc_value

    except SQLAlchemyError as e:
        print(f"Database error while fetching HSI data: {e}")
        return None
    except (IndexError, TypeError, ValueError) as e:
        print(f"Error parsing HSI content: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
    finally:
        engine.dispose()  

# ──────────────────────────────────────────────────────────────
# Execution Block
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Starting investment data query - Date: {TODAY}")

    ohlc_value = fetch_ohlc()

    if ohlc_value is not None:
        print(f"\nFinal HSI OHLC value: {ohlc_value}")
    else:
        print("\nFailed to retrieve valid HSI ohlc data.")
        print("Possible reasons:")
        print("  • No matching record for the date")
        print("  • Database connection issue")
        print("  • Parsing error in content field")
        print("Please verify date, connection, or data format.")
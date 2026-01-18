import pandas as pd
from dataclasses import dataclass, field
from typing import Optional

from .fetch_residual_data import fetch_residuals
from .fetch_ohlc_value import fetch_ohlc
from .build_position_data import build_position

@dataclass
class CBBCResult:
    """Container for all CBBC data"""
    date: str
    
    # Core data
    residual_df: Optional[pd.DataFrame] = None
    position_data: dict = field(default_factory=dict)
    
    # HSI OHLC
    hsi_open: float = 0.0
    hsi_high: float = 0.0
    hsi_low: float = 0.0
    hsi_close: float = 0.0


class CBBCBuilder:
    """
    Builder pattern class for constructing CBBC position analysis.
    Chainable methods for clean usage.
    """
    
    def __init__(self, date_str: str):
        self.result = CBBCResult(date=date_str)

    def load_data(self) -> 'CBBCBuilder':
        """
        Load residual value data and HSI OHLC values for the given date.
        Returns self for method chaining.
        """

        df_data = fetch_residuals(self.result.date)
        self.result.df_data = df_data

        ohlc_value = fetch_ohlc(self.result.date)
        self.result.hsi_high = ohlc_value[1]
        self.result.hsi_low = ohlc_value[2]
        self.result.hsi_close = ohlc_value[3]

        return self
    
    def build_positions(self) -> 'CBBCBuilder':
        positions = build_position(self.result.df_data, self.result.hsi_high, self.result.hsi_low, self.result.hsi_close)
        self.result.position_data = positions

        return self
    
    def get_cbbc_data(self) -> dict:
        return self.result.position_data

# ──────────────────────────────────────────────────────────────
# Execution Block
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cbbc = (
        CBBCBuilder("20260112")
        .load_data()
        .build_positions()
    )

    result = cbbc.get_cbbc_data()

    print(result)

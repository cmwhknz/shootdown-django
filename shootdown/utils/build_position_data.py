import pandas as pd

def build_position(
        df_data: pd.DataFrame,
        hsi_high: float,
        hsi_low: float,
        hsi_close: float
):
    """
    Build bear/bull position data structure for CBBC visualization.
    Returns dict ready for frontend/content consumption.
    """
    content = {
        'bear': {'range_label': [], 'net': []},
        'bull': {'range_label': [], 'net': []},
        'bear_min': 15,
        'bull_max': 15,
        'bear_call': 15,
        'bull_call': 15,
        'max': 0,
        'hsi_close': 0,
    }

    # ─── HSI Close────────────────────────────────────────
    content['hsi_close'] = hsi_close


    # ─── Split data ────────────────────────────────────────
    df_bear = df_data.loc[(df_data['bullbear'] == 'bear')].copy()
    df_bull = df_data.loc[(df_data['bullbear'] == 'bull')].copy()

    spread = 100
    now_str = 2330


    # ─── Bear side (upward from current price) ─────────────
    bear_range = [hsi_close]
    bear_remain = hsi_close % spread
    step = spread - bear_remain if bear_remain < spread / 2 else 2 * spread - bear_remain
    bear_range.append(int(round(hsi_close + step)))

    for _ in range(14):
        bear_range.append(bear_range[-1] + spread)

    bear_labels, bear_nets, bear_vol_codes, bear_vol_nets = [], [], [], []

    for i in range(15):
        r_from = bear_range[i]
        r_to = bear_range[i + 1]
        label = f"{int(round(r_from)):,} - {int(round(r_to)) - 1:,}"
        bear_labels.append(label)

        mask = (
            (df_bear['time'] <= int(now_str)) &
            (df_bear['start'] >= r_from) &
            (df_bear['start'] < r_to)
        )
        net = df_bear.loc[mask, 'net'].sum()
        bear_nets.append(round(net))

    # Assign to content
    content['bear'] = {
        'range_label': bear_labels,
        'net': bear_nets,
    }


    # ─── Bull side (downward from current price) ───────────
    bull_range = [hsi_close]
    bull_remain = spread - bear_remain

    # First downward step adjustment
    step_down = -bull_remain if bull_remain < spread / 2 else -bear_remain - spread
    bull_range.append(int(round(hsi_close + step_down)))

    # Fill up to 15 points (14 intervals)
    while len(bull_range) < 16:
        bull_range.append(bull_range[-1] - spread)

    bull_range.reverse()  # make it ascending order (lowest to highest)

    bull_labels = []
    bull_nets = []

    for i in range(15):
        r_from = bull_range[i]
        r_to = bull_range[i + 1]

        # Label formatting (special handling for the last range)
        if i == 14:
            label = f"{int(r_from):,} - {int(round(r_to)):,}"
        else:
            label = f"{int(r_from):,} - {int(r_to) - 1:,}"

        bull_labels.append(label)

        mask = (
            (df_bull['time'] <= int(now_str)) &
            (df_bull['start'] >= r_from) &
            (df_bull['start'] < r_to)
        )
        net = df_bull.loc[mask, 'net'].sum()
        bull_nets.append(int(round(net)))

    # Assign to content
    content['bull'] = {
        'range_label': bull_labels,
        'net': bull_nets,
    }


    # ─── No CBBC Area ───────────
    bear_min = float(df_data.loc[df_data['start'] == 5, 'net'].iloc[0]) if not df_data[df_data['start'] == 5].empty else 0
    bull_max = float(df_data.loc[df_data['start'] == 4, 'net'].iloc[0]) if not df_data[df_data['start'] == 4].empty else 0

    bear_min_pos = next((i for i in range(15) if bear_min < (bear_range[i + 1] - 1)),15)
    bull_max_pos = next((i for i in range(15) if bull_max > bull_range[14 - i]),15)

    # Assign to content
    content['bear_min'] = bear_min_pos
    content['bull_max'] = bull_max_pos


    # ─── Call Area ───────────
    bear_call_position = next((i for i in range(15) if hsi_high < float(bear_range[i + 1]) - 1), 15 )
    bull_call_position = next((i for i in range(15) if hsi_low > float(bull_range[14 - i])), 15 )

    # Assign to content
    content['bear_call'] = bear_call_position
    content['bull_call'] = bull_call_position


    # ─── Max Abs Value ───────────
    max_value = max(map(abs, bear_nets + bull_nets))

    # Assign to content
    content['max'] = max_value

    return content





    
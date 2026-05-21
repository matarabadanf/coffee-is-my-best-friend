import pandas as pd

def process_raw_data(data, users):
    if not data:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}, {}

    df = pd.DataFrame(data)
    
    # Ensure drink_id exists (fill with 1 for Coffee if missing)
    if "drink_id" not in df.columns:
        df["drink_id"] = 1
    else:
        df["drink_id"] = df["drink_id"].fillna(1)
    
    # Convert timestamps
    if not df.empty and "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"])
    
    # Separate Dataframes
    df_coffee = df[df["drink_id"] == 1]
    df_tea = df[df["drink_id"] == 2]
    
    # Calculate Scores
    coffee_scores = df_coffee.groupby("user_name")["value"].sum().to_dict()
    tea_scores = df_tea.groupby("user_name")["value"].sum().to_dict()

    return df, df_coffee, df_tea, coffee_scores, tea_scores

def get_cumulative_data(data, start_date, end_date, users, freq="D"):
    # 1. Expand range (reindex needs strict boundaries)
    full_index = pd.date_range(start=start_date, end=end_date, freq=freq)
    
    # 2. Filter first to minimize processing
    mask = (data["created_at"] >= start_date) & (data["created_at"] <= end_date)
    filtered_df = data.loc[mask]
    
    if filtered_df.empty:
        empty_df = pd.DataFrame(0, index=full_index, columns=users)
        return empty_df.cumsum()

    # Pivot to [Time, User] = Count
    pivot = filtered_df.pivot_table(index="created_at", columns="user_name", values="value", aggfunc="sum", fill_value=0)
    
    # 3. Ensure all users exist
    # Here, we ensure the known users are in columns. If 'Bea(tea)' was added, 
    # the calling function should make sure it passes it in the `users` list if needed.
    for u in users:
        if u not in pivot.columns:
            pivot[u] = 0
            
    # 4. Resample & Reindex
    resampled = pivot.resample(freq).sum()
    resampled = resampled.reindex(full_index, fill_value=0)
    
    # 5. Cumulative Sum
    cumulative = resampled.cumsum()
    
    # 6. Mask future dates to stop the line at "today"
    cumulative = cumulative.astype(float)
    
    # Get cutoff (Now)
    current_time = pd.Timestamp.now(tz=cumulative.index.tz).normalize()
    
    # Mask future dates
    cumulative.loc[cumulative.index > current_time] = None
    
    return cumulative

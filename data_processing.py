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

def get_expense_and_caffeine(coffee_scores, tea_scores):
    # Assumptions
    COFFEE_MG = 95
    COFFEE_COST = 2.50
    TEA_MG = 30
    TEA_COST = 1.50
    
    metrics = {}
    for user in set(list(coffee_scores.keys()) + list(tea_scores.keys())):
        coffees = coffee_scores.get(user, 0)
        teas = tea_scores.get(user, 0)
        
        total_mg = (coffees * COFFEE_MG) + (teas * TEA_MG)
        total_cost = (coffees * COFFEE_COST) + (teas * TEA_COST)
        
        metrics[user] = {"caffeine_mg": total_mg, "cost_eur": total_cost}
        
    return metrics

def get_gamification_metrics(df_coffee, df_tea, users):
    trophies = {
        "monthly_records": [],
        "caffeine_addict": None,
        "tea_purist": None,
        "streaks": {}
    }
    
    combined = pd.concat([df_coffee, df_tea]) if not df_coffee.empty or not df_tea.empty else pd.DataFrame()

    # Historical Monthly Records
    if not combined.empty:
        combined_copy = combined.copy()
        combined_copy["month_str"] = combined_copy["created_at"].dt.to_period("M").astype(str)
        months = sorted(combined_copy["month_str"].unique(), reverse=True)
        
        records = []
        for m in months:
            month_data = combined_copy[combined_copy["month_str"] == m]
            
            c_data = month_data[month_data["drink_id"] == 1]
            t_data = month_data[month_data["drink_id"] == 2]
            
            top_c = "-"
            if not c_data.empty:
                c_counts = c_data.groupby("user_name")["value"].sum()
                if not c_counts.empty:
                    top_c = f"{c_counts.idxmax()} ({int(c_counts.max())})"
                    
            top_t = "-"
            if not t_data.empty:
                t_counts = t_data.groupby("user_name")["value"].sum()
                if not t_counts.empty:
                    top_t = f"{t_counts.idxmax()} ({int(t_counts.max())})"
                    
            month_name = pd.to_datetime(m + "-01").strftime("%B %Y")
            records.append({
                "Month": month_name,
                "☕ Top Coffee Drinker": top_c,
                "🍵 Top Tea Drinker": top_t
            })
            
        trophies["monthly_records"] = records
            
    # Caffeine Addict (Most coffees in last 7 days)
    if not df_coffee.empty:
        seven_days_ago = pd.Timestamp.now(tz=df_coffee["created_at"].dt.tz) - pd.Timedelta(days=7)
        recent_coffees = df_coffee[df_coffee["created_at"] >= seven_days_ago]
        if not recent_coffees.empty:
            counts = recent_coffees.groupby("user_name")["value"].sum()
            if not counts.empty:
                trophies["caffeine_addict"] = counts.idxmax()
                
    # Tea Purist (Highest Tea-to-Coffee ratio)
    best_ratio = -1
    for user in users:
        c_count = len(df_coffee[df_coffee["user_name"] == user]) if not df_coffee.empty else 0
        t_count = len(df_tea[df_tea["user_name"] == user]) if not df_tea.empty else 0
        
        if t_count > 0:
            ratio = t_count / (c_count + 1) # Add 1 to avoid div by zero
            if ratio > best_ratio:
                best_ratio = ratio
                trophies["tea_purist"] = user

    # Streaks (Active consecutive days logging ANY drink)
    longest_streak_user = None
    longest_streak_val = 0
    for user in users:
        trophies["streaks"][user] = 0
        if not combined.empty:
            user_logs = combined[combined["user_name"] == user].copy()
            if not user_logs.empty:
                # Calculate Longest Historical Streak
                dates_asc = user_logs["created_at"].dt.normalize().drop_duplicates().sort_values().tolist()
                if dates_asc:
                    current_len = 1
                    max_len = 1
                    for i in range(1, len(dates_asc)):
                        if dates_asc[i] - dates_asc[i-1] == pd.Timedelta(days=1):
                            current_len += 1
                            if current_len > max_len:
                                max_len = current_len
                        else:
                            current_len = 1
                    if max_len > longest_streak_val:
                        longest_streak_val = max_len
                        longest_streak_user = user

                # Calculate Active Streak
                dates_desc = user_logs["created_at"].dt.normalize().drop_duplicates().sort_values(ascending=False).tolist()
                
                if not dates_desc:
                    continue
                    
                today = pd.Timestamp.now(tz=dates_desc[0].tz).normalize()
                if dates_desc[0] < today - pd.Timedelta(days=1):
                    continue # Streak is broken
                    
                streak = 1
                for i in range(1, len(dates_desc)):
                    if dates_desc[i-1] - dates_desc[i] == pd.Timedelta(days=1):
                        streak += 1
                    else:
                        break
                trophies["streaks"][user] = streak
                
    if longest_streak_user and longest_streak_val > 0:
        trophies["longest_historical_streak"] = {
            "user": longest_streak_user,
            "days": longest_streak_val
        }

    # Most Coffees in a Single Day
    if not df_coffee.empty:
        df_coffee_copy = df_coffee.copy()
        if df_coffee_copy["created_at"].dt.tz is None:
            df_coffee_copy["created_at"] = df_coffee_copy["created_at"].dt.tz_localize("UTC")
        df_coffee_copy["created_at"] = df_coffee_copy["created_at"].dt.tz_convert("Europe/Madrid")
        
        df_coffee_copy["date_str"] = df_coffee_copy["created_at"].dt.normalize().astype(str)
        daily_coffees = df_coffee_copy.groupby(["date_str", "user_name"])["value"].sum().reset_index()
        if not daily_coffees.empty:
            max_idx = daily_coffees["value"].idxmax()
            best_day = daily_coffees.loc[max_idx]
            trophies["most_coffees_in_a_day"] = {
                "user": best_day["user_name"],
                "count": int(best_day["value"]),
                "date": best_day["date_str"]
            }

    # --- Funny Stats (Timezone Aware: Europe/Madrid) ---
    trophies["funny_stats"] = {
        "night_owl": None,
        "early_bird": None,
        "speedrunner": None,
        "marathon": None,
        "balanced": None
    }
    
    if not combined.empty:
        df_local = combined.copy()
        if df_local["created_at"].dt.tz is None:
            df_local["created_at"] = df_local["created_at"].dt.tz_localize("UTC")
        df_local["created_at"] = df_local["created_at"].dt.tz_convert("Europe/Madrid")
        
        df_local["hour"] = df_local["created_at"].dt.hour
        
        # 1. Night Owl (20:00 to 04:00)
        night_owls = df_local[df_local["hour"].isin([20, 21, 22, 23, 0, 1, 2, 3])]
        if not night_owls.empty:
            trophies["funny_stats"]["night_owl"] = night_owls.groupby("user_name").size().idxmax()
            
        # 2. Early Bird (04:00 to 08:00)
        early_birds = df_local[df_local["hour"].isin([4, 5, 6, 7])]
        if not early_birds.empty:
            trophies["funny_stats"]["early_bird"] = early_birds.groupby("user_name").size().idxmax()
            
        # 3. Speedrunner & Marathon
        # Speedrunner: Most drinks in a single hour
        df_local["date_str"] = df_local["created_at"].dt.normalize().astype(str)
        hourly_counts = df_local.groupby(["user_name", "date_str", "hour"])["value"].sum().reset_index()
        
        if not hourly_counts.empty:
            max_idx = hourly_counts["value"].idxmax()
            best_hour = hourly_counts.loc[max_idx]
            if best_hour["value"] > 1: # Only award if more than 1
                trophies["funny_stats"]["speedrunner"] = {
                    "user": best_hour['user_name'],
                    "count": int(best_hour['value']),
                    "date": best_hour['date_str'],
                    "hour": int(best_hour['hour'])
                }
                
        # Marathon: Longest average time gap
        max_avg_gap = pd.Timedelta.min
        marathon_user = None
        
        for user in users:
            user_logs = df_local[df_local["user_name"] == user].sort_values("created_at")
            if len(user_logs) > 1:
                gaps = user_logs["created_at"].diff().dropna()
                valid_gaps = gaps[gaps >= pd.Timedelta(minutes=1)]
                
                if not valid_gaps.empty:
                    user_avg = valid_gaps.mean()
                    if user_avg > max_avg_gap:
                        max_avg_gap = user_avg
                        marathon_user = user
            
        if marathon_user:
            hours = int(max_avg_gap.total_seconds() / 3600)
            trophies["funny_stats"]["marathon"] = f"{marathon_user} ({hours}h avg gap)"
            
        # 4. Perfectly Balanced (Closest to 50/50 ratio)
        best_diff = 1.0
        balanced_user = None
        for user in users:
            user_logs = df_local[df_local["user_name"] == user]
            if not user_logs.empty and len(user_logs) > 4: # Need at least 5 drinks to judge
                c_count = len(user_logs[user_logs["drink_id"] == 1])
                t_count = len(user_logs[user_logs["drink_id"] == 2])
                total = c_count + t_count
                if total > 0:
                    diff = abs((c_count / total) - (t_count / total))
                    if diff < best_diff:
                        best_diff = diff
                        balanced_user = user
                        
        if balanced_user:
            trophies["funny_stats"]["balanced"] = balanced_user

    # --- New All-Time Records ---
    if not combined.empty:
        df_local["dayofweek"] = df_local["created_at"].dt.dayofweek
        
        df_local["year_week"] = df_local["created_at"].dt.strftime("%Y-%W")
        
        # 1. Monday Grump
        mondays = df_local[(df_local["dayofweek"] == 0) & (df_local["drink_id"] == 1)]
        if not mondays.empty:
            counts = mondays.groupby("user_name")["value"].sum()
            if not counts.empty:
                trophies["monday_grump"] = {"user": counts.idxmax(), "count": int(counts.max())}
                
        # 2. Weekend Warrior
        weekends = df_local[df_local["dayofweek"].isin([5, 6])]
        if not weekends.empty:
            weekly_sums = weekends.groupby(["user_name", "year_week"])["value"].sum().reset_index()
            averages = weekly_sums.groupby("user_name")["value"].mean()
            if not averages.empty:
                trophies["weekend_warrior"] = {"user": averages.idxmax(), "count": round(averages.max(), 1)}
                
        # 2b. Weekday Warrior
        weekdays = df_local[df_local["dayofweek"].isin([0, 1, 2, 3, 4])]
        if not weekdays.empty:
            weekly_sums = weekdays.groupby(["user_name", "year_week"])["value"].sum().reset_index()
            averages = weekly_sums.groupby("user_name")["value"].mean()
            if not averages.empty:
                trophies["weekday_warrior"] = {"user": averages.idxmax(), "count": round(averages.max(), 1)}
                
        # 3. Longest Dry Spell
        max_gap = pd.Timedelta.min
        quitter_user = None
        for user in users:
            user_logs = df_local[df_local["user_name"] == user].sort_values("created_at")
            if len(user_logs) > 1:
                gaps = user_logs["created_at"].diff().dropna()
                user_max = gaps.max()
                if user_max > max_gap:
                    max_gap = user_max
                    quitter_user = user
        if quitter_user and max_gap > pd.Timedelta(days=1):
            trophies["dry_spell"] = {"user": quitter_user, "days": max_gap.days}
            
        # 4. Burning the Midnight Oil
        late_night = df_local[df_local["hour"].isin([0, 1, 2, 3, 4])].copy()
        if not late_night.empty:
            late_night["minute"] = late_night["created_at"].dt.minute
            latest_drink = late_night.sort_values(by=["hour", "minute"], ascending=[False, False]).iloc[0]
            trophies["midnight_oil"] = {
                "user": latest_drink["user_name"],
                "time": latest_drink["created_at"].strftime("%H:%M")
            }
            
        # 5. The Monogamist
        monogamist_user = None
        monogamist_streak = 0
        monogamist_drink = None
        for user in users:
            user_logs = df_local[df_local["user_name"] == user].sort_values("created_at")
            if not user_logs.empty:
                drinks = user_logs["drink_id"].tolist()
                current_streak = 1
                current_drink = drinks[0]
                for i in range(1, len(drinks)):
                    if drinks[i] == current_drink:
                        current_streak += 1
                        if current_streak > monogamist_streak:
                            monogamist_streak = current_streak
                            monogamist_user = user
                            monogamist_drink = "Coffee" if current_drink == 1 else "Tea"
                    else:
                        current_drink = drinks[i]
                        current_streak = 1
        if monogamist_user and monogamist_streak > 1:
            trophies["monogamist"] = {"user": monogamist_user, "streak": monogamist_streak, "drink": monogamist_drink}

        # 6. Afternoon Slump (14:00 - 16:59)
        afternoons = df_local[df_local["hour"].isin([14, 15, 16])]
        if not afternoons.empty:
            counts = afternoons.groupby("user_name")["value"].sum()
            if not counts.empty:
                trophies["afternoon_slump"] = {"user": counts.idxmax(), "count": int(counts.max())}

    return trophies

import random

def get_user_titles(user, trophies):
    titles = []
    
    if trophies.get("caffeine_addict") == user: titles.append("☕ Caffeine Addict")
    if trophies.get("tea_purist") == user: titles.append("🍵 Tea Purist")
    
    lhs = trophies.get("longest_historical_streak")
    if lhs and isinstance(lhs, dict) and lhs.get("user") == user:
        titles.append(f"🔥 Longest Streak ({lhs.get('days')} days)")
        
    mcid = trophies.get("most_coffees_in_a_day")
    if mcid and isinstance(mcid, dict) and mcid.get("user") == user:
        titles.append(f"🚀 Most in a Day ({mcid.get('count')})")
        
    fs = trophies.get("funny_stats", {})
    if fs.get("night_owl") == user: titles.append("🦉 Night Owl")
    if fs.get("early_bird") == user: titles.append("🌅 Early Bird")
    
    speed = fs.get("speedrunner")
    if speed and isinstance(speed, dict) and speed.get("user") == user:
        titles.append(f"⚡ Speedrunner ({speed.get('count')}/hr)")
        
    mara = fs.get("marathon")
    if mara and isinstance(mara, str) and mara.startswith(user):
        titles.append("🐢 Marathon Drinker")
        
    if fs.get("balanced") == user: titles.append("⚖️ Perfectly Balanced")
    
    mg = trophies.get("monday_grump")
    if mg and isinstance(mg, dict) and mg.get("user") == user: titles.append("😠 Monday Grump")
    
    ww = trophies.get("weekend_warrior")
    if ww and isinstance(ww, dict) and ww.get("user") == user: titles.append("⚔️ Weekend Warrior")
    
    wd = trophies.get("weekday_warrior")
    if wd and isinstance(wd, dict) and wd.get("user") == user: titles.append("👔 Weekday Warrior")
    
    ds = trophies.get("dry_spell")
    if ds and isinstance(ds, dict) and ds.get("user") == user: titles.append("🏜️ Longest Dry Spell")
    
    mo = trophies.get("midnight_oil")
    if mo and isinstance(mo, dict) and mo.get("user") == user: titles.append("🕯️ Midnight Oil")
    
    mono = trophies.get("monogamist")
    if mono and isinstance(mono, dict) and mono.get("user") == user: titles.append(f"💍 The Monogamist")
    
    asl = trophies.get("afternoon_slump")
    if asl and isinstance(asl, dict) and asl.get("user") == user: titles.append("😴 Afternoon Slump")
    
    if not titles:
        return "Alicia would not be proud"
        
    return random.choice(titles)

import pandas as pd

def compute_monarch_hall_of_fame(df_coffee, df_tea, users, transactions=None):
    """
    Computes complete dynasty lineage and Hall of Fame for the 4 global monarch thrones:
    - Lists all users who have ever held each throne
    - Highlights current reigning monarchs
    - Displays last held dates and peak stats for all historical title holders
    """
    combined = pd.concat([df_coffee, df_tea]) if not df_coffee.empty or not df_tea.empty else pd.DataFrame()
    
    # 1. Caffeine Emperor (Weekly Coffee Monarch)
    caffeine_hof = []
    if not df_coffee.empty:
        df_c = df_coffee.copy()
        df_c["week_str"] = df_c["created_at"].dt.strftime("%Y-W%W")
        weekly_groups = df_c.groupby(["week_str", "user_name"])["value"].sum().unstack(fill_value=0)
        
        user_weekly_wins = {u: 0 for u in users}
        user_last_reign_date = {u: None for u in users}
        user_peak_weekly = {u: 0 for u in users}
        
        for w_str, row in weekly_groups.iterrows():
            top_user = row.idxmax()
            top_val = row.max()
            if top_val > 0:
                user_weekly_wins[top_user] += 1
                w_logs = df_c[(df_c["week_str"] == w_str) & (df_c["user_name"] == top_user)]
                if not w_logs.empty:
                    user_last_reign_date[top_user] = w_logs["created_at"].max()
            for u in users:
                user_peak_weekly[u] = max(user_peak_weekly[u], int(row.get(u, 0)))
                
        seven_days_ago = pd.Timestamp.now(tz=df_c["created_at"].dt.tz) - pd.Timedelta(days=7)
        recent_c = df_c[df_c["created_at"] >= seven_days_ago]
        cur_caff_holder = recent_c.groupby("user_name")["value"].sum().idxmax() if not recent_c.empty else None

        for u in users:
            if user_weekly_wins[u] > 0 or user_peak_weekly[u] > 0:
                is_cur = (u == cur_caff_holder)
                last_dt = user_last_reign_date[u]
                last_held_str = "👑 Currently Reigning" if is_cur else (
                    last_dt.strftime("%b %d, %Y") if pd.notnull(last_dt) else "Historical Record"
                )
                caffeine_hof.append({
                    "user": u,
                    "is_current": is_cur,
                    "weeks_won": user_weekly_wins[u],
                    "peak_weekly_coffees": user_peak_weekly[u],
                    "last_held": last_held_str,
                    "last_held_dt": last_dt
                })
        caffeine_hof.sort(key=lambda x: (x["is_current"], x["weeks_won"]), reverse=True)

    # 2. Tea Dynasty Sovereign (Tea Purist)
    tea_hof = []
    if not combined.empty:
        cur_tea_holder = None
        best_ratio = -1
        for u in users:
            c_cnt = len(df_coffee[df_coffee["user_name"] == u]) if not df_coffee.empty else 0
            t_cnt = len(df_tea[df_tea["user_name"] == u]) if not df_tea.empty else 0
            if t_cnt > 0:
                r = t_cnt / (c_cnt + 1)
                if r > best_ratio:
                    best_ratio = r
                    cur_tea_holder = u

        for u in users:
            t_logs = df_tea[df_tea["user_name"] == u] if not df_tea.empty else pd.DataFrame()
            t_count = len(t_logs)
            if t_count > 0:
                is_cur = (u == cur_tea_holder)
                last_dt = t_logs["created_at"].max()
                last_held_str = "👑 Currently Reigning" if is_cur else last_dt.strftime("%b %d, %Y")
                c_cnt = len(df_coffee[df_coffee["user_name"] == u]) if not df_coffee.empty else 0
                ratio = round(t_count / (c_cnt + 1), 2)
                tea_hof.append({
                    "user": u,
                    "is_current": is_cur,
                    "tea_count": t_count,
                    "tea_ratio": ratio,
                    "last_held": last_held_str,
                    "last_held_dt": last_dt
                })
        tea_hof.sort(key=lambda x: (x["is_current"], x["tea_ratio"]), reverse=True)

    # 3. Sub-Zero Monarch (Iced Beverage Master)
    ice_hof = []
    if not combined.empty and "drink_id" in combined.columns:
        iced_logs = combined[combined["drink_id"].isin([3, 4])]
        if not iced_logs.empty:
            ice_counts = iced_logs.groupby("user_name")["value"].sum().to_dict()
            top_ice_user = max(ice_counts, key=ice_counts.get) if ice_counts else None
            for u in users:
                u_ice_logs = iced_logs[iced_logs["user_name"] == u]
                if not u_ice_logs.empty:
                    cnt = int(ice_counts.get(u, 0))
                    is_cur = (u == top_ice_user)
                    last_dt = u_ice_logs["created_at"].max()
                    last_held_str = "👑 Currently Reigning" if is_cur else last_dt.strftime("%b %d, %Y")
                    ice_hof.append({
                        "user": u,
                        "is_current": is_cur,
                        "iced_count": cnt,
                        "last_held": last_held_str,
                        "last_held_dt": last_dt
                    })
            ice_hof.sort(key=lambda x: (x["is_current"], x["iced_count"]), reverse=True)

    # 4. Combustion Monarch (Warp Speed / 400+ mg Days)
    combustion_hof = []
    if not combined.empty:
        caff_map = {1: 95, 3: 95, 2: 35, 4: 35}
        comb_copy = combined.copy()
        comb_copy["caff_mg"] = comb_copy["drink_id"].map(caff_map).fillna(50)
        if comb_copy["created_at"].dt.tz is None:
            comb_copy["created_at"] = comb_copy["created_at"].dt.tz_localize("UTC")
        comb_copy["madrid_dt"] = comb_copy["created_at"].dt.tz_convert("Europe/Madrid")
        comb_copy["date"] = comb_copy["madrid_dt"].dt.date
        
        daily_caff = comb_copy.groupby(["user_name", "date"])["caff_mg"].sum().reset_index()
        on_fire_days = daily_caff[daily_caff["caff_mg"] >= 400]
        
        top_fire_user = None
        if not on_fire_days.empty:
            fire_counts = on_fire_days.groupby("user_name")["date"].count().to_dict()
            top_fire_user = max(fire_counts, key=fire_counts.get) if fire_counts else None
        else:
            fire_counts = {}

        for u in users:
            u_fire = on_fire_days[on_fire_days["user_name"] == u]
            cnt = int(fire_counts.get(u, 0))
            if cnt > 0:
                is_cur = (u == top_fire_user)
                last_d = u_fire["date"].max()
                last_held_str = "👑 Currently Reigning" if is_cur else pd.to_datetime(last_d).strftime("%b %d, %Y")
                combustion_hof.append({
                    "user": u,
                    "is_current": is_cur,
                    "fire_days": cnt,
                    "last_held": last_held_str,
                    "last_held_dt": pd.to_datetime(last_d)
                })
        combustion_hof.sort(key=lambda x: (x["is_current"], x["fire_days"]), reverse=True)

    caff_monarch_dict = {
        "title": "👑 Caffeine Monarch",
        "subtitle": "Weekly Caffeine Champion",
        "metric_label": "Weeks Crowned",
        "hall_of_fame": caffeine_hof
    }

    return {
        "caffeine_monarch": caff_monarch_dict,
        "caffeine_emperor": caff_monarch_dict,
        "tea_sovereign": {
            "title": "🍵 Tea Dynasty Sovereign",
            "subtitle": "Highest Tea Ratio Dedication",
            "metric_label": "Tea Ratio",
            "hall_of_fame": tea_hof
        },
        "ice_monarch": {
            "title": "🧊 Sub-Zero Monarch",
            "subtitle": "Master of Cold Brews & Iced Teas",
            "metric_label": "Iced Drinks",
            "hall_of_fame": ice_hof
        },
        "combustion_monarch": {
            "title": "🔥 Combustion Monarch",
            "subtitle": "Warp Speed Overclock (400+ mg Days)",
            "metric_label": "On-Fire Days",
            "hall_of_fame": combustion_hof
        }
    }

def compute_all_trophy_hall_of_fames(df_coffee, df_tea, users, transactions=None):
    """Computes full crew breakdowns and rankings across all milestone and style trophies."""
    combined = pd.concat([df_coffee, df_tea]) if not df_coffee.empty or not df_tea.empty else pd.DataFrame()
    if not combined.empty:
        if combined["created_at"].dt.tz is None:
            combined["created_at"] = combined["created_at"].dt.tz_localize("UTC")
        combined["local_dt"] = combined["created_at"].dt.tz_convert("Europe/Madrid")
        combined["hour"] = combined["local_dt"].dt.hour
        combined["dayofweek"] = combined["local_dt"].dt.dayofweek
        combined["date"] = combined["local_dt"].dt.date
    else:
        combined["local_dt"] = []
        combined["hour"] = []
        combined["dayofweek"] = []
        combined["date"] = []

    res = {}
    
    # 1. Streak Sovereign
    streak_records = []
    for u in users:
        u_logs = combined[combined["user_name"] == u].copy() if not combined.empty else pd.DataFrame()
        best_streak = 0
        current_streak = 0
        if not u_logs.empty:
            dates_asc = u_logs["local_dt"].dt.normalize().drop_duplicates().sort_values().tolist()
            if dates_asc:
                cur_len = 1
                best_streak = 1
                for i in range(1, len(dates_asc)):
                    if dates_asc[i] - dates_asc[i-1] == pd.Timedelta(days=1):
                        cur_len += 1
                        if cur_len > best_streak:
                            best_streak = cur_len
                    else:
                        cur_len = 1
            
            dates_desc = u_logs["local_dt"].dt.normalize().drop_duplicates().sort_values(ascending=False).tolist()
            if dates_desc:
                today = pd.Timestamp.now(tz=dates_desc[0].tz).normalize()
                if dates_desc[0] >= today - pd.Timedelta(days=1):
                    cur_s = 1
                    for i in range(1, len(dates_desc)):
                        if dates_desc[i-1] - dates_desc[i] == pd.Timedelta(days=1):
                            cur_s += 1
                        else:
                            break
                    current_streak = cur_s
        streak_records.append({"user": u, "best_streak": best_streak, "current_streak": current_streak})
    streak_records.sort(key=lambda x: x["best_streak"], reverse=True)
    res["streak_sovereign"] = streak_records

    # 2. Velocity Monarch (Most Coffees in a Single Day)
    velocity_records = []
    if not df_coffee.empty:
        df_c = df_coffee.copy()
        if df_c["created_at"].dt.tz is None:
            df_c["created_at"] = df_c["created_at"].dt.tz_localize("UTC")
        df_c["local_date"] = df_c["created_at"].dt.tz_convert("Europe/Madrid").dt.date
        for u in users:
            u_c = df_c[df_c["user_name"] == u]
            if not u_c.empty:
                daily = u_c.groupby("local_date")["value"].sum()
                max_val = int(daily.max())
                best_date = str(daily.idxmax())
                velocity_records.append({"user": u, "max_day": max_val, "best_date": best_date})
            else:
                velocity_records.append({"user": u, "max_day": 0, "best_date": "-"})
    velocity_records.sort(key=lambda x: x["max_day"], reverse=True)
    res["velocity_monarch"] = velocity_records

    # 3. The Monogamist (Longest Consecutive Single-Beverage Loyalty)
    monogamist_records = []
    for u in users:
        u_logs = combined[combined["user_name"] == u].sort_values("created_at") if not combined.empty else pd.DataFrame()
        best_streak = 0
        best_drink = "None"
        if not u_logs.empty:
            drinks = u_logs["drink_id"].tolist()
            cur_s = 1
            cur_d = drinks[0]
            best_streak = 1
            best_drink = "Coffee" if cur_d in [1, 3] else "Tea"
            for i in range(1, len(drinks)):
                if drinks[i] == cur_d:
                    cur_s += 1
                    if cur_s > best_streak:
                        best_streak = cur_s
                        best_drink = "Coffee" if cur_d in [1, 3] else "Tea"
                else:
                    cur_d = drinks[i]
                    cur_s = 1
        monogamist_records.append({"user": u, "streak": best_streak, "drink": best_drink})
    monogamist_records.sort(key=lambda x: x["streak"], reverse=True)
    res["monogamist"] = monogamist_records

    # 4. Monday Grump (Most Caffeine on Mondays)
    monday_records = []
    mondays = combined[(combined["dayofweek"] == 0) & (combined["drink_id"].isin([1, 3]))] if not combined.empty else pd.DataFrame()
    for u in users:
        u_mon = mondays[mondays["user_name"] == u] if not mondays.empty else pd.DataFrame()
        cnt = int(u_mon["value"].sum()) if not u_mon.empty else 0
        monday_records.append({"user": u, "count": cnt})
    monday_records.sort(key=lambda x: x["count"], reverse=True)
    res["monday_grump"] = monday_records

    # 5. Night Owl (20:00 to 04:00)
    night_records = []
    night_logs = combined[combined["hour"].isin([20, 21, 22, 23, 0, 1, 2, 3])] if not combined.empty else pd.DataFrame()
    for u in users:
        u_night = night_logs[night_logs["user_name"] == u] if not night_logs.empty else pd.DataFrame()
        total_u = len(combined[combined["user_name"] == u]) if not combined.empty else 0
        cnt = len(u_night)
        pct = round((cnt / total_u * 100), 1) if total_u > 0 else 0.0
        night_records.append({"user": u, "count": cnt, "pct": pct})
    night_records.sort(key=lambda x: x["count"], reverse=True)
    res["night_owl"] = night_records

    # 6. Early Bird (04:00 to 08:00)
    early_records = []
    early_logs = combined[combined["hour"].isin([4, 5, 6, 7])] if not combined.empty else pd.DataFrame()
    for u in users:
        u_early = early_logs[early_logs["user_name"] == u] if not early_logs.empty else pd.DataFrame()
        total_u = len(combined[combined["user_name"] == u]) if not combined.empty else 0
        cnt = len(u_early)
        pct = round((cnt / total_u * 100), 1) if total_u > 0 else 0.0
        early_records.append({"user": u, "count": cnt, "pct": pct})
    early_records.sort(key=lambda x: x["count"], reverse=True)
    res["early_bird"] = early_records

    # 7. Midnight Oil (Absolute Latest Logged Timestamp)
    midnight_records = []
    late_hours = combined[combined["hour"].isin([0, 1, 2, 3, 4])] if not combined.empty else pd.DataFrame()
    for u in users:
        u_late = late_hours[late_hours["user_name"] == u] if not late_hours.empty else pd.DataFrame()
        if not u_late.empty:
            u_late_copy = u_late.copy()
            u_late_copy["minute"] = u_late_copy["local_dt"].dt.minute
            latest_row = u_late_copy.sort_values(by=["hour", "minute"], ascending=[False, False]).iloc[0]
            t_str = latest_row["local_dt"].strftime("%H:%M")
            midnight_records.append({"user": u, "latest_time": t_str, "sort_val": int(latest_row["hour"] * 60 + latest_row["minute"])})
        else:
            midnight_records.append({"user": u, "latest_time": "None", "sort_val": -1})
    midnight_records.sort(key=lambda x: x["sort_val"], reverse=True)
    res["midnight_oil"] = midnight_records

    # 8. Marathon Drinker (Average Time Gap)
    marathon_records = []
    for u in users:
        u_logs = combined[combined["user_name"] == u].sort_values("created_at") if not combined.empty else pd.DataFrame()
        if len(u_logs) > 1:
            gaps = u_logs["created_at"].diff().dropna()
            valid_gaps = gaps[gaps >= pd.Timedelta(minutes=1)]
            if not valid_gaps.empty:
                avg_hours = round(valid_gaps.mean().total_seconds() / 3600, 1)
                marathon_records.append({"user": u, "avg_hours": avg_hours})
            else:
                marathon_records.append({"user": u, "avg_hours": 0.0})
        else:
            marathon_records.append({"user": u, "avg_hours": 0.0})
    marathon_records.sort(key=lambda x: x["avg_hours"], reverse=True)
    res["marathon_drinker"] = marathon_records

    # 9. Equilibrium Monarch (Coffee vs Tea balance)
    equil_records = []
    for u in users:
        u_logs = combined[combined["user_name"] == u] if not combined.empty else pd.DataFrame()
        c_cnt = len(u_logs[u_logs["drink_id"].isin([1, 3])]) if not u_logs.empty else 0
        t_cnt = len(u_logs[u_logs["drink_id"].isin([2, 4])]) if not u_logs.empty else 0
        tot = c_cnt + t_cnt
        if tot > 0:
            c_pct = round((c_cnt / tot) * 100)
            t_pct = round((t_cnt / tot) * 100)
            diff = abs(c_pct - 50)
            equil_records.append({"user": u, "c_pct": c_pct, "t_pct": t_pct, "diff": diff})
        else:
            equil_records.append({"user": u, "c_pct": 50, "t_pct": 50, "diff": 999})
    equil_records.sort(key=lambda x: x["diff"])
    res["equilibrium_monarch"] = equil_records

    return res

import pandas as pd
import random
from world_data import compute_passport_stats, is_coffee_capital
from gamification.achievements import ACHIEVEMENT_TIERS, SECRET_FEATS, ACHIEVEMENTS_START_DATE
from gamification.hall_of_fame import compute_monarch_hall_of_fame, compute_all_trophy_hall_of_fames

def get_gamification_metrics(df_coffee, df_tea, users, transactions=None, achievements_start_date=ACHIEVEMENTS_START_DATE):
    """
    Computes all gamification metrics, monarch thrones, personal milestone tiers, and secret feats.
    - All-time historical records (monthly crowns, all-time highest streaks, Hall of Fame) use all logs.
    - Active personal achievement tiers, secret feats, and seasonal streaks count from achievements_start_date (tomorrow's UI 2.0 release date).
    """
    trophies = {
        "monthly_records": [],
        "caffeine_addict": None,
        "tea_purist": None,
        "ice_monarch": None,
        "combustion_monarch": None,
        "streaks": {},
        "personal_achievements": {},
        "secret_feats": {}
    }
    
    combined = pd.concat([df_coffee, df_tea]) if not df_coffee.empty or not df_tea.empty else pd.DataFrame()

    # 1. Historical Monthly Records (All-time)
    if not combined.empty:
        combined_copy = combined.copy()
        combined_copy["month_str"] = combined_copy["created_at"].dt.strftime("%Y-%m")
        months = sorted(combined_copy["month_str"].unique(), reverse=True)
        
        records = []
        for m in months:
            month_data = combined_copy[combined_copy["month_str"] == m]
            
            c_data = month_data[month_data["drink_id"].isin([1, 3])]
            t_data = month_data[month_data["drink_id"].isin([2, 4])]
            
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
                "☕ Coffee Monarch": top_c,
                "🍵 Tea Monarch": top_t
            })
            
        trophies["monthly_records"] = records
            
    # 2. Reigning Monarchs
    # Caffeine Monarch of the Week (Most coffees in last 7 days)
    if not df_coffee.empty:
        seven_days_ago = pd.Timestamp.now(tz=df_coffee["created_at"].dt.tz) - pd.Timedelta(days=7)
        recent_coffees = df_coffee[df_coffee["created_at"] >= seven_days_ago]
        if not recent_coffees.empty:
            counts = recent_coffees.groupby("user_name")["value"].sum()
            if not counts.empty:
                trophies["caffeine_addict"] = counts.idxmax()
                
    # Tea Monarch / Purist (Highest Tea-to-Coffee ratio)
    best_ratio = -1
    for user in users:
        c_count = len(df_coffee[df_coffee["user_name"] == user]) if not df_coffee.empty else 0
        t_count = len(df_tea[df_tea["user_name"] == user]) if not df_tea.empty else 0
        
        if t_count > 0:
            ratio = t_count / (c_count + 1)
            if ratio > best_ratio:
                best_ratio = ratio
                trophies["tea_purist"] = user

    # Sub-Zero Monarch (Most Iced Drinks all-time)
    if not combined.empty and "drink_id" in combined.columns:
        iced_logs = combined[combined["drink_id"].isin([3, 4])]
        if not iced_logs.empty:
            ice_counts = iced_logs.groupby("user_name")["value"].sum()
            if not ice_counts.empty:
                trophies["ice_monarch"] = {
                    "user": ice_counts.idxmax(),
                    "count": int(ice_counts.max())
                }

    # Combustion Monarch (Most On-Fire days with >= 400 mg caffeine)
    best_fire_user = None
    best_fire_days = 0
    for user in users:
        if not combined.empty:
            u_logs = combined[combined["user_name"] == user].copy()
            if not u_logs.empty:
                if u_logs["created_at"].dt.tz is None:
                    u_logs["created_at"] = u_logs["created_at"].dt.tz_localize("UTC")
                u_logs["created_at"] = u_logs["created_at"].dt.tz_convert("Europe/Madrid")
                u_logs["date_only"] = u_logs["created_at"].dt.date
                def calc_caff_m(r):
                    val = r["value"]
                    did = r["drink_id"]
                    return val * 95 if did in [1, 3] else val * 35
                u_logs["caffeine_mg"] = u_logs.apply(calc_caff_m, axis=1)
                daily_caff = u_logs.groupby("date_only")["caffeine_mg"].sum()
                fire_days = int((daily_caff >= 400).sum())
                if fire_days > best_fire_days:
                    best_fire_days = fire_days
                    best_fire_user = user
                    
    if best_fire_user and best_fire_days > 0:
        trophies["combustion_monarch"] = {
            "user": best_fire_user,
            "count": best_fire_days
        }

    # 3. Streaks (Active consecutive days logging ANY drink)
    longest_streak_user = None
    longest_streak_val = 0
    for user in users:
        trophies["streaks"][user] = 0
        if not combined.empty:
            user_logs = combined[combined["user_name"] == user].copy()
            if not user_logs.empty:
                # Calculate Longest Historical Streak (All-Time)
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
                if dates_desc:
                    today = pd.Timestamp.now(tz=dates_desc[0].tz).normalize()
                    if dates_desc[0] >= today - pd.Timedelta(days=1):
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

    # 4. Most Coffees in a Single Day (All-Time)
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

    # 5. Funny Stats (Timezone Aware: Europe/Madrid)
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
        df_local["date_str"] = df_local["created_at"].dt.normalize().astype(str)
        hourly_counts = df_local.groupby(["user_name", "date_str", "hour"])["value"].sum().reset_index()
        if not hourly_counts.empty:
            max_idx = hourly_counts["value"].idxmax()
            best_hour = hourly_counts.loc[max_idx]
            if best_hour["value"] > 1:
                trophies["funny_stats"]["speedrunner"] = {
                    "user": best_hour['user_name'],
                    "count": int(best_hour['value']),
                    "date": best_hour['date_str'],
                    "hour": int(best_hour['hour'])
                }
                
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
            if not user_logs.empty and len(user_logs) > 4:
                c_count = len(user_logs[user_logs["drink_id"].isin([1, 3])])
                t_count = len(user_logs[user_logs["drink_id"].isin([2, 4])])
                total = c_count + t_count
                if total > 0:
                    diff = abs((c_count / total) - (t_count / total))
                    if diff < best_diff:
                        best_diff = diff
                        balanced_user = user
                        
        if balanced_user:
            trophies["funny_stats"]["balanced"] = balanced_user

        # 5. All-Time Fun Records
        df_local["dayofweek"] = df_local["created_at"].dt.dayofweek
        df_local["year_week"] = df_local["created_at"].dt.strftime("%Y-%W")
        
        mondays = df_local[(df_local["dayofweek"] == 0) & (df_local["drink_id"].isin([1, 3]))]
        if not mondays.empty:
            counts = mondays.groupby("user_name")["value"].sum()
            if not counts.empty:
                trophies["monday_grump"] = {"user": counts.idxmax(), "count": int(counts.max())}
                
        weekends = df_local[df_local["dayofweek"].isin([5, 6])]
        if not weekends.empty:
            weekly_sums = weekends.groupby(["user_name", "year_week"])["value"].sum().reset_index()
            averages = weekly_sums.groupby("user_name")["value"].mean()
            if not averages.empty:
                trophies["weekend_warrior"] = {"user": averages.idxmax(), "count": round(averages.max(), 1)}
                
        weekdays = df_local[df_local["dayofweek"].isin([0, 1, 2, 3, 4])]
        if not weekdays.empty:
            weekly_sums = weekdays.groupby(["user_name", "year_week"])["value"].sum().reset_index()
            averages = weekly_sums.groupby("user_name")["value"].mean()
            if not averages.empty:
                trophies["weekday_warrior"] = {"user": averages.idxmax(), "count": round(averages.max(), 1)}
                
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
            
        late_night = df_local[df_local["hour"].isin([0, 1, 2, 3, 4])].copy()
        if not late_night.empty:
            late_night["minute"] = late_night["created_at"].dt.minute
            latest_drink = late_night.sort_values(by=["hour", "minute"], ascending=[False, False]).iloc[0]
            trophies["midnight_oil"] = {
                "user": latest_drink["user_name"],
                "time": latest_drink["created_at"].strftime("%H:%M")
            }
            
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
                            monogamist_drink = "Coffee" if current_drink in [1, 3] else "Tea"
                    else:
                        current_drink = drinks[i]
                        current_streak = 1
        if monogamist_user and monogamist_streak > 1:
            trophies["monogamist"] = {"user": monogamist_user, "streak": monogamist_streak, "drink": monogamist_drink}

    # 6. Personal Tiered Achievements & Secret Feats (Progression starting from achievements_start_date)
    # Filter logs to achievement release cutoff if start date specified
    if not combined.empty and achievements_start_date is not None:
        if combined["created_at"].dt.tz is None:
            combined_tz = combined["created_at"].dt.tz_localize("UTC")
        else:
            combined_tz = combined["created_at"]
        ach_cutoff_tz = achievements_start_date.tz_convert(combined_tz.dt.tz) if achievements_start_date.tz else achievements_start_date
        ach_active_df = combined[combined_tz >= ach_cutoff_tz].copy()
    else:
        ach_active_df = combined.copy() if not combined.empty else pd.DataFrame()

    for user in users:
        user_logs = ach_active_df[ach_active_df["user_name"] == user].copy() if not ach_active_df.empty else pd.DataFrame()
        
        if not user_logs.empty:
            if user_logs["created_at"].dt.tz is None:
                user_logs["created_at"] = user_logs["created_at"].dt.tz_localize("UTC")
            user_logs["created_at"] = user_logs["created_at"].dt.tz_convert("Europe/Madrid")
            user_logs["date_only"] = user_logs["created_at"].dt.date
            user_logs["hour"] = user_logs["created_at"].dt.hour
            user_logs["dayofweek"] = user_logs["created_at"].dt.dayofweek
            
            u_coffee = int(user_logs[user_logs["drink_id"].isin([1, 3])]["value"].sum())
            u_tea = int(user_logs[user_logs["drink_id"].isin([2, 4])]["value"].sum())
            u_total = u_coffee + u_tea
            u_iced = int(user_logs[user_logs["drink_id"].isin([3, 4])]["value"].sum())
            u_active_days = int(user_logs["date_only"].nunique())
            
            dates_asc = user_logs["created_at"].dt.normalize().drop_duplicates().sort_values().tolist()
            u_max_streak = 0
            if dates_asc:
                cur_s = 1
                u_max_streak = 1
                for i in range(1, len(dates_asc)):
                    if dates_asc[i] - dates_asc[i-1] == pd.Timedelta(days=1):
                        cur_s += 1
                        if cur_s > u_max_streak:
                            u_max_streak = cur_s
                    else:
                        cur_s = 1
                        
            u_early = int(user_logs[user_logs["hour"] < 9]["value"].sum())
            u_night = int(user_logs[user_logs["hour"] >= 19]["value"].sum())
            
            daily_drink_counts = user_logs.groupby("date_only")["value"].sum()
            u_surge_days = int((daily_drink_counts >= 3).sum())
            
            weekend_logs = user_logs[user_logs["dayofweek"].isin([5, 6])]
            u_weekend = int(weekend_logs["value"].sum()) if not weekend_logs.empty else 0
            
            def calc_caff(r):
                val = r["value"]
                did = r["drink_id"]
                return val * 95 if did in [1, 3] else val * 35
            user_logs["caffeine_mg"] = user_logs.apply(calc_caff, axis=1)
            daily_caff = user_logs.groupby("date_only")["caffeine_mg"].sum()
            u_combustion_days = int((daily_caff >= 400).sum())
            
            # Passport stats
            passport = compute_passport_stats(transactions=transactions, user=user, clicks_data=user_logs)
            u_countries = len(passport.get("countries_visited", set()))
            u_cities = len(passport.get("cities_visited", set()))
        else:
            passport = compute_passport_stats(transactions=transactions, user=user, clicks_data=None)
            u_countries = len(passport.get("countries_visited", set()))
            u_cities = len(passport.get("cities_visited", set()))
            u_total = u_coffee = u_tea = u_iced = u_active_days = u_max_streak = 0
            u_early = u_night = u_surge_days = u_weekend = u_combustion_days = 0

        stats_map = {
            "total": u_total,
            "coffee": u_coffee,
            "tea": u_tea,
            "iced": u_iced,
            "streak": u_max_streak,
            "active_days": u_active_days,
            "early": u_early,
            "night": u_night,
            "surge": u_surge_days,
            "weekend": u_weekend,
            "combustion": u_combustion_days,
            "world_explorer": u_countries,
            "metropolis_explorer": u_cities
        }

        user_achievements = {}
        for cat_key, cat_data in ACHIEVEMENT_TIERS.items():
            current_val = stats_map.get(cat_key, 0)
            tier_list = []
            for tier in cat_data["tiers"]:
                target = tier["target"]
                unlocked = bool(current_val >= target)
                progress = min(1.0, current_val / target) if target > 0 else 1.0
                tier_list.append({
                    "level": tier["level"],
                    "name": tier["name"],
                    "target": target,
                    "current": current_val,
                    "unlocked": unlocked,
                    "progress": progress,
                    "progress_pct": progress
                })
            user_achievements[cat_key] = {
                "title": cat_data["title"],
                "icon": cat_data["icon"],
                "desc": cat_data["desc"],
                "current_val": current_val,
                "tiers": tier_list
            }
        trophies["personal_achievements"][user] = user_achievements

        # Secret Feats Evaluation
        user_secrets = {}
        if not user_logs.empty:
            logs_chrono = user_logs.sort_values("created_at").reset_index(drop=True)
            times = logs_chrono["created_at"]
            
            user_secrets["phantom"] = bool((logs_chrono["hour"] == 3).any())
            user_secrets["clockwork"] = bool((times.dt.minute == 0).any())
            
            has_power_nap = False
            has_cursed_fusion = False
            for i in range(len(logs_chrono) - 1):
                delta = (times.iloc[i+1] - times.iloc[i]).total_seconds()
                if 18 * 60 <= delta <= 25 * 60:
                    has_power_nap = True
                if delta <= 90:
                    d1 = logs_chrono.iloc[i]["drink_id"]
                    d2 = logs_chrono.iloc[i+1]["drink_id"]
                    is_c1 = d1 in [1, 3]
                    is_c2 = d2 in [1, 3]
                    if (is_c1 and not is_c2) or (not is_c1 and is_c2):
                        has_cursed_fusion = True
            user_secrets["power_nap"] = has_power_nap
            user_secrets["cursed_fusion"] = has_cursed_fusion
            
            has_overclock = False
            for i in range(len(logs_chrono)):
                window = logs_chrono[(times >= times.iloc[i]) & (times <= times.iloc[i] + pd.Timedelta(hours=2))]
                if len(window) >= 4:
                    has_overclock = True
                    break
            user_secrets["overclock"] = has_overclock
            
            max_mono = 0
            if len(logs_chrono) > 0:
                cur_m = 1
                max_mono = 1
                d_list = logs_chrono["drink_id"].tolist()
                for i in range(1, len(d_list)):
                    if d_list[i] == d_list[i-1]:
                        cur_m += 1
                        if cur_m > max_mono:
                            max_mono = cur_m
                    else:
                        cur_m = 1
            user_secrets["monastic"] = bool(max_mono >= 35)
            
            user_secrets["high_noon"] = bool(((logs_chrono["hour"] == 12) & (times.dt.minute <= 5)).any())
            
            has_all_nighter = False
            user_dates = sorted(list(set(logs_chrono["date_only"])))
            for d in user_dates:
                next_d = d + pd.Timedelta(days=1)
                late = logs_chrono[(logs_chrono["date_only"] == d) & (logs_chrono["hour"] >= 23)]
                early = logs_chrono[(logs_chrono["date_only"] == next_d) & (logs_chrono["hour"] < 6)]
                if not late.empty and not early.empty:
                    has_all_nighter = True
                    break
            user_secrets["all_nighter"] = has_all_nighter
            
            distinct_drinks = set(logs_chrono["drink_id"].unique())
            user_secrets["alchemist"] = bool({1, 2, 3, 4}.issubset(distinct_drinks))
            
            has_thermal = False
            if len(logs_chrono) >= 3:
                d_list = logs_chrono["drink_id"].tolist()
                for i in range(len(d_list) - 2):
                    is_iced1 = d_list[i] in [3, 4]
                    is_hot2 = d_list[i+1] in [1, 2]
                    is_iced3 = d_list[i+2] in [3, 4]
                    if is_iced1 and is_hot2 and is_iced3:
                        has_thermal = True
                        break
            user_secrets["thermal_sandwich"] = has_thermal
        else:
            for s_id in ["phantom", "clockwork", "power_nap", "cursed_fusion", "overclock", "monastic", "high_noon", "all_nighter", "alchemist", "thermal_sandwich"]:
                user_secrets[s_id] = False
                
        # Theme unlocks check from transactions
        from data_processing import get_unlocked_themes, ALL_VALID_THEMES
        unlocked_set = set(get_unlocked_themes(transactions or [], user))
        user_secrets["chromatic_sovereign"] = bool(len(unlocked_set) >= len(ALL_VALID_THEMES))
        
        # Passport Travel Secrets
        user_secrets["continent_hopper"] = len(passport.get("continents_visited", set())) >= 3
        user_secrets["jet_lagged"] = passport.get("jet_lagged", False)
        user_secrets["homebody"] = passport.get("max_home_streak", 0) >= 100
        user_secrets["capital_tour"] = len(passport.get("capital_cities_visited", set())) >= 3
        user_secrets["twin_cities"] = any(len(cities) >= 2 for cities in passport.get("country_cities_map", {}).values())
        
        coffee_caps_count = sum(passport.get("city_counts", {}).get(k, 0) for k in passport.get("city_counts", {}) if is_coffee_capital(k[1]))
        user_secrets["coffee_capital"] = bool(len(passport.get("coffee_capitals_visited", set())) >= 2 or coffee_caps_count >= 3)
        user_secrets["ui_2_0_pioneer"] = bool(not user_logs.empty)

        trophies["secret_feats"][user] = user_secrets

    trophies["monarch_hall_of_fame"] = compute_monarch_hall_of_fame(df_coffee, df_tea, users, transactions=transactions)
    trophies["all_trophies_hof"] = compute_all_trophy_hall_of_fames(df_coffee, df_tea, users, transactions=transactions)

    return trophies

def get_user_titles(user, trophies, return_all=False):
    """Returns list of unlocked titles and badges for a user with standardized emojis."""
    titles = []
    
    # 1. Global Monarch Crowns
    if trophies.get("caffeine_addict") == user: titles.append("👑 ☕ Caffeine Monarch")
    if trophies.get("tea_purist") == user: titles.append("👑 🍵 Tea Monarch")
    if trophies.get("ice_monarch", {}).get("user") == user if isinstance(trophies.get("ice_monarch"), dict) else trophies.get("ice_monarch") == user:
        titles.append("👑 🧊 Sub-Zero Monarch")
    if trophies.get("combustion_monarch", {}).get("user") == user if isinstance(trophies.get("combustion_monarch"), dict) else trophies.get("combustion_monarch") == user:
        titles.append("👑 🔥 Combustion Monarch")

    # 2. Funny / Milestone Records
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
    if ds and isinstance(ds, dict) and ds.get("user") == user: titles.append("🏜️ Desert Survivor")
    
    mo = trophies.get("midnight_oil")
    if mo and isinstance(mo, dict) and mo.get("user") == user: titles.append("🕯️ Midnight Oil")
    
    mono = trophies.get("monogamist")
    if mono and isinstance(mono, dict) and mono.get("user") == user: titles.append("💍 The Monogamist")
    
    asl = trophies.get("afternoon_slump")
    if asl and isinstance(asl, dict) and asl.get("user") == user: titles.append("😴 Afternoon Slump")

    # 3. Unlocked Personal Achievement Badges (Mastery Tracks)
    user_ach = trophies.get("personal_achievements", {}).get(user, {})
    for cat_key, cat_data in user_ach.items():
        cat_icon = cat_data.get("icon", "🎖️")
        for tier in cat_data.get("tiers", []):
            if tier.get("unlocked"):
                tier_name = tier['name']
                if any(ord(c) > 127 for c in tier_name[:2]):
                    t_name = f"{tier_name} ({tier['level']})"
                else:
                    t_name = f"{cat_icon} {tier_name} ({tier['level']})"
                if t_name not in titles:
                    titles.append(t_name)

    # 4. Unlocked Arcane Secret Feats
    user_sec = trophies.get("secret_feats", {}).get(user, {})
    for feat in SECRET_FEATS:
        if user_sec.get(feat["id"]):
            s_name = feat["title"]
            if s_name not in titles:
                titles.append(s_name)

    # 5. Base Starter Badges & Special Unlocks
    base_titles = [
        "☕ Caffeine Fiend",
        "🍵 Tea Connoisseur",
        "🥛 Oat Milk Fanatic",
        "⚡ Velocity Pilot",
        "🌱 Eco Brewer"
    ]
    for bt in base_titles:
        if bt not in titles:
            titles.append(bt)
    
    if return_all:
        return titles
        
    if not titles:
        return "☕ Caffeine Fiend"
        
    return random.choice(titles)

def resolve_user_title(user, prefs, trophies):
    """Resolves the active displayed profile title, dynamically rolling a random unlocked title if 'Random' is selected."""
    user_pref = prefs.get(user, {}) if prefs else {}
    raw_title = user_pref.get("title")
    if not raw_title or "Random" in raw_title or "🎲" in raw_title:
        return get_user_titles(user, trophies, return_all=False)
    return raw_title

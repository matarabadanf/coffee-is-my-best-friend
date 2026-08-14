import pandas as pd
from world_data import (
    TRAVEL_COUNTRIES, 
    DEFAULT_COUNTRY, 
    get_user_default_country, 
    get_user_default_city,
    compute_passport_stats,
    is_coffee_capital
)

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

    # Extract location (country & city) from JSON or dedicated columns if present
    if not df.empty:
        if "location" in df.columns:
            def _extract_loc(loc):
                if isinstance(loc, dict):
                    return loc.get("country"), loc.get("city")
                return None, None
            loc_tuples = df["location"].apply(_extract_loc)
            if "country" not in df.columns or df["country"].isna().all():
                df["country"] = [t[0] for t in loc_tuples]
            else:
                df["country"] = df["country"].fillna(pd.Series([t[0] for t in loc_tuples], index=df.index))
                
            if "city" not in df.columns or df["city"].isna().all():
                df["city"] = [t[1] for t in loc_tuples]
            else:
                df["city"] = df["city"].fillna(pd.Series([t[1] for t in loc_tuples], index=df.index))
    
    # Separate Dataframes (1: Hot Coffee, 3: Iced Coffee, 2: Hot Tea, 4: Iced Tea)
    df_coffee = df[df["drink_id"].isin([1, 3])]
    df_tea = df[df["drink_id"].isin([2, 4])]
    
    # Calculate Scores
    coffee_scores = df_coffee.groupby("user_name")["value"].sum().to_dict()
    tea_scores = df_tea.groupby("user_name")["value"].sum().to_dict()

    return df, df_coffee, df_tea, coffee_scores, tea_scores

def get_cumulative_data(data, start_date, end_date, users, freq="D"):
    # 1. Normalize dates to clean midnight intervals so reindex matches resampled timestamps
    start_date = pd.to_datetime(start_date).normalize()
    end_date = pd.to_datetime(end_date).normalize()
    full_index = pd.date_range(start=start_date, end=end_date, freq=freq)
    
    # 2. Filter data within normalized boundaries
    mask = (data["created_at"] >= start_date) & (data["created_at"] <= (end_date + pd.Timedelta(days=1)))
    filtered_df = data.loc[mask].copy()
    
    if filtered_df.empty:
        empty_df = pd.DataFrame(0, index=full_index, columns=users)
        return empty_df.cumsum()

    # Pivot to [Time, User] = Count
    pivot = filtered_df.pivot_table(index="created_at", columns="user_name", values="value", aggfunc="sum", fill_value=0)
    
    # 3. Ensure all users exist
    for u in users:
        if u not in pivot.columns:
            pivot[u] = 0
            
    # 4. Resample & Reindex
    resampled = pivot.resample(freq).sum()
    resampled = resampled.reindex(full_index, fill_value=0)
    
    # 5. Cumulative Sum
    cumulative = resampled.cumsum()
    cumulative = cumulative.astype(float)
    
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

# Achievement Configuration Tiers (Calibrated for balanced prestige and long-term milestones)
ACHIEVEMENT_TIERS = {
    "total": {
        "title": "🏆 Universal Dedication",
        "icon": "🏆",
        "desc": "Overall drinks logged (Coffee + Tea, Hot + Iced).",
        "tiers": [
            {"level": "Bronze", "name": "🥤 Daily Sipper", "target": 100},
            {"level": "Silver", "name": "☕ Café Regular", "target": 350},
            {"level": "Gold", "name": "🎖️ Beverage Devotee", "target": 750},
            {"level": "Diamond", "name": "🏆 Beverage Titan", "target": 1500},
        ]
    },
    "coffee": {
        "title": "☕ Espresso Mastery",
        "icon": "☕",
        "desc": "Total coffee cups consumed.",
        "tiers": [
            {"level": "Bronze", "name": "☕ Bean Novice", "target": 150},
            {"level": "Silver", "name": "☕ Barista Artisan", "target": 400},
            {"level": "Gold", "name": "☕ Espresso Virtuoso", "target": 750},
            {"level": "Diamond", "name": "👑 Coffee Monarch", "target": 1500},
        ]
    },
    "tea": {
        "title": "🍵 Zen Tea Garden",
        "icon": "🍵",
        "desc": "Total tea brews consumed.",
        "tiers": [
            {"level": "Bronze", "name": "🍃 Leaf Initiate", "target": 50},
            {"level": "Silver", "name": "🌿 Herbal Sage", "target": 125},
            {"level": "Gold", "name": "🍵 Matcha Alchemist", "target": 250},
            {"level": "Diamond", "name": "👑 Zen Monarch", "target": 500},
        ]
    },
    "iced": {
        "title": "🧊 Sub-Zero Frost Realm",
        "icon": "🧊",
        "desc": "Total iced beverages consumed.",
        "tiers": [
            {"level": "Bronze", "name": "🧊 Chilled Sipper", "target": 15},
            {"level": "Silver", "name": "❄️ Ice Sculptor", "target": 50},
            {"level": "Gold", "name": "🧊 Frost Titan", "target": 120},
            {"level": "Diamond", "name": "👑 Sub-Zero Monarch", "target": 250},
        ]
    },
    "streak": {
        "title": "🔥 Streak Sovereign",
        "icon": "🔥",
        "desc": "Unbroken consecutive daily logging streak.",
        "tiers": [
            {"level": "Bronze", "name": "✨ Spark", "target": 7},
            {"level": "Silver", "name": "🔥 Iron Flame", "target": 21},
            {"level": "Gold", "name": "⚡ Unstoppable Blaze", "target": 45},
            {"level": "Diamond", "name": "👑 Eternal Inferno", "target": 90},
        ]
    },
    "active_days": {
        "title": "🗓️ Calendar Dedication",
        "icon": "🗓️",
        "desc": "Total unique days with at least one logged drink.",
        "tiers": [
            {"level": "Bronze", "name": "🗓️ Habit Initiate", "target": 75},
            {"level": "Silver", "name": "📅 Steadfast Brewer", "target": 220},
            {"level": "Gold", "name": "💯 Centurion", "target": 350},
            {"level": "Diamond", "name": "👑 Bicentennial Legend", "target": 500},
        ]
    },
    "early": {
        "title": "🌅 Dawn Patrol",
        "icon": "🌅",
        "desc": "Early morning drinks logged before 09:00 AM.",
        "tiers": [
            {"level": "Bronze", "name": "🌅 Sunrise Sipper", "target": 25},
            {"level": "Silver", "name": "🐓 Early Rooster", "target": 60},
            {"level": "Gold", "name": "🌄 Dawn Monarch", "target": 125},
            {"level": "Diamond", "name": "👑 Master of the Dawn", "target": 250},
        ]
    },
    "night": {
        "title": "🦉 Midnight Society",
        "icon": "🦉",
        "desc": "Evening & late-night drinks logged after 19:00 PM.",
        "tiers": [
            {"level": "Bronze", "name": "🌆 Dusk Drinker", "target": 30},
            {"level": "Silver", "name": "🌌 Twilight Scholar", "target": 75},
            {"level": "Gold", "name": "🦉 Midnight Monarch", "target": 150},
            {"level": "Diamond", "name": "👑 Creature of the Night", "target": 300},
        ]
    },
    "surge": {
        "title": "⚡ Velocity Overdrive",
        "icon": "⚡",
        "desc": "Days where 3 or more drinks were logged in 24 hours.",
        "tiers": [
            {"level": "Bronze", "name": "🏎️ Turbo Day", "target": 35},
            {"level": "Silver", "name": "⚡ Overdrive", "target": 90},
            {"level": "Gold", "name": "🚀 Hyper-Drive", "target": 175},
            {"level": "Diamond", "name": "👑 Supersonic Monarch", "target": 300},
        ]
    },
    "weekend": {
        "title": "🏖️ Weekend Wanderer",
        "icon": "🏖️",
        "desc": "Total drinks logged on Saturdays and Sundays.",
        "tiers": [
            {"level": "Bronze", "name": "🏖️ Saturday Starter", "target": 50},
            {"level": "Silver", "name": "⛵ Sunday Brewer", "target": 110},
            {"level": "Gold", "name": "⚔️ Weekend Warrior", "target": 200},
            {"level": "Diamond", "name": "👑 Weekend Monarch", "target": 350},
        ]
    },
    "combustion": {
        "title": "🔥 Combustion Overclock",
        "icon": "🔥",
        "desc": "Days where daily caffeine velocity reached >= 400 mg (On-Fire state).",
        "tiers": [
            {"level": "Bronze", "name": "💥 Ignition Spark", "target": 1},
            {"level": "Silver", "name": "🔥 Flamethrower", "target": 5},
            {"level": "Gold", "name": "🌋 Inferno Beast", "target": 15},
            {"level": "Diamond", "name": "👑 Combustion Monarch", "target": 35},
        ]
    },
    "world_explorer": {
        "title": "🌍 World Explorer",
        "icon": "🌍",
        "desc": "Visit different countries and expand your passport.",
        "tiers": [
            {"level": "Bronze",  "name": "🗺️ First Stamp",       "target": 1},
            {"level": "Silver",  "name": "✈️ Frequent Flyer",     "target": 3},
            {"level": "Gold",    "name": "🌎 Globe Trotter",      "target": 8},
            {"level": "Diamond", "name": "🌐 World Traveler",     "target": 15},
            {"level": "Master",  "name": "👑 Nomad Supreme",      "target": 25},
        ]
    },
    "metropolis_explorer": {
        "title": "🏙️ Metropolis Explorer",
        "icon": "🏙️",
        "desc": "Visit different cities across your coffee journeys.",
        "tiers": [
            {"level": "Bronze",  "name": "🚶 Urban Roamer",       "target": 3},
            {"level": "Silver",  "name": "🚲 City Hopper",        "target": 8},
            {"level": "Gold",    "name": "🚇 Metropolitan",       "target": 18},
            {"level": "Diamond", "name": "✈️ Cosmopolitan",       "target": 35},
            {"level": "Master",  "name": "👑 Global Citizen",      "target": 60},
        ]
    }
}

SECRET_FEATS = [
    {
        "id": "phantom",
        "title": "🌒 The Phantom of 03:00",
        "desc": "Distilled the sacred brew between 03:00 AM and 03:59 AM in the dead of night.",
        "hint": "When the third hour tolls and the world surrenders to shadows, only the sleepless ghost distills the elixir..."
    },
    {
        "id": "clockwork",
        "title": "🕰️ The Atomic Precisionist",
        "desc": "Logged a beverage at the exact zero-minute mark (:00) of the hour with chronometer precision.",
        "hint": "When the gear strikes true north on the zero tick, drink without a microsecond of hesitation..."
    },
    {
        "id": "power_nap",
        "title": "💤 Power Nap Protocol",
        "desc": "Logged consecutive drinks separated by an exact 18-to-25 minute power nap window.",
        "hint": "Rest for the duration of a sparrow's slumber. Awaken and drink before the half-hour expires..."
    },
    {
        "id": "cursed_fusion",
        "title": "🧙‍♂️ The Cursed Fusion",
        "desc": "Committed barista heresy by logging a Coffee and a Tea within 90 seconds of each other.",
        "hint": "Pour the essence of the roasted bean and the spirit of the leaf into the same cauldron before the steam subsides..."
    },
    {
        "id": "overclock",
        "title": "⚡ Overclock Protocol",
        "desc": "Pushed vascular limits with 4 or more drinks consumed within a 2-hour window.",
        "hint": "A tempest within a heartbeat. Four strikes before the hourglass turns twice..."
    },
    {
        "id": "monastic",
        "title": "📜 The Monastic Vow",
        "desc": "Maintained an unbroken vow of singular devotion with 35+ consecutive identical beverage logs.",
        "hint": "True conviction is not variety, but relentless focus. Thirty-five steps along a single path without turning your gaze..."
    },
    {
        "id": "high_noon",
        "title": "☀️ High Noon Apex",
        "desc": "Brewed precisely during the solar zenith between 12:00 PM and 12:05 PM.",
        "hint": "Strike when the sun reaches the true apex, and the shadow vanishes directly beneath the pedestal..."
    },
    {
        "id": "all_nighter",
        "title": "🦉 The All-Nighter",
        "desc": "Conquered the midnight abyss by logging a late-night drink after 23:00 PM and greeting the dawn before 06:00 AM.",
        "hint": "Bridge the abyss of midnight. Drink as the stars reign, and greet the dawn without closing your eyes..."
    },
    {
        "id": "alchemist",
        "title": "🔮 The Grand Alchemist",
        "desc": "Mastered all 4 elemental chalices: Hot Coffee, Iced Coffee, Hot Tea, and Iced Tea.",
        "hint": "Four elemental chalices exist in the realm: Ember, Steam, Ice, and Mist. Collect all four to close the circle..."
    },
    {
        "id": "thermal_sandwich",
        "title": "🥪 The Thermal Sandwich",
        "desc": "Encased a Hot drink between two consecutive Iced drinks (Iced ➔ Hot ➔ Iced).",
        "hint": "Encase the burning ember between two slabs of frozen crystal..."
    },
    {
        "id": "chromatic_sovereign",
        "title": "🌈 The Chromatic Sovereign",
        "desc": "Unlocked all 8 handcrafted aesthetic palettes in the Theme Boutique to attain complete stylistic supremacy.",
        "hint": "Don every cloak, gown, and armor tailored by the masters of bean and leaf..."
    },
    {
        "id": "continent_hopper",
        "title": "🌏 Continent Hopper",
        "desc": "Log drinks in 3+ different continents.",
        "hint": "One cup per landmass. The equator is just a suggestion."
    },
    {
        "id": "jet_lagged",
        "title": "✈️ Jet Lagged",
        "desc": "Log drinks in 2 different countries within 24 hours.",
        "hint": "Two flags in 24 hours. Where did you wake up?"
    },
    {
        "id": "homebody",
        "title": "🏠 The Homebody",
        "desc": "Log 100 consecutive drinks in your default country.",
        "hint": "100 cups and never left the zip code."
    },
    {
        "id": "capital_tour",
        "title": "🏛️ Capital Tour",
        "desc": "Log drinks in 3+ different national capital cities.",
        "hint": "Three seats of sovereign power. Three sacred brews."
    },
    {
        "id": "twin_cities",
        "title": "🌉 Twin Cities",
        "desc": "Log drinks in 2+ different cities within the same country.",
        "hint": "Two metropolises under one flag."
    },
    {
        "id": "ui_2_0_pioneer",
        "title": "🌟 UI 2.0 Pioneer",
        "desc": "Stepped into the next generation of Coffee is my best friend with morphism themes, passport exploration, and live unlock celebrations.",
        "hint": "Explore the newly unlocked realm of UI 2.0 and forge the frontier..."
    },
    {
        "id": "coffee_capital",
        "title": "☕ Coffee Capital Pilgrim",
        "desc": "Log 3+ drinks across world-renowned coffee metropolises.",
        "hint": "Drink where espresso legends were forged: Vienna, Rome, Seattle, Kyoto, Istanbul..."
    }
]

def get_gamification_metrics(df_coffee, df_tea, users, transactions=None):
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

    # Historical Monthly Records with gender-neutral Monarch titles
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

    # --- New All-Time Records ---
    if not combined.empty:
        df_local["dayofweek"] = df_local["created_at"].dt.dayofweek
        
        df_local["year_week"] = df_local["created_at"].dt.strftime("%Y-%W")
        
        # 1. Monday Grump
        mondays = df_local[(df_local["dayofweek"] == 0) & (df_local["drink_id"].isin([1, 3]))]
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
                            monogamist_drink = "Coffee" if current_drink in [1, 3] else "Tea"
                    else:
                        current_drink = drinks[i]
                        current_streak = 1
        if monogamist_user and monogamist_streak > 1:
            trophies["monogamist"] = {"user": monogamist_user, "streak": monogamist_streak, "drink": monogamist_drink}

    # --- Personal Tiered Achievements & Secret Feats per User ---
    for user in users:
        user_logs = combined[combined["user_name"] == user].copy() if not combined.empty else pd.DataFrame()
        
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
            u_early = int(user_logs[user_logs["hour"] < 9]["value"].sum())
            u_night = int(user_logs[user_logs["hour"] >= 19]["value"].sum())
            u_weekend = int(user_logs[user_logs["dayofweek"].isin([5, 6])]["value"].sum())
            u_surge = int((user_logs.groupby("date_only")["value"].sum() >= 3).sum())
            u_mondays = int(user_logs[user_logs["dayofweek"] == 0]["value"].sum())
            
            def calc_row_caff(r):
                val = r["value"]
                did = r["drink_id"]
                return val * 95 if did in [1, 3] else val * 35
            user_logs["caffeine_mg"] = user_logs.apply(calc_row_caff, axis=1)
            u_daily_caff = user_logs.groupby("date_only")["caffeine_mg"].sum()
            u_on_fire_days = int((u_daily_caff >= 400).sum())
        else:
            u_coffee = 0
            u_tea = 0
            u_total = 0
            u_iced = 0
            u_active_days = 0
            u_early = 0
            u_night = 0
            u_weekend = 0
            u_surge = 0
            u_mondays = 0
            u_on_fire_days = 0
            
        u_streak = trophies["streaks"].get(user, 0)

        # Drop 1 Travel Stats & Passport
        prefs_for_user = get_user_preferences(transactions, [user]).get(user, {})
        u_def_country = prefs_for_user.get("default_country", get_user_default_country(user))
        u_def_city = prefs_for_user.get("default_city", get_user_default_city(user))
        clicks_for_u = user_logs.to_dict("records") if not user_logs.empty else None
        passport = compute_passport_stats(transactions or [], user, u_def_country, u_def_city, clicks_data=clicks_for_u)
        u_unique_foreign_countries = len([c for c in passport["countries_visited"] if c != u_def_country])
        u_unique_cities = len(passport["cities_visited"])

        user_counts = {
            "total": u_total,
            "coffee": u_coffee,
            "tea": u_tea,
            "iced": u_iced,
            "streak": u_streak,
            "active_days": u_active_days,
            "early": u_early,
            "night": u_night,
            "surge": u_surge,
            "weekend": u_weekend,
            "combustion": u_on_fire_days,
            "world_explorer": u_unique_foreign_countries,
            "metropolis_explorer": u_unique_cities
        }

        # Build Tier Progression
        user_achievements = {}
        for cat_key, cat_meta in ACHIEVEMENT_TIERS.items():
            current_val = user_counts.get(cat_key, 0)
            tiers_progress = []
            for t in cat_meta["tiers"]:
                target = t["target"]
                is_unlocked = current_val >= target
                pct = min(1.0, current_val / max(1, target))
                tiers_progress.append({
                    "level": t["level"],
                    "name": t["name"],
                    "target": target,
                    "current": current_val,
                    "unlocked": is_unlocked,
                    "progress_pct": pct
                })
            user_achievements[cat_key] = {
                "title": cat_meta["title"],
                "icon": cat_meta["icon"],
                "desc": cat_meta.get("desc", ""),
                "tiers": tiers_progress
            }
        trophies["personal_achievements"][user] = user_achievements

        # Check Mysterious Secret Feats
        user_secrets = {}
        if not user_logs.empty:
            sorted_logs = user_logs.sort_values("created_at")
            drinks = sorted_logs["drink_id"].tolist()
            
            # 1. The Phantom of 03:00 (03:00 to 03:59 AM)
            phantom_unlocked = not sorted_logs[sorted_logs["hour"] == 3].empty
            
            # 2. The Atomic Precisionist (:00 on the dot)
            clockwork_unlocked = not sorted_logs[sorted_logs["created_at"].dt.minute == 0].empty
            
            # 3. Power Nap Protocol (18 to 25 min gap)
            power_nap_unlocked = False
            if len(sorted_logs) > 1:
                gaps = sorted_logs["created_at"].diff().dropna()
                power_nap_unlocked = bool(((gaps >= pd.Timedelta(minutes=18)) & (gaps <= pd.Timedelta(minutes=25))).any())
                
            # 4. The Cursed Fusion (Coffee + Tea within 90s)
            fusion_unlocked = False
            if len(sorted_logs) > 1:
                for i in range(len(sorted_logs) - 1):
                    d1 = sorted_logs.iloc[i]
                    d2 = sorted_logs.iloc[i+1]
                    if (d1["drink_id"] in [1, 3]) != (d2["drink_id"] in [1, 3]):
                        if (d2["created_at"] - d1["created_at"]).total_seconds() <= 90:
                            fusion_unlocked = True
                            break
                            
            # 5. Overclock Protocol (4+ drinks within 120 minutes)
            overclock_unlocked = False
            if len(sorted_logs) >= 4:
                for i in range(len(sorted_logs) - 3):
                    t_start = sorted_logs.iloc[i]["created_at"]
                    t_end = sorted_logs.iloc[i+3]["created_at"]
                    if (t_end - t_start) <= pd.Timedelta(hours=2):
                        overclock_unlocked = True
                        break
                        
            # 6. The Monastic Vow (35+ consecutive same drink logs)
            monastic_unlocked = False
            cur_streak = 1
            for i in range(1, len(drinks)):
                if drinks[i] == drinks[i-1]:
                    cur_streak += 1
                    if cur_streak >= 35:
                        monastic_unlocked = True
                        break
                else:
                    cur_streak = 1
                    
            # 7. High Noon Apex (12:00 to 12:05 PM)
            high_noon_unlocked = not sorted_logs[(sorted_logs["hour"] == 12) & (sorted_logs["created_at"].dt.minute <= 5)].empty
            
            # 8. The All-Nighter (log >= 23h and next <= 06h within 7h)
            all_nighter_unlocked = False
            if len(sorted_logs) > 1:
                for i in range(len(sorted_logs) - 1):
                    t1 = sorted_logs.iloc[i]["created_at"]
                    t2 = sorted_logs.iloc[i+1]["created_at"]
                    if t1.hour >= 23 and t2.hour < 6 and (t2 - t1) <= pd.Timedelta(hours=7):
                        all_nighter_unlocked = True
                        break
                        
            # 9. The Grand Alchemist (Logged all 4 distinct drink variations)
            alchemist_unlocked = bool(set(sorted_logs["drink_id"].unique()) == {1, 2, 3, 4})
            
            # 10. The Thermal Sandwich (Iced -> Hot -> Iced)
            sandwich_unlocked = False
            if len(drinks) >= 3:
                for i in range(len(drinks) - 2):
                    if drinks[i] in [3, 4] and drinks[i+1] in [1, 2] and drinks[i+2] in [3, 4]:
                        sandwich_unlocked = True
                        break
        else:
            phantom_unlocked = False
            clockwork_unlocked = False
            power_nap_unlocked = False
            fusion_unlocked = False
            overclock_unlocked = False
            monastic_unlocked = False
            high_noon_unlocked = False
            all_nighter_unlocked = False
            alchemist_unlocked = False
            sandwich_unlocked = False

        # 11. The Chromatic Sovereign (Unlocked all 8 themes in Theme Shop)
        unlocked_set = set(get_unlocked_themes(transactions, user)) if transactions else set(BASE_THEMES)
        chromatic_unlocked = bool(len(unlocked_set) >= len(ALL_VALID_THEMES))

        # Drop 1 Secret Feats
        continent_hopper_unlocked = len(passport["continents_reached"]) >= 3
        
        jet_lagged_unlocked = False
        homebody_unlocked = False
        max_consecutive_default_country = 0
        current_consecutive_default = 0
        
        if transactions:
            user_txs = [tx for tx in transactions if tx.get("user_name") == user and tx.get("transaction_type") == "drink_log"]
            user_txs.sort(key=lambda x: pd.to_datetime(x.get("created_at", "1970-01-01")))
            
            for i in range(len(user_txs)):
                tx = user_txs[i]
                c_code = tx.get("metadata", {}).get("country", u_def_country) if isinstance(tx.get("metadata"), dict) else u_def_country
                if c_code == u_def_country:
                    current_consecutive_default += 1
                    max_consecutive_default_country = max(max_consecutive_default_country, current_consecutive_default)
                else:
                    current_consecutive_default = 0
                    
                if i > 0:
                    prev_tx = user_txs[i-1]
                    prev_code = prev_tx.get("metadata", {}).get("country", u_def_country) if isinstance(prev_tx.get("metadata"), dict) else u_def_country
                    if c_code != prev_code:
                        time_diff = pd.to_datetime(tx.get("created_at")) - pd.to_datetime(prev_tx.get("created_at"))
                        if time_diff.total_seconds() <= 86400:
                            jet_lagged_unlocked = True
                            
            homebody_unlocked = max_consecutive_default_country >= 100

        user_secrets["phantom"] = phantom_unlocked
        user_secrets["clockwork"] = clockwork_unlocked
        user_secrets["power_nap"] = power_nap_unlocked
        user_secrets["cursed_fusion"] = fusion_unlocked
        user_secrets["overclock"] = overclock_unlocked
        user_secrets["monastic"] = monastic_unlocked
        user_secrets["high_noon"] = high_noon_unlocked
        user_secrets["all_nighter"] = all_nighter_unlocked
        user_secrets["alchemist"] = alchemist_unlocked
        user_secrets["thermal_sandwich"] = sandwich_unlocked
        user_secrets["chromatic_sovereign"] = chromatic_unlocked
        user_secrets["continent_hopper"] = continent_hopper_unlocked
        user_secrets["jet_lagged"] = jet_lagged_unlocked
        user_secrets["homebody"] = homebody_unlocked
        
        # New City Secret Feats
        user_secrets["capital_tour"] = len(passport.get("capital_cities_visited", set())) >= 3
        user_secrets["twin_cities"] = any(len(cities) >= 2 for cities in passport.get("country_cities_map", {}).values())
        
        coffee_caps_count = sum(passport.get("city_counts", {}).get(k, 0) for k in passport.get("city_counts", {}) if is_coffee_capital(k[1]))
        user_secrets["coffee_capital"] = bool(len(passport.get("coffee_capitals_visited", set())) >= 2 or coffee_caps_count >= 3)
        user_secrets["ui_2_0_pioneer"] = bool(not user_logs.empty or len(unlocked_set) > 1 or passport.get("countries_count", 0) > 0)

        trophies["secret_feats"][user] = user_secrets

    return trophies

import random

def get_user_titles(user, trophies, return_all=False):
    titles = []
    
    # 1. Global Monarch Crowns
    if trophies.get("caffeine_addict") == user: titles.append("👑 ☕ Caffeine Monarch")
    if trophies.get("tea_purist") == user: titles.append("👑 🍵 Tea Monarch")
    if trophies.get("ice_monarch") == user: titles.append("👑 🧊 Sub-Zero Monarch")
    if trophies.get("combustion_monarch") == user: titles.append("👑 🔥 Combustion Monarch")
    
    # 2. Historical & Record Badges
    lhs = trophies.get("longest_historical_streak")
    if lhs and isinstance(lhs, dict) and lhs.get("user") == user:
        titles.append(f"🔥 Longest Streak ({lhs.get('days')}d)")
        
    mcid = trophies.get("most_coffees_in_a_day")
    if mcid and isinstance(mcid, dict) and mcid.get("user") == user:
        titles.append(f"🚀 Most in a Day ({mcid.get('count')} drinks)")
        
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
        "🌱 Eco Brewer",
        "🌟 UI 2.0 Pioneer"
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

def get_coin_balances(df, transactions, users):
    balances = {u: 0 for u in users}
    
    if not df.empty:
        counts = df.groupby("user_name").size()
        for u, count in counts.items():
            if u in balances:
                balances[u] += count * 10
                
    if transactions:
        tx_df = pd.DataFrame(transactions)
        if not tx_df.empty and "amount" in tx_df.columns:
            tx_sums = tx_df.groupby("user_name")["amount"].sum()
            for u, amt in tx_sums.items():
                if u in balances:
                    balances[u] += amt
                    
    return balances

def get_active_perks(transactions, users):
    perks = {u: [] for u in users}
    if not transactions:
        return perks
        
    tx_df = pd.DataFrame(transactions)
    if tx_df.empty or "transaction_type" not in tx_df.columns:
        return perks
        
    shop_txs = tx_df[tx_df["transaction_type"] == "shop"]
    if shop_txs.empty:
        return perks
        
    for _, row in shop_txs.iterrows():
        meta = row.get("metadata", {})
        if isinstance(meta, dict) and "perk" in meta:
            expires_at = meta.get("expires_at")
            if expires_at:
                try:
                    expires_dt = pd.to_datetime(expires_at)
                    if pd.Timestamp.now(tz="UTC") > expires_dt:
                        continue 
                except:
                    pass
            
            u = row.get("user_name")
            if u in perks:
                perks[u].append(meta["perk"])
                
    return perks

BASE_THEMES = ["Latte (Light)"]
ALL_VALID_THEMES = [
    "Latte (Light)",
    "Espresso (Dark)",
    "Matcha (Green)",
    "Caramel Macchiato (Amber)",
    "Strawberry Frappé (Pink)",
    "Taro Boba (Purple)",
    "Midnight Cyber Brew (Dark Neon)",
    "Velvet Mocha (Cocoa)"
]

def get_unlocked_themes(transactions, user):
    """Returns list of themes unlocked by a specific user (always includes base themes)."""
    unlocked = set(BASE_THEMES)
    if not transactions:
        return [t for t in ALL_VALID_THEMES if t in unlocked]
        
    tx_df = pd.DataFrame(transactions)
    if tx_df.empty or "transaction_type" not in tx_df.columns:
        return [t for t in ALL_VALID_THEMES if t in unlocked]
        
    user_shop_txs = tx_df[(tx_df["transaction_type"] == "shop") & (tx_df["user_name"] == user)]
    if not user_shop_txs.empty:
        for _, row in user_shop_txs.iterrows():
            meta = row.get("metadata", {})
            if isinstance(meta, dict):
                theme_unlocked = meta.get("theme_unlock") or meta.get("unlocked_theme")
                if theme_unlocked and theme_unlocked in ALL_VALID_THEMES:
                    unlocked.add(theme_unlocked)
                    
    # Return in standardized order
    return [t for t in ALL_VALID_THEMES if t in unlocked]

def get_user_preferences(transactions=None, users=None, db_preferences=None):
    if users is None:
        users = ["Cris", "Bea", "Fer"]
        
    prefs = {
        u: {
            "theme": "Latte (Light)", 
            "emoji": "☕", 
            "title": None, 
            "ui_style": "Modern Flat", 
            "default_country": get_user_default_country(u),
            "default_city": get_user_default_city(u),
            "share_live_location": True
        } for u in users
    }
    
    # 1. Apply preferences from coin_transactions (legacy fallback)
    if transactions:
        tx_df = pd.DataFrame(transactions)
        if not tx_df.empty and "transaction_type" in tx_df.columns:
            pref_txs = tx_df[tx_df["transaction_type"] == "preference"]
            for _, row in pref_txs.iterrows():
                u = row.get("user_name")
                meta = row.get("metadata", {})
                if u in prefs and isinstance(meta, dict):
                    if "theme" in meta:
                        theme_val = meta["theme"]
                        unlocked_for_u = get_unlocked_themes(transactions, u)
                        if theme_val not in unlocked_for_u:
                            theme_val = "Latte (Light)"
                        prefs[u]["theme"] = theme_val
                    if "emoji" in meta:
                        prefs[u]["emoji"] = meta["emoji"]
                    if "title" in meta:
                        prefs[u]["title"] = meta["title"]
                    if "ui_style" in meta:
                        style_val = meta["ui_style"]
                        if style_val not in ["Modern Flat", "Glassmorphism", "Neumorphism"]:
                            style_val = "Modern Flat"
                        prefs[u]["ui_style"] = style_val
                    if "default_country" in meta:
                        prefs[u]["default_country"] = meta["default_country"]
                    if "default_city" in meta:
                        prefs[u]["default_city"] = meta["default_city"]
                    if "share_live_location" in meta:
                        prefs[u]["share_live_location"] = bool(meta["share_live_location"])

    # 2. Apply from dedicated user_preferences table (takes primary precedence)
    if db_preferences:
        for row in db_preferences:
            u = row.get("user_name")
            if u in prefs:
                if row.get("theme"):
                    theme_val = row["theme"]
                    unlocked_for_u = get_unlocked_themes(transactions or [], u)
                    if theme_val not in unlocked_for_u:
                        theme_val = "Latte (Light)"
                    prefs[u]["theme"] = theme_val
                if row.get("emoji"):
                    prefs[u]["emoji"] = row["emoji"]
                if "title" in row and row["title"] is not None:
                    prefs[u]["title"] = row["title"]
                if row.get("ui_style"):
                    style_val = row["ui_style"]
                    if style_val in ["Modern Flat", "Glassmorphism", "Neumorphism"]:
                        prefs[u]["ui_style"] = style_val
                if row.get("default_country"):
                    prefs[u]["default_country"] = row["default_country"]
                if row.get("default_city"):
                    prefs[u]["default_city"] = row["default_city"]
                if "share_live_location" in row and row["share_live_location"] is not None:
                    prefs[u]["share_live_location"] = bool(row["share_live_location"])
                if isinstance(row.get("metadata"), dict):
                    meta = row["metadata"]
                    for k in ["theme", "emoji", "title", "ui_style", "default_country", "default_city", "share_live_location"]:
                        if k in meta:
                            prefs[u][k] = meta[k]

    return prefs
    return prefs

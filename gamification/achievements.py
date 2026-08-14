import pandas as pd

# UI 2.0 Release Date Cutoff: Progression for personal milestone tracks, secret feats, and active thrones starts here!
ACHIEVEMENTS_START_DATE = pd.Timestamp("2026-08-15 00:00:00", tz="Europe/Madrid")

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

# ☕ Coffee is my best friend

> *"Dios no creo que oiga una frikada mayor de lo que acabo de oir."* — A wise woman.

Welcome to the digital caffeine sanctuary. This app tracks the life-sustaining elixir consumption of **Cris, Bea, and Fer**. It's not just a tracker; it's a lifestyle.

Disclaimer: This project was **partially vibe coded**.

## 🚀 Features
- **Real-time Caffeine Ingestion Tracking**: Powered by Supabase.
- **Anti-Jitter Mechanism**: A built-in 1-minute cooldown to prevent heart palpitations.
- **Analytics that Matter**: Stacked weekly, monthly, and annual charts. See who is winning the race to enlightenment (or insomnia).
- **Philosophical Quotes**: Because coffee is a hug in a mug.

## 🛠️ Stack
- **Frontend**: [Streamlit](https://streamlit.io/) (The GOAT for data apps).
- **Backend**: [Supabase](https://supabase.com/) (Postgres for the modern era).
- **Charts**: [Altair](https://altair-viz.github.io/) (Pretty lines go up).

## 💻 How to Run
1. **Clone the repo**.
2. **Install the goods**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Secrets**:
   Create a `.streamlit/secrets.toml` file with your Supabase credentials:
   ```toml
   [supabase]
   url = "your-supabase-url"
   key = "your-supabase-key"
   ```
4. **Ignition**:
   ```bash
   streamlit run app.py
   ```

---
*Maintained with ❤️ and ☕.*
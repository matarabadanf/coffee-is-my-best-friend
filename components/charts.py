import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# High-contrast, vibrant color mappings tailored for users & drink categories
USER_COLORS = {
    "Cris (coffee)": "#0284C7",   # Sky Blue
    "Cris (tea)": "#38BDF8",      # Light Cyan
    "Cris": "#0284C7",
    "Bea (coffee)": "#F43F5E",    # Rose / Coral Red
    "Bea (tea)": "#FB7185",       # Light Rose
    "Bea": "#F43F5E",
    "Fer (coffee)": "#8B5CF6",    # Purple
    "Fer (tea)": "#A78BFA",       # Light Purple
    "Fer": "#8B5CF6",
    "Hot Coffee": "#D97706",      # Amber Coffee
    "Iced Coffee": "#0284C7",     # Ice Cyan
    "Hot Tea": "#059669",         # Emerald Tea
    "Iced Tea": "#10B981"         # Mint Green
}

def get_color_scale(data_items):
    """Returns domain and range for only the items present in the data."""
    unique_items = list(set(data_items))
    domain = []
    range_ = []
    for item in unique_items:
        domain.append(item)
        range_.append(USER_COLORS.get(item, "#6366F1"))
    return alt.Scale(domain=domain, range=range_)

def render_pie_chart(scores_dict, label_col, val_col, is_coffee=True):
    """Renders a modern Donut Chart with inner radius, percentage callouts, and clean padding."""
    pie_df = pd.DataFrame(list(scores_dict.items()), columns=[label_col, val_col])
    
    if pie_df.empty or pie_df[val_col].sum() == 0:
        st.info("No drink share data available.")
        return

    pie_df['Percentage'] = pie_df[val_col] / pie_df[val_col].sum()

    base = alt.Chart(pie_df).encode(
        theta=alt.Theta(f"{val_col}:Q", stack=True)
    )
    
    # Donut Arc with generous margin
    donut = base.mark_arc(innerRadius=45, outerRadius=75, cornerRadius=4, stroke="rgba(0,0,0,0.15)", strokeWidth=1).encode(
        color=alt.Color(f"{label_col}:N", scale=get_color_scale(pie_df[label_col]), legend=alt.Legend(title="User / Drink", orient="bottom", columns=3)),
        order=alt.Order(f"{val_col}:Q", sort="descending"),
        tooltip=[label_col, val_col, alt.Tooltip("Percentage:Q", format=".1%")]
    )
    
    # Text labels with safe offset
    text = base.mark_text(radius=95, fontSize=11, fontWeight="bold").encode(
        text=alt.Text("Percentage:Q", format=".1%"),
        order=alt.Order(f"{val_col}:Q", sort="descending"),
        color=alt.Color(f"{label_col}:N", scale=get_color_scale(pie_df[label_col]), legend=None)
    )
    
    chart_donut = (donut + text).properties(
        height=320,
        padding={"top": 20, "bottom": 20, "left": 20, "right": 20}
    ).configure(
        background='transparent'
    ).configure_view(
        strokeWidth=0
    ).configure_legend(
        labelFontSize=11,
        titleFontSize=12
    )
    
    st.altair_chart(chart_donut, use_container_width=True)

def plot_metric(data, title="Cumulative Pace"):
    """Plots an unstacked area + line cumulative race chart with timezone-safe timeline."""
    source = data.reset_index().melt('index', var_name='User', value_name='Amount')
    source = source.groupby('User').filter(lambda x: x['Amount'].max() > 0)
    
    if source.empty:
        st.info("No activity recorded for this period.")
        return
        
    # Strip timezone so Vega-Lite parses standard dates across Daylight Savings
    if hasattr(source['index'].dt, 'tz') and source['index'].dt.tz is not None:
        source['index'] = source['index'].dt.tz_localize(None)
        
    y_max = source['Amount'].max()
    y_domain_max = y_max * 1.12 if y_max > 0 else 5
    
    # Area gradient under curve (stack=False to prevent layer scale collision)
    area = alt.Chart(source).mark_area(opacity=0.15).encode(
        x=alt.X('index:T', title='Date', axis=alt.Axis(format='%b %d', gridColor="rgba(128,128,128,0.12)")),
        y=alt.Y('Amount:Q', stack=False, scale=alt.Scale(domain=[0, y_domain_max]), axis=alt.Axis(gridColor="rgba(128,128,128,0.12)")),
        color=alt.Color('User:N', scale=get_color_scale(source['User']), legend=None)
    )
    
    # Bold Line with full opacity legend (stack=False)
    line = alt.Chart(source).mark_line(strokeWidth=3, interpolate='monotone').encode(
        x=alt.X('index:T', title='Date'),
        y=alt.Y('Amount:Q', stack=False),
        color=alt.Color('User:N', scale=get_color_scale(source['User']), legend=alt.Legend(orient="bottom", columns=3, symbolOpacity=1.0)),
        tooltip=[alt.Tooltip('index:T', format='%b %d, %Y', title='Date'), 'User:N', 'Amount:Q']
    )
    
    final_chart = (area + line).properties(
        title=title,
        height=320,
        padding={"top": 15, "bottom": 15, "left": 15, "right": 15}
    ).configure(
        background='transparent'
    ).configure_view(
        strokeWidth=0
    ).configure_title(
        fontSize=15,
        fontWeight="bold"
    )
    
    st.altair_chart(final_chart, use_container_width=True)

def plot_hourly_distribution(df, title="24-Hour Circadian Rhythm (Peak Hours)"):
    """Plots drink volume by hour of day (0-23) with rounded bars."""
    if df.empty:
        st.info("No hourly data available.")
        return
        
    df_copy = df.copy()
    if df_copy["created_at"].dt.tz is None:
        df_copy["created_at"] = df_copy["created_at"].dt.tz_localize("UTC")
    df_copy["created_at"] = df_copy["created_at"].dt.tz_convert("Europe/Madrid")
    
    df_copy["hour"] = df_copy["created_at"].dt.hour
    hourly_counts = df_copy.groupby(["user_name", "hour"])["value"].sum().reset_index()
    
    chart = alt.Chart(hourly_counts).mark_bar(
        cornerRadiusTopLeft=5, 
        cornerRadiusTopRight=5,
        opacity=0.9
    ).encode(
        x=alt.X('hour:O', title='Hour of Day (00:00 - 23:00)', axis=alt.Axis(labelAngle=0, gridColor="rgba(128,128,128,0.12)")),
        y=alt.Y('value:Q', title='Total Drinks', axis=alt.Axis(gridColor="rgba(128,128,128,0.12)")),
        color=alt.Color('user_name:N', scale=get_color_scale(hourly_counts['user_name']), legend=alt.Legend(orient="bottom", columns=3)),
        tooltip=['user_name:N', alt.Tooltip('hour:O', title='Hour'), alt.Tooltip('value:Q', title='Drinks')]
    ).properties(
        title=title,
        height=300
    ).configure(
        background='transparent'
    ).configure_view(
        strokeWidth=0
    ).configure_title(
        fontSize=15,
        fontWeight="bold"
    )
    
    st.altair_chart(chart, use_container_width=True)

def plot_weekday_distribution(df, title="Weekday Volume Breakdown"):
    """Plots volume by day of week with sorted days."""
    if df.empty:
        st.info("No weekday data available.")
        return
        
    df_copy = df.copy()
    if df_copy["created_at"].dt.tz is None:
        df_copy["created_at"] = df_copy["created_at"].dt.tz_localize("UTC")
    df_copy["created_at"] = df_copy["created_at"].dt.tz_convert("Europe/Madrid")
    
    df_copy["weekday_num"] = df_copy["created_at"].dt.dayofweek
    df_copy["weekday_name"] = df_copy["created_at"].dt.day_name()
    
    weekday_counts = df_copy.groupby(["user_name", "weekday_num", "weekday_name"])["value"].sum().reset_index()
    
    chart = alt.Chart(weekday_counts).mark_bar(
        cornerRadiusTopLeft=5,
        cornerRadiusTopRight=5,
        opacity=0.9
    ).encode(
        x=alt.X('weekday_name:O', title='', sort=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], axis=alt.Axis(labelAngle=0)),
        y=alt.Y('value:Q', title='Total Drinks', axis=alt.Axis(gridColor="rgba(128,128,128,0.12)")),
        color=alt.Color('user_name:N', scale=get_color_scale(weekday_counts['user_name']), legend=alt.Legend(orient="bottom", columns=3)),
        tooltip=['user_name:N', 'weekday_name:N', 'value:Q']
    ).properties(
        title=title,
        height=300
    ).configure(
        background='transparent'
    ).configure_view(
        strokeWidth=0
    ).configure_title(
        fontSize=15,
        fontWeight="bold"
    )
    
    st.altair_chart(chart, use_container_width=True)

def plot_average_weekday_distribution(df, title="Average Drinks per Weekday", mode="normalized"):
    """Plots average drinks per day. mode='normalized' divides by total calendar days; mode='raw' divides only by active logged days."""
    if df.empty:
        st.info("No data available for average calculation.")
        return
        
    df_copy = df.copy()
    if df_copy["created_at"].dt.tz is None:
        df_copy["created_at"] = df_copy["created_at"].dt.tz_localize("UTC")
    df_copy["created_at"] = df_copy["created_at"].dt.tz_convert("Europe/Madrid")
    
    df_copy["weekday_num"] = df_copy["created_at"].dt.dayofweek
    df_copy["weekday_name"] = df_copy["created_at"].dt.day_name()
    df_copy["date_only"] = df_copy["created_at"].dt.date
    
    users_in_df = df_copy["user_name"].unique()
    all_days = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), 
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ]
    complete_index = pd.MultiIndex.from_product([users_in_df, [d[0] for d in all_days]], names=["user_name", "weekday_num"])
    complete_df = pd.DataFrame(index=complete_index).reset_index()
    complete_df["weekday_name"] = complete_df["weekday_num"].map({d[0]: d[1] for d in all_days})
    
    if mode == "raw":
        # Raw Average: Total Drinks on that weekday / Distinct active days user logged on that weekday
        user_active_days = df_copy.groupby(["user_name", "weekday_num", "weekday_name"])["date_only"].nunique().reset_index(name="active_days")
        weekday_sums = df_copy.groupby(["user_name", "weekday_num", "weekday_name"])["value"].sum().reset_index()
        merged = pd.merge(complete_df, weekday_sums, on=["user_name", "weekday_num", "weekday_name"], how="left").fillna({"value": 0})
        merged = pd.merge(merged, user_active_days, on=["user_name", "weekday_num", "weekday_name"], how="left").fillna({"active_days": 1})
        merged["average"] = merged.apply(lambda r: r["value"] / r["active_days"] if r["value"] > 0 else 0.0, axis=1)
        weekday_sums = merged
        y_title = "Avg Drinks / Active Day"
    else:
        # Normalized: Total Drinks / Total occurrences of that weekday in the calendar period
        start_date = df_copy["created_at"].min().floor("D")
        end_date = df_copy["created_at"].max().ceil("D")
        if start_date == end_date:
            end_date = end_date + pd.Timedelta(days=1)
            
        date_range = pd.date_range(start_date, end_date, inclusive="left")
        if len(date_range) == 0:
            date_range = pd.date_range(start_date, start_date + pd.Timedelta(days=1), inclusive="left")
            
        total_weekdays = date_range.day_name().value_counts()
        weekday_sums = df_copy.groupby(["user_name", "weekday_num", "weekday_name"])["value"].sum().reset_index()
        weekday_sums = pd.merge(complete_df, weekday_sums, on=["user_name", "weekday_num", "weekday_name"], how="left").fillna({"value": 0})
        weekday_sums['average'] = weekday_sums.apply(lambda r: r['value'] / total_weekdays.get(r['weekday_name'], 1) if total_weekdays.get(r['weekday_name'], 1) > 0 else 0.0, axis=1)
        y_title = "Avg Drinks / Calendar Day"
    
    chart = alt.Chart(weekday_sums).mark_line(point=True, strokeWidth=3, interpolate="monotone").encode(
        x=alt.X('weekday_name:O', title='', 
                sort=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], 
                axis=alt.Axis(labelAngle=0, gridColor="rgba(128,128,128,0.12)")),
        y=alt.Y('average:Q', title=y_title, axis=alt.Axis(gridColor="rgba(128,128,128,0.12)")),
        color=alt.Color('user_name:N', scale=get_color_scale(weekday_sums['user_name']), legend=alt.Legend(orient="bottom", columns=3)),
        tooltip=['user_name:N', 'weekday_name:N', alt.Tooltip('average:Q', format='.2f', title='Average')]
    ).properties(
        title=title,
        height=320,
        padding={"top": 15, "bottom": 15, "left": 15, "right": 15}
    ).configure(
        background='transparent'
    ).configure_view(
        strokeWidth=0
    ).configure_title(
        fontSize=15,
        fontWeight="bold"
    )
    
    st.altair_chart(chart, use_container_width=True)

def plot_hot_vs_iced_distribution(df, title="Temperature Duel: Hot vs. Iced"):
    """Plots stacked / grouped comparison of Hot vs Iced beverages per user."""
    if df.empty or "drink_id" not in df.columns:
        st.info("No temperature metadata available.")
        return
        
    df_copy = df.copy()
    
    def classify_temp(did):
        if did == 1:
            return "Hot Coffee"
        elif did == 3:
            return "Iced Coffee"
        elif did == 2:
            return "Hot Tea"
        elif did == 4:
            return "Iced Tea"
        return "Hot Coffee"

    df_copy["drink_type"] = df_copy["drink_id"].apply(classify_temp)
    # Strip user (coffee)/(tea) suffix for clean grouping
    df_copy["clean_user"] = df_copy["user_name"].str.replace(" (coffee)", "", regex=False).str.replace(" (tea)", "", regex=False)
    
    temp_counts = df_copy.groupby(["clean_user", "drink_type"])["value"].sum().reset_index()
    
    chart = alt.Chart(temp_counts).mark_bar(
        cornerRadiusTopLeft=6,
        cornerRadiusTopRight=6,
        opacity=0.9
    ).encode(
        x=alt.X('clean_user:N', title='User', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('value:Q', title='Drinks Logged', axis=alt.Axis(gridColor="rgba(128,128,128,0.12)")),
        color=alt.Color('drink_type:N', scale=alt.Scale(
            domain=['Hot Coffee', 'Iced Coffee', 'Hot Tea', 'Iced Tea'],
            range=['#D97706', '#0284C7', '#059669', '#10B981']
        ), legend=alt.Legend(orient="bottom", title="Drink & Temperature")),
        xOffset='drink_type:N',
        tooltip=['clean_user:N', 'drink_type:N', 'value:Q']
    ).properties(
        title=title,
        height=320
    ).configure(
        background='transparent'
    ).configure_view(
        strokeWidth=0
    ).configure_title(
        fontSize=15,
        fontWeight="bold"
    )
    
    st.altair_chart(chart, use_container_width=True)

def plot_cumulative_projections(df_filtered, p_start, p_end, chart_users, title):
    """Plots actual cumulative line with dotted linear regression projection to end of period."""
    from data_processing import get_cumulative_data
    now = pd.Timestamp.now(tz="Europe/Madrid")
    trend_df = get_cumulative_data(df_filtered, p_start, now, chart_users, "D")
    
    if trend_df.empty:
        st.info("No trend data to project.")
        return None
        
    source = trend_df.reset_index().melt('index', var_name='User', value_name='Amount')
    source = source.groupby('User').filter(lambda x: x['Amount'].max() > 0)
    
    if source.empty:
        st.info("No active users in this period to project.")
        return None

    # Strip timezone for clean Vega-Lite date parsing
    if hasattr(source['index'].dt, 'tz') and source['index'].dt.tz is not None:
        source['index'] = source['index'].dt.tz_localize(None)

    proj_lines = []
    projected_final_values = {}
    
    p_start_naive = pd.to_datetime(p_start).tz_localize(None) if hasattr(p_start, 'tz') and p_start.tz is not None else pd.to_datetime(p_start)
    p_end_naive = pd.to_datetime(p_end).tz_localize(None) if hasattr(p_end, 'tz') and p_end.tz is not None else pd.to_datetime(p_end)

    for user in source['User'].unique():
        user_data = source[source['User'] == user].copy()
        active_data = user_data[user_data['Amount'] > 0].copy()
        
        if len(active_data) > 1:
            active_data['day_num'] = (active_data['index'] - p_start_naive).dt.total_seconds() / 86400.0
            x = active_data['day_num'].values
            y = active_data['Amount'].values
            slope, intercept = np.polyfit(x, y, 1)
            
            end_day_num = (p_end_naive - p_start_naive).total_seconds() / 86400.0
            last_actual_val = user_data['Amount'].max()
            raw_final = slope * end_day_num + intercept
            final_val = max(last_actual_val, raw_final)
            projected_final_values[user] = final_val
            
            proj_df = pd.DataFrame({
                'index': [p_start_naive, p_end_naive],
                'Amount': [max(0, intercept), final_val],
                'User': user
            })
            proj_lines.append(proj_df)
        else:
            final_val = user_data['Amount'].max()
            projected_final_values[user] = final_val
            proj_df = pd.DataFrame({
                'index': [user_data['index'].max(), p_end_naive],
                'Amount': [final_val, final_val],
                'User': user
            })
            proj_lines.append(proj_df)

    proj_source = pd.concat(proj_lines) if proj_lines else pd.DataFrame()
    
    chart_actual = alt.Chart(source).mark_line(point=True, strokeWidth=3, interpolate="monotone").encode(
        x=alt.X('index:T', title='Date', axis=alt.Axis(format='%b %d', gridColor="rgba(128,128,128,0.12)")),
        y=alt.Y('Amount:Q', stack=False, title='Total Drinks', axis=alt.Axis(gridColor="rgba(128,128,128,0.12)")),
        color=alt.Color('User:N', scale=get_color_scale(source['User']), legend=alt.Legend(orient="bottom", columns=3)),
        tooltip=['index:T', 'User:N', 'Amount:Q']
    )
    
    if not proj_source.empty:
        chart_proj = alt.Chart(proj_source).mark_line(strokeDash=[6, 6], opacity=0.6, strokeWidth=2.5).encode(
            x=alt.X('index:T', title='Date'),
            y=alt.Y('Amount:Q', stack=False),
            color=alt.Color('User:N', scale=get_color_scale(source['User'])),
            tooltip=['index:T', 'User:N', alt.Tooltip('Amount:Q', format='.1f', title='Projected')]
        )
        final_chart = chart_actual + chart_proj
    else:
        final_chart = chart_actual
        
    final_chart = final_chart.properties(
        title=title,
        height=350
    ).configure(
        background='transparent'
    ).configure_view(
        strokeWidth=0
    ).configure_title(
        fontSize=15,
        fontWeight="bold"
    )
    
    st.altair_chart(final_chart, use_container_width=True)
    
    sorted_proj = dict(sorted(projected_final_values.items(), key=lambda item: item[1], reverse=True))
    return sorted_proj

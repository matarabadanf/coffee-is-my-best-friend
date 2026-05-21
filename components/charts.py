import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# Custom colors for users (Vibrant colors + Fer's mandatory color)
USER_COLORS = {
    "Cris (coffee)": "#4ECDC4",   # Turquoise
    "Cris (tea)": "#FFB6C1",      # Light Pink
    "Bea (coffee)": "#FF6B6B",    # Coral Red
    "Bea (tea)": "#FFA07A",       # Salmon
    "Fer (coffee)": "rebeccapurple",
    "Fer (tea)": "rebeccapurple"  # Must always be rebeccapurple
}

def get_color_scale(data_items):
    """Returns domain and range for only the items present in the data."""
    unique_items = list(set(data_items))
    domain = []
    range_ = []
    for item in unique_items:
        domain.append(item)
        range_.append(USER_COLORS.get(item, "#888888")) # Fallback color
    return alt.Scale(domain=domain, range=range_)

def render_pie_chart(scores_dict, label_col, val_col, is_coffee=True):
    pie_df = pd.DataFrame(list(scores_dict.items()), columns=[label_col, val_col])
    
    # Avoid division by zero if empty
    if pie_df.empty or pie_df[val_col].sum() == 0:
        return

    pie_df['Percentage'] = pie_df[val_col] / pie_df[val_col].sum()

    base = alt.Chart(pie_df).encode(
        theta=alt.Theta(val_col, stack=True)
    )
    
    pie = base.mark_arc(outerRadius=100).encode(
        color=alt.Color(label_col, scale=get_color_scale(pie_df[label_col])),
        order=alt.Order(val_col, sort="descending"),
        tooltip=[label_col, val_col, alt.Tooltip("Percentage", format=".1%")]
    )
    
    text = base.mark_text(radius=120).encode(
        text=alt.Text("Percentage", format=".1%"),
        order=alt.Order(val_col, sort="descending"),
        color=alt.value("#4A3B32")
    )
    
    chart_pie = (pie + text).properties(
        title="",
        height=350
    ).configure(
        background='transparent'
    ).configure_view(
        strokeWidth=0
    ).configure_title(
        fontSize=16, color='#4A3B32'
    ).configure_legend(
        labelColor='#4A3B32', titleColor='#4A3B32'
    )
    
    st.altair_chart(chart_pie, use_container_width=True)

def plot_metric(data, title):
    # Melt to long format for Altair
    source = data.reset_index().melt('index', var_name='User', value_name='Amount')
    
    # Filter out users who have 0 total drinks in this period
    source = source.groupby('User').filter(lambda x: x['Amount'].max() > 0)
    
    if source.empty:
        st.info("No data available for this period.")
        return
        
    y_max = source['Amount'].max()
    y_domain_max = y_max * 1.1 if y_max > 0 else 5
    
    chart = alt.Chart(source).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X('index', title='Date', axis=alt.Axis(format='%b %d')),
        y=alt.Y('Amount', scale=alt.Scale(domain=[0, y_domain_max])),
        color=alt.Color('User', scale=get_color_scale(source['User'])),
        tooltip=['index', 'User', 'Amount']
    ).properties(
        title=title,
        height=300
    ).configure(
        background='transparent'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        gridColor='#E0E0E0',
        domainColor='#4A3B32',
        tickColor='#4A3B32',
        labelColor='#4A3B32',
        titleColor='#4A3B32'
    ).configure_legend(
        labelColor='#4A3B32',
        titleColor='#4A3B32'
    ).configure_title(
        fontSize=16,
        color='#4A3B32'
    )
    
    st.altair_chart(chart, use_container_width=True)

def plot_hourly_distribution(df, title="Time of Day Distribution"):
    """Plot the distribution of drinks by hour of the day."""
    if df.empty:
        st.info("No data available for this chart.")
        return
        
    # Extract hour and count
    df_copy = df.copy()
    if df_copy["created_at"].dt.tz is None:
        df_copy["created_at"] = df_copy["created_at"].dt.tz_localize("UTC")
    df_copy["created_at"] = df_copy["created_at"].dt.tz_convert("Europe/Madrid")
    
    df_copy["hour"] = df_copy["created_at"].dt.hour
    hourly_counts = df_copy.groupby(["user_name", "hour"])["value"].sum().reset_index()
    
    # Create complete index for 0-23 hours
    hours_df = pd.DataFrame({'hour': range(24)})
    
    chart = alt.Chart(hourly_counts).mark_bar(opacity=0.8).encode(
        x=alt.X('hour:O', title='Hour of Day (0-23)'),
        y=alt.Y('value:Q', title='Total Drinks'),
        color=alt.Color('user_name:N', scale=get_color_scale(hourly_counts['user_name']), title="User"),
        tooltip=['user_name', 'hour', 'value']
    ).properties(
        title=title,
        height=300
    ).configure(
        background='transparent'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        gridColor='#E0E0E0',
        domainColor='#4A3B32',
        tickColor='#4A3B32',
        labelColor='#4A3B32',
        titleColor='#4A3B32'
    ).configure_legend(
        labelColor='#4A3B32',
        titleColor='#4A3B32'
    ).configure_title(
        fontSize=16,
        color='#4A3B32'
    )
    
    st.altair_chart(chart, use_container_width=True)

def plot_weekday_distribution(df, title="Day of Week Distribution"):
    """Plot the distribution of drinks by day of the week."""
    if df.empty:
        st.info("No data available for this chart.")
        return
        
    df_copy = df.copy()
    if df_copy["created_at"].dt.tz is None:
        df_copy["created_at"] = df_copy["created_at"].dt.tz_localize("UTC")
    df_copy["created_at"] = df_copy["created_at"].dt.tz_convert("Europe/Madrid")
    
    df_copy["weekday_num"] = df_copy["created_at"].dt.dayofweek
    df_copy["weekday_name"] = df_copy["created_at"].dt.day_name()
    
    weekday_counts = df_copy.groupby(["user_name", "weekday_num", "weekday_name"])["value"].sum().reset_index()
    
    chart = alt.Chart(weekday_counts).mark_bar(opacity=0.8).encode(
        x=alt.X('weekday_name:O', title='', sort=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']),
        y=alt.Y('value:Q', title='Total Drinks'),
        color=alt.Color('user_name:N', scale=get_color_scale(weekday_counts['user_name']), title="User"),
        tooltip=['user_name', 'weekday_name', 'value']
    ).properties(
        title=title,
        height=300
    ).configure(
        background='transparent'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        gridColor='#E0E0E0',
        labelAngle=0,
        domainColor='#4A3B32',
        tickColor='#4A3B32',
        labelColor='#4A3B32',
        titleColor='#4A3B32'
    ).configure_legend(
        labelColor='#4A3B32',
        titleColor='#4A3B32'
    ).configure_title(
        fontSize=16,
        color='#4A3B32'
    )
    
    st.altair_chart(chart, use_container_width=True)

def plot_average_weekday_distribution(df, title="Average Drinks per Day of Week"):
    """Plot the average drinks per day of the week, accounting for days with zero logs."""
    if df.empty:
        st.info("No data available for this chart.")
        return
        
    df_copy = df.copy()
    if df_copy["created_at"].dt.tz is None:
        df_copy["created_at"] = df_copy["created_at"].dt.tz_localize("UTC")
    df_copy["created_at"] = df_copy["created_at"].dt.tz_convert("Europe/Madrid")
    
    # Calculate the total number of each weekday in the date range
    start_date = df_copy["created_at"].min().floor("D")
    end_date = df_copy["created_at"].max().ceil("D")
    
    # Use inclusive range covering start_date to end_date
    if start_date == end_date:
        end_date = end_date + pd.Timedelta(days=1)
        
    date_range = pd.date_range(start_date, end_date, inclusive="left")
    if len(date_range) == 0:
        date_range = pd.date_range(start_date, start_date + pd.Timedelta(days=1), inclusive="left")
        
    total_weekdays = date_range.day_name().value_counts()
    
    df_copy["weekday_num"] = df_copy["created_at"].dt.dayofweek
    df_copy["weekday_name"] = df_copy["created_at"].dt.day_name()
    
    # Sum up the drinks per user per weekday
    weekday_sums = df_copy.groupby(["user_name", "weekday_num", "weekday_name"])["value"].sum().reset_index()
    
    # Guarantee every user has a row for all 7 days so the line drops to 0
    users_in_df = df_copy["user_name"].unique()
    all_days = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), 
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ]
    complete_index = pd.MultiIndex.from_product([users_in_df, [d[0] for d in all_days]], names=["user_name", "weekday_num"])
    complete_df = pd.DataFrame(index=complete_index).reset_index()
    complete_df["weekday_name"] = complete_df["weekday_num"].map({d[0]: d[1] for d in all_days})
    
    weekday_sums = pd.merge(complete_df, weekday_sums, on=["user_name", "weekday_num", "weekday_name"], how="left").fillna({"value": 0})
    
    # Calculate the true average by dividing by the number of times that weekday occurred
    def calculate_average(row):
        count = total_weekdays.get(row['weekday_name'], 1)
        # Avoid division by zero
        return row['value'] / count if count > 0 else 0
        
    weekday_sums['average'] = weekday_sums.apply(calculate_average, axis=1)
    
    chart = alt.Chart(weekday_sums).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X('weekday_name:O', title='', 
                sort=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], 
                scale=alt.Scale(domain=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']),
                axis=alt.Axis(labelOverlap=False, labelAngle=-45)),
        y=alt.Y('average:Q', title='Average Drinks'),
        color=alt.Color('user_name:N', scale=get_color_scale(weekday_sums['user_name']), title="User"),
        tooltip=[
            'user_name', 
            'weekday_name', 
            alt.Tooltip('average', format='.2f', title='Average')
        ]
    ).properties(
        title=title,
        height=300
    ).configure(
        background='transparent'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        gridColor='#E0E0E0',
        labelAngle=0,
        domainColor='#4A3B32',
        tickColor='#4A3B32',
        labelColor='#4A3B32',
        titleColor='#4A3B32'
    ).configure_legend(
        labelColor='#4A3B32',
        titleColor='#4A3B32'
    ).configure_title(
        fontSize=16,
        color='#4A3B32'
    )
    
    st.altair_chart(chart, use_container_width=True)

def plot_cumulative_projections(df_filtered, p_start, p_end, chart_users, title):
    # Get cumulative data up to NOW
    from data_processing import get_cumulative_data
    now = pd.Timestamp.now(tz="Europe/Madrid")
    trend_df = get_cumulative_data(df_filtered, p_start, now, chart_users, "D")
    
    if trend_df.empty:
        st.info("No trend data to project.")
        return None
        
    # Melt to long format
    source = trend_df.reset_index().melt('index', var_name='User', value_name='Amount')
    source = source.groupby('User').filter(lambda x: x['Amount'].max() > 0)
    
    if source.empty:
        st.info("No active users in this period to project.")
        return None

    # Calculate regression for each user
    proj_lines = []
    projected_final_values = {}
    
    for user in source['User'].unique():
        user_data = source[source['User'] == user].copy()
        
        # Filter out leading zeroes so they don't drag down the regression
        active_data = user_data[user_data['Amount'] > 0].copy()
        
        # Need at least 2 points for a meaningful regression
        if len(active_data) > 1:
            # Convert dates to numeric (days since p_start)
            active_data['day_num'] = (active_data['index'] - p_start).dt.total_seconds() / 86400.0
            
            x = active_data['day_num'].values
            y = active_data['Amount'].values
            
            # Linear fit (y = mx + b)
            slope, intercept = np.polyfit(x, y, 1)
            
            # Predict up to p_end
            end_day_num = (p_end - p_start).total_seconds() / 86400.0
            
            last_actual_date = user_data['index'].max()
            last_actual_val = user_data['Amount'].max()
            
            # Calculate final projected value
            raw_final = slope * end_day_num + intercept
            final_val = max(last_actual_val, raw_final)
            
            projected_final_values[user] = final_val
            
            # Create a dataframe for the projection line
            # The dashed line spans the entire timeframe based on the regression intercept
            proj_df = pd.DataFrame({
                'index': [p_start, p_end],
                'Amount': [max(0, intercept), final_val],
                'User': user
            })
            proj_lines.append(proj_df)
        else:
            # If only 1 point or no active data, assume flat
            final_val = user_data['Amount'].max()
            projected_final_values[user] = final_val
            proj_df = pd.DataFrame({
                'index': [user_data['index'].max(), p_end],
                'Amount': [final_val, final_val],
                'User': user
            })
            proj_lines.append(proj_df)

    proj_source = pd.concat(proj_lines) if proj_lines else pd.DataFrame()
    
    # Plot original solid lines
    chart_actual = alt.Chart(source).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X('index', title='Date', axis=alt.Axis(format='%b %d')),
        y=alt.Y('Amount', title='Total Drinks'),
        color=alt.Color('User', scale=get_color_scale(source['User'])),
        tooltip=['index', 'User', 'Amount']
    )
    
    # Plot dashed projection lines
    if not proj_source.empty:
        chart_proj = alt.Chart(proj_source).mark_line(strokeDash=[5, 5], opacity=0.5, strokeWidth=3).encode(
            x=alt.X('index', title='Date'),
            y=alt.Y('Amount'),
            color=alt.Color('User', scale=get_color_scale(source['User'])),
            tooltip=['index', 'User', alt.Tooltip('Amount', format='.1f', title='Projected')]
        )
        final_chart = chart_actual + chart_proj
    else:
        final_chart = chart_actual
        
    final_chart = final_chart.properties(
        title=title,
        height=350
    ).configure(
        background='transparent'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        gridColor='#E0E0E0',
        domainColor='#4A3B32',
        tickColor='#4A3B32',
        labelColor='#4A3B32',
        titleColor='#4A3B32'
    ).configure_legend(
        labelColor='#4A3B32',
        titleColor='#4A3B32'
    ).configure_title(
        fontSize=16,
        color='#4A3B32'
    )
    
    st.altair_chart(final_chart, use_container_width=True)
    
    # Sort projected_values descending for display
    sorted_proj = dict(sorted(projected_final_values.items(), key=lambda item: item[1], reverse=True))
    return sorted_proj

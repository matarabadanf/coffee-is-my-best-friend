import streamlit as st
import pandas as pd
import altair as alt

# Custom colors for users
DOMAIN = ["Cris", "Bea", "Fer", "Bea(tea)"]
RANGE_ = ["#1f77b4", "#ff7f0e", "rebeccapurple", "#2ca02c"]

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
        color=alt.Color(label_col, scale=alt.Scale(domain=DOMAIN, range=RANGE_)),
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
        background='#DDC7A0' 
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
    
    y_max = source['Amount'].max()
    y_domain_max = y_max * 1.1 if y_max > 0 else 5
    
    chart = alt.Chart(source).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X('index', title='Date', axis=alt.Axis(format='%b %d')),
        y=alt.Y('Amount', scale=alt.Scale(domain=[0, y_domain_max])),
        color=alt.Color('User', scale=alt.Scale(domain=DOMAIN, range=RANGE_)),
        tooltip=['index', 'User', 'Amount']
    ).properties(
        title=title,
        height=300
    ).configure(
        background='#DDC7A0'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        gridColor='#000000',
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

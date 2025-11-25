import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import streamlit as st
from utils import format_revenue

def create_data_metric(label, current_value, previous_value):
    if previous_value == 0 or previous_value is None:
        delta_reference = None
    else:
        delta_reference = previous_value

    indicator = go.Indicator(
        mode="number+delta",
        value=current_value,
        delta={"reference": delta_reference,
                "relative": True,
                "valueformat": ".2%",
                "increasing": {"color": "green"},
                "decreasing": {"color": "red"},},
        number={"valueformat": ",.2s",
                },
        title={"text": label},
    )
    fig = go.Figure(indicator)
    fig.update_layout(height=200, margin=dict(t=30, b=10, l=10, r=10))
    return fig

def create_line_chart(data, x, y, x_label=None, y_label=None, color=None, height=None, markers=None):
    chart = px.line(
        data,
        x=x,
        y=y,
        color=color,
        height=height,
        markers=markers
    )
    chart.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
    )
    chart.update_xaxes(
        tickformat="%m-%d",
        type="category"
    ) 
    return chart

import plotly.express as px

import plotly.express as px

def create_bar_chart(
    data,
    x,
    y,
    x_label=None,
    y_label=None,
    color=None,
    height=None,
    orientation=None,
    ):
    chart = px.bar(
        data,
        x=x,
        y=y,
        color=color,
        height=height,
        orientation=orientation
    )

    chart.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
    )

    if orientation == 'v':
        chart.update_xaxes(
            tickformat="%m-%d" if orientation != "v" else None,
            type="category"
        )
    return chart

def create_pie_chart(data, names, values, height=None, hole=None):
    chart = px.pie(
        data,
        names,
        values,
        height=height,
        hole=hole
    )
    chart.update_layout(
    legend=dict(
        orientation="h",
        x=0.5,
        y=-0.1,  # moves legend below the chart
        xanchor="center",
        yanchor="top",
        )
    )
    return chart

def create_choropleth_map(data, locations, color, title, geojson, locationmode='ISO-3'):
    chart = px.choropleth(
        data,
        locations=locations,
        color=color,
        geojson=geojson,
        locationmode=locationmode,
        color_continuous_scale="Viridis",
        title=title
    )
    chart.update_geos(fitbounds="locations", visible=False)
    chart.update_layout(margin={"r":0,"t":30,"l":0,"b":0})

    return chart

def create_folium_map_object(data, geo_data, value_columns, key_on, legend_name):
    choropleth_map = folium.Map(location=[16,108], zoom_start=5, tiles="cartodbpositron")

    folium.Choropleth(
        geo_data=geo_data,
        data=data,
        columns=value_columns,
        key_on=key_on,
        fill_color="YlGnBu",
        fill_opacity=0.7,
        line_opacity=0.5,
        legend_name=legend_name,
    ).add_to(choropleth_map)

    return choropleth_map

def render_folium_map(map_obj, geo_data, tooltip_fields):
    folium.GeoJson(
        geo_data,
        style_function=lambda x: {"fillOpacity": 0, "color": "black", "weight": 1},
        tooltip=folium.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=[f"{t}:" for t in tooltip_fields]
        )
    ).add_to(map_obj)

    return st_folium(map_obj, height=400, width="100%")

def create_combined_charts(chart_1, chart_2, height=None):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for trace in chart_1.data:
        fig.add_trace(trace, secondary_y=False)

    for trace in chart_2.data:
        fig.add_trace(trace, secondary_y=True)

    fig.update_layout(height=height)
    return st.plotly_chart(fig)



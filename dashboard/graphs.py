import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import streamlit as st
from utils import format_revenue

def create_data_metric(label, current_value, previous_value):
    if previous_value is None or previous_value == 0:
        delta_value = 0
    else:
        delta_value = (current_value - previous_value) / previous_value

    formatted_current = format_revenue(current_value)

    if previous_value is None or previous_value == 0:
        formatted_delta = "0%"
    else:
        sign = "-" if delta_value < 0 else "+"
        formatted_delta = f"{sign}{abs(delta_value) * 100:.2f} %"

    return st.metric(
        label=label,
        value=formatted_current,
        border=True,
        delta=formatted_delta,
        delta_color="normal",
    )

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
    return st.plotly_chart(chart)

def create_bar_chart(data, x, y, x_label=None, y_label=None, color=None, height=None, orientation=None):
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
    return st.plotly_chart(chart)

def create_pie_chart(data, names, values, height=None):
    chart = px.pie(
        data,
        names,
        values,
        height=height
    )
    return st.plotly_chart(chart)

def create_choropleth_map(data, locations, color, title, geojson, locationmode='ISO-3'):
    fig = px.choropleth(
        data,
        locations=locations,
        color=color,
        geojson=geojson,
        locationmode=locationmode,
        color_continuous_scale="Viridis",
        title=title
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})

    return st.plotly_chart(fig, use_container_width=True)

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
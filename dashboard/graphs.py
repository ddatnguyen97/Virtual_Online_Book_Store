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

def create_line_chart(data, x, y):
    return st.line_chart(
        data=data,
        x=x,
        y=y,
    )

def create_bar_chart(data, x, y, horizontal=False, height=400):
    return st.bar_chart(
        data=data,
        x=x,
        y=y,
        horizontal=horizontal,
        height=height
    )

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

def create_folium_map(data, 
                      geo_data,
                      location=[16, 108],
                      zoom_start=5,
                      tiles='cartodbpositron',
                      value_columns=None,        
                      tooltip_fields=None,
                      key_on=None,
                      legend_name=None,
                    #   container_height=None,
            ):
    choropleth_map = folium.Map(location=location,
                                 zoom_start=zoom_start,
                                 tiles=tiles,
    )

    folium.Choropleth(
    geo_data=geo_data,
    name="choropleth",
    data=data,
    columns=value_columns,
    key_on=key_on,
    fill_color="YlGnBu",
    fill_opacity=0.7,
    line_opacity=0.5,
    legend_name=legend_name,
    ).add_to(choropleth_map)

    folium.GeoJson(
        geo_data,
        name="Province Borders",
        style_function=lambda x: {
            "fillOpacity": 0,
            "color": "black",
            "weight": 1
        },
        tooltip=folium.GeoJsonTooltip(
            fields=tooltip_fields,       
            aliases=[f"{field}:" for field in tooltip_fields],  
            sticky=False,
            labels=True,
            style="""
                background-color: white;
                border: 1px solid black;
                border-radius: 3px;
                padding: 2px;
            """
        )
    ).add_to(choropleth_map)

    return st_folium(choropleth_map, 
                     height="400",
                     width="100%",
                          )

    
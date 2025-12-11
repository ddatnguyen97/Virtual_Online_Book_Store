import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

def create_data_metric(label, current_value=None, previous_value=None):
    if previous_value == 0 or previous_value is None:
        delta_reference = None
    else:
        delta_reference = previous_value

    indicator = go.Indicator(
        mode="number+delta",
        value=current_value,
        delta={
                "reference": delta_reference,
                "relative": True,
                "valueformat": ".2%",
                "increasing": {"color": "green"},
                "decreasing": {"color": "red"},
                "font": {"size": 35}
                },
        number={    
                "valueformat": ",.2s",
                "font": {"size": 45}
                },
        title={
                "text": label,
                "font": {"size": 25},
               },
    )
    fig = go.Figure(indicator)
    fig.update_layout(height=180, margin=dict(t=30, b=10, l=10, r=10))
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
        yaxis=dict(rangemode='tozero')
    )
    chart.update_xaxes(
        tickformat="%m-%d",
        type="category"
    ) 
    return chart

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
        orientation=orientation,
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

def create_pie_chart(data, names, values, height=None, hole=None, category_orders=None):
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
            y=-0.1,
            xanchor="center",
            yanchor="top",
        )
    )
    chart.update_traces(
        sort=False,
    )
    return chart

def create_choropleth_map(data, locations, color, color_scale, geojson, featureidkey, height=None):
    chart = px.choropleth(
        data,
        locations=locations,
        color=color,
        geojson=geojson,
        featureidkey=featureidkey,
        color_continuous_scale=color_scale,
    )
    chart.update_geos(
        fitbounds="locations", 
        visible=False,
        projection_scale=5
    )
    
    chart.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=0, r=0, t=50, b=0)
    )

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

def create_histogram_chart(data, x=None, y=None, x_label=None, y_label=None, nbins=None, height=None):
    chart = px.histogram(
        data,
        x=x,
        y=y,
        nbins=nbins,
        height=height
    )
    chart.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
    )
    return chart

def create_treemap_chart(data, path, values, height=None):
    if isinstance(path, str):
        path = [path]
    chart = px.treemap(
        data,
        path=path,
        values=values,
        height=height
    )
    chart.update_traces(
        marker=dict(cornerradius=5)
    )

    return chart 

def create_data_table(df, height=None, column_width=None):
    table = go.Figure(
        data=[
            go.Table(
                columnwidth=column_width,
                header=dict(
                    values=list(df.columns),
                    fill_color="lightgrey",
                    align="left",
                    font=dict(size=12, color="black"),
                ),
                cells=dict(
                    values=[df[col] for col in df.columns],
                    align="left",
                    font=dict(size=12),
                    height=30,
                )
            )
        ]
    )
    table.update_layout(height=height)
    return table
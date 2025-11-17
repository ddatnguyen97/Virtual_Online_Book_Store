import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

def create_data_metric(label, value):
    return st.metric(
                    label=label,
                    value=value,
                    border=True,
                    delta=float('nan'),
                    delta_color="normal",
                    )
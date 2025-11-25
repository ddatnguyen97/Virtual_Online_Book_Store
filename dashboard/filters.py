import streamlit as st

def build_filters(df):
    st.title("Filters")

    filters = {}

    for col in df.select_dtypes(include=["object", "category"]).columns:
        unique_values = df[col].dropna().unique().tolist()
        filters[col] = st.multiselect(col.capitalize(), unique_values)
    return filters

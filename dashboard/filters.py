import streamlit as st

def build_filters(df, key_label):
    st.title("Filters")
    filters = {}

    for col in df.select_dtypes(include=["object", "category"]).columns:
        unique_values = df[col].dropna().unique().tolist()
        filters[col] = st.multiselect(
            label=col.capitalize(),
            options=unique_values,
            key=f"filter_{key_label}_{col}"
        )

    return filters

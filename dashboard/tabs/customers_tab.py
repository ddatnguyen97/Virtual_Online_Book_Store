import streamlit as st

from data import *
from metrics.customer_metrics import *
from graphs import *
from filters import *
from utils import *

def customer_tab():
    st.header("Customer Overview")
    total_customers = metrics_total_customers['total_customers'].iloc[0]
    col = st.columns(1)[0]
    col.metric(label="Total Customers", value=total_customers)

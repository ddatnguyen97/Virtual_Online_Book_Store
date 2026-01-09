import streamlit as st

def home_tab():
    st.header("Welcome to the Virtual Online Book Store")
    st.markdown(
        """
        This dashboard provides insights into sales, customer behavior, and product performance for the Virtual Online Book Store.
        
        Use the tabs above to navigate through different sections of the dashboard:
        
        - **Sales**: Analyze weekly sales performance, including revenue, orders, average order value, growth trends, payment behavior, and geographic distribution.
        - **Customers**: Monitor customer growth, retention, and engagement using RFM analysis, demographic breakdowns, and geographic distribution.
        - **Products**: Analyze product and category performance across revenue, sales volume, pricing efficiency, and repeat purchase behavior.
        
        Select a date from the sidebar to filter data accordingly. Use the filters within each tab to customize your view further.
        
        Enjoy exploring the data!
        """
    )
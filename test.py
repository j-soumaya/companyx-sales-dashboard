import pandas as pd  
import plotly.express as px 
import streamlit as st  
from PIL import Image
import json

st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")

@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
            io="data clean complete2.xlsx",
            engine="openpyxl",
            sheet_name="data",
            skiprows=0,
            usecols="A:N",
            nrows=10
        )
    return df

df = get_data_from_excel()


# ---- SIDEBAR ----
st.sidebar.header("Use Filters Here:")

company = st.sidebar.multiselect(
    "Select the Company:",
    options=df["Company Name"].unique(),
    default=df["Company Name"].unique()
)

year = st.sidebar.multiselect(
    "Select the year:",
    options=df["Year"].unique(),
    default=df["Year"].unique()
)

activity = st.sidebar.multiselect(
    "Select the activity:",
    options=df["Company Activity"].unique(),
    default=df["Company Activity"].unique()
)

# df_selection = df.query(
#     "Company Name == @company & Year ==@year & Company Activity == @activity"
# )


# df_selection = df.query(
#     "Société == @company & ANNEE ==@year & ACTIVITE == @activity"
# )

# df_selection = df

# df_selection = df.query(f'"Company Name" == "{company}" & Year == {int(year)} & "Company Activity" == "{activity}"')

# df_selection = df.query('Year == @year & Company Name == @company')

# df_selection = df[(df['Company Name'].isin([company])) & (df['Year'].isin(year)) & (df['Company Activity'].isin([activity]))]


df_selection = df.query("`Company Name` == @company and `Year` == @year and `Company Activity` == @activity ")


# st.write(f"`Company Name` == '{company}'")
# st.write(f"Year == {year}")
# st.write(f"`Company Activity` == '{activity}'")

st.write(df_selection)
import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
from PIL import Image
import json

st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")

# define a function to categorize market type
def categorize_market_type(receipt):
    first_letter = receipt[0]
    if first_letter == 'F':
        return 'Local'
    elif first_letter in['M','E']:
        return 'Export'
    else: 
        return None

@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
            io="data.xlsx",
            engine="openpyxl",
            sheet_name="xx",
            skiprows=0,
            usecols="A:AL",
            nrows=447782 #447782 
        )
    df['market'] = df['Adr fact'].apply(categorize_market_type)
    df = df.dropna(subset=['market'])
    return df

df = get_data_from_excel()

#st.dataframe(df)

#style CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

#JSON
with open('gov.geojson', 'r', encoding='utf-8') as j:
    geojson_data = json.load(j)

for feature in geojson_data['features']:
    # Convert 'name' property to uppercase
    if 'name' in feature['properties']:
        if isinstance(feature['properties']['name'], str):
            feature['properties']['name'] = feature['properties']['name'].upper()
    
    # Convert 'name:fr' property to uppercase
    if 'name:fr' in feature['properties']:
        if isinstance(feature['properties']['name:fr'], str):
            feature['properties']['name:fr'] = feature['properties']['name:fr'].upper()

# Save modified GeoJSON file
with open('gov_modified.geojson', 'w', encoding='utf-8') as j:
    json.dump(geojson_data, j)

# ---- SIDEBAR ----
st.sidebar.header("Use Filters Here:")

# city = st.sidebar.multiselect(
#     "Select the City:",
#     options=df["GOUVERNORAT"].unique(),
#     default=df["GOUVERNORAT"].unique()
# )

company = st.sidebar.multiselect(
    "Select the Company:",
    options=df["Société"].unique(),
    default=df["Société"].unique()
)

year = st.sidebar.multiselect(
    "Select the year:",
    options=df["ANNEE"].unique(),
    default=df["ANNEE"].unique()
)

activity = st.sidebar.multiselect(
    "Select the activity:",
    options=df["ACTIVITE"].unique(),
    default=df["ACTIVITE"].unique()
)

df_selection = df.query(
    "Société == @company & ANNEE ==@year & ACTIVITE == @activity"
)


# ---- MAINPAGE ----
EY = Image.open('assets/EY_logo.png')
companyX = Image.open('assets/companyXwhite.png')

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.image(EY, width=100)
with middle_column:
    st.markdown("##")
    st.title("Sales Dashboard")
with right_column:
    st.markdown("##")
    st.markdown("##")
    left_column,right_column =st.columns(2)
    with left_column:
        st.text("")
    with right_column:
        st.image(companyX, width=200)

# st.markdown("""---""")
st.markdown("##")

# different pages/tabs
tab1, tab2, tab3 = st.tabs(["Overall Sales", "Local Sales", "Export Sales"])

# TOP KPI's
total_sales = int(df_selection["HT"].sum())
total_quantity_sold = round(df_selection["Quantité facturée"].sum())
#star_rating = ":star:" * int(round(average_rating, 0))
average_sale_by_transaction = round(df_selection["HT"].mean(), 2)


# SALES BY COMPANY [BAR CHART]
sales_by_company = (
    df_selection.groupby(by=["Société"]).sum()[["HT"]].sort_values(by="HT")
)
fig_company_sales = px.bar(
    sales_by_company,
    x="HT",
    y=sales_by_company.index,
    orientation="h",
    title="<b>Sales by Company</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_company),
    template="plotly_white",
)

fig_company_sales.update_layout(
    xaxis_title="Total sales", 
    yaxis_title="Company",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)


# SALES BY YEAR [BAR CHART]
sales_by_year = df_selection.groupby(by=["ANNEE"]).sum()[["HT"]]
fig_yearly_sales = px.bar(
    sales_by_year,
    x=sales_by_year.index,
    y="HT",
    title="<b>Sales by year</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_year),
    template="plotly_white",
)
fig_yearly_sales.update_layout(
    xaxis_title="Year", 
    yaxis_title="Total sales",
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)

# SALES PER GAMME[BAR CHART]
sales_per_gamme = df_selection.groupby(by=["Ligne prod."]).sum()[["HT"]]

top_5 = sales_per_gamme.sort_values("HT", ascending=False).iloc[:5]
others = sales_per_gamme.loc[~sales_per_gamme.index.isin(top_5.index)]
other_sum = others["HT"].sum()
threshold = other_sum * 0.1

top_5_names = top_5.index.tolist()
top_5_names.append("Other")

top_5_values = top_5["HT"].tolist()
if other_sum > threshold:
    top_5_values.append(other_sum)
else:
    top_5_names.pop()

fig_sales_per_gamme = px.bar(
    x=top_5_names,
    y=top_5_values,
    title="<b>Sales per product line</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_per_gamme),
    template="plotly_white"
)
fig_sales_per_gamme.update_layout(
    xaxis_title="Product lines",
    yaxis_title="Total sales",
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)

# SALES PER MARKET TYPE[PIE CHART]
fig_sales_per_market = px.pie(
    df_selection, 
    values= "HT",
    names= "market",
    title="<b>Sales per market type</b>",
    color_discrete_sequence=["#0083B8","#A5D7E8"],
    template="plotly_white"
)

#SALES PER CITY [MAP]
df_selection = df_selection.dropna(subset=['GOUVERNORAT'])
city_coordinates = {
    'TUNIS': {'lat': 36.8065, 'lon': 10.1815},
    'SFAX': {'lat': 34.7406, 'lon': 10.7604},
    'SOUSSE': {'lat': 35.8288, 'lon': 10.6405},
    'ARIANA': {'lat': 36.8625, 'lon': 10.1944},
    'BEN AROUS': {'lat': 36.7531, 'lon': 10.2137},
    'BIZERTE': {'lat': 37.2628, 'lon': 9.8739},
    'BEJA': {'lat': 36.725, 'lon': 9.1814},
    'GABES': {'lat': 33.8825, 'lon': 10.1167},
    'GAFSA': {'lat': 34.425, 'lon': 8.7842},
    'JENDOUBA': {'lat': 36.5019, 'lon': 8.7761},
    'KAIROUAN': {'lat': 35.6786, 'lon': 10.0944},
    'KASSERINE': {'lat': 35.1683, 'lon': 8.8308},
    'KEBILI': {'lat': 33.7022, 'lon': 8.9691},
    'KEF': {'lat': 36.1829, 'lon': 8.7142},
    'MAHDIA': {'lat': 35.5014, 'lon': 11.0623},
    'MANOUBA': {'lat': 36.8089, 'lon': 10.0992},
    'Manouba': {'lat': 36.8089, 'lon': 10.0992},
    'MEDNINE': {'lat': 33.3542, 'lon': 10.4978},
    'MONASTIR': {'lat': 35.7878, 'lon': 10.8272},
    'NABEUL': {'lat': 36.4602, 'lon': 10.7345},
    'SIDI BOUZID': {'lat': 35.0317, 'lon': 9.4916},
    'SILIANA': {'lat': 36.0833, 'lon': 9.375},
    'TATAOUINE': {'lat': 32.9397, 'lon': 10.4511},
    'TOZEUR': {'lat': 33.9209, 'lon': 8.1339},
    'ZAGHOUAN': {'lat': 36.4012, 'lon': 10.1424}
}

# Add latitude and longitude columns based on the city names
df_selection['lat'] = df_selection['GOUVERNORAT'].apply(lambda x: city_coordinates[x]['lat'])
df_selection['lon'] = df_selection['GOUVERNORAT'].apply(lambda x: city_coordinates[x]['lon'])

fig_sales_per_city = px.choropleth_mapbox(
    df_selection,
    geojson=geojson_data,
    locations="GOUVERNORAT",
    color="HT",
    # featureidkey='properties.name:fr',
    hover_name='GOUVERNORAT',
    mapbox_style="carto-positron",
    zoom=5.5,
    center={"lat": 35.8, "lon": 10.2},
    opacity=0.8,
    labels={"HT": "Total Sales"}
)
fig_bubble = px.scatter_mapbox(
    df_selection,
    lat="lat",
    lon="lon",
    color="HT",
    size=abs(df_selection["HT"]),
    size_max=50,
    zoom=5.5,
    center={"lat": 35.8, "lon": 10.2},
    opacity=0.8,
    color_continuous_scale="Blues",
    hover_data={"HT": True, "lat": False, "lon": False},
    labels={"HT": "Total Sales"}
)

# Add the bubble map as a new trace on top of the choropleth map
fig_sales_per_city.add_trace(fig_bubble.data[0])

fig_sales_per_city.update_layout(
    title="<b>Sales per Tunisian City</b>",
    margin={"r":0,"t":0,"l":0,"b":0},
    coloraxis_showscale=False
)

#LOCAL SALES PER MONTH AND YEAR [BARCHART]

df_local_init = df_selection[df_selection["market"] == "Local"]

# Convert Date facture column to datetime and extract month-year as a new column
df_local_init["month-year"] = pd.to_datetime(df_local_init["Date facture"], format="%d/%m/%Y").dt.strftime("%B %Y")

# Group the data by month-year and sum the HT column
df_local = df_local_init.groupby("month-year").agg({"HT": "sum"}).reset_index()

# Create a list of all the month-year values in chronological order
month_year_list = sorted(df_local["month-year"], key=lambda x: pd.to_datetime(x, format="%B %Y"))
df_local_sorted = df_local.sort_values("month-year", key=lambda x: x.map({month_year_list[i]: i for i in range(len(month_year_list))}))


# Create the bar chart using Plotly Express
fig_local_sales = px.line(
    df_local_sorted,
    x="month-year",
    y="HT",
    color_discrete_sequence=["#0083B8"] * len(df_local),
    template="plotly_white",
    category_orders={"month-year": month_year_list},
    labels={"month-year": "Date", "HT": "Total Sales"}
)

# fig_local_sales.add_trace(
#     px.line(
#         df_local_sorted,
#         x="month-year",
#         y="HT",
#         color_discrete_sequence=["#FFA15A"],
#     ).data[0]
# )


fig_local_sales.update_layout(
    title="<b>Local Sales per Month and Year</b>",
    width=1200
)

# LOCAL SALES BY COMPANY [BAR CHART]
local_sales_by_company = (
    df_local_init.groupby(by=["Société"]).sum()[["HT"]].sort_values(by="HT")
)
fig_local_company_sales = px.bar(
    local_sales_by_company,
    x="HT",
    y=local_sales_by_company.index,
    orientation="h",
    title="<b>Local Sales by Company</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_company),
    template="plotly_white",
)

fig_local_company_sales.update_layout(
    xaxis_title="Total sales", 
    yaxis_title="Company",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

#LOCAL SALES PER GAMME [PIE CHART]
local_sales_per_gamme = df_local_init.groupby(by=["Ligne prod."]).sum()[["HT"]]

top_5 = local_sales_per_gamme.sort_values("HT", ascending=False).iloc[:5]
others = local_sales_per_gamme.loc[~local_sales_per_gamme.index.isin(top_5.index)]
other_sum = others["HT"].sum()
threshold = other_sum * 0.1

top_5_names = top_5.index.tolist()
top_5_names.append("Other")

top_5_values = top_5["HT"].tolist()
if other_sum > threshold:
    top_5_values.append(other_sum)
else:
    top_5_names.pop()

# fig_local_sales_per_gamme = px.bar(
#     x=top_5_names,
#     y=top_5_values,
#     title="<b>Local Sales per product line</b>",
#     color_discrete_sequence=["#0083B8"] * len(sales_per_gamme),
#     template="plotly_white"
# )

fig_local_sales_per_gamme = px.pie(
    df_local_init, 
    values= top_5_values,
    names= top_5_names,
    title="<b>Local Sales per product line</b>",
    # color_discrete_sequence=["#0083B8","#A5D7E8"],
    # color_discrete_sequence=px.colors.sequential.Blues_r,
    color_discrete_sequence = ["#084594", "#2171b5", "#4292c6", "#6baed6", "#9ecae1", "#c6dbef"],
    template="plotly_white"
)

#EXPORT SALES PER MONTH AND YEAR [BARCHART]

df_export_init = df_selection[df_selection["market"] == "Export"]

# Convert Date facture column to datetime and extract month-year as a new column
df_export_init["month-year"] = pd.to_datetime(df_export_init["Date facture"], format="%d/%m/%Y").dt.strftime("%B %Y")

# Group the data by month-year and sum the HT column
df_export = df_export_init.groupby("month-year").agg({"HT": "sum"}).reset_index()

# Create a list of all the month-year values in chronological order
month_year_list = sorted(df_export["month-year"], key=lambda x: pd.to_datetime(x, format="%B %Y"))
df_export_sorted = df_export.sort_values("month-year", key=lambda x: x.map({month_year_list[i]: i for i in range(len(month_year_list))}))


# Create the bar chart using Plotly Express
fig_export_sales = px.line(
    df_export_sorted,
    x="month-year",
    y="HT",
    color_discrete_sequence=["#0083B8"] * len(df_export),
    template="plotly_white",
    category_orders={"month-year": month_year_list},
    labels={"month-year": "Date", "HT": "Total Sales"}
)

fig_export_sales.update_layout(
    title="<b>Export Sales per Month and Year</b>",
    width=1200
)

# EXPORT SALES BY COMPANY [BAR CHART]
export_sales_by_company = (
    df_export_init.groupby(by=["Société"]).sum()[["HT"]].sort_values(by="HT")
)
# fig_export_company_sales = px.bar(
#     export_sales_by_company,
#     x="HT",
#     y=export_sales_by_company.index,
#     orientation="h",
#     title="<b>Export Sales by Company</b>",
#     color_discrete_sequence=["#0083B8"] * len(export_sales_by_company),
#     template="plotly_white",
# )

fig_export_company_sales = px.pie(
    export_sales_by_company,
    values= "HT",
    names= export_sales_by_company.index,
    title="<b>Export Sales by company</b>",
    color_discrete_sequence = ["#084594", "#2171b5", "#4292c6", "#6baed6", "#9ecae1", "#c6dbef"],
    template="plotly_white"
)

# fig_export_company_sales.update_layout(
#     xaxis_title="Total sales", 
#     yaxis_title="Company",
#     plot_bgcolor="rgba(0,0,0,0)",
#     xaxis=(dict(showgrid=False))
# )

# EXPORT SALES BY ACTIVITY [BAR CHART]
export_sales_by_activity = (
    df_export_init.groupby(by=["ACTIVITE"]).sum()[["HT"]].sort_values(by="HT")
)
fig_export_company_sales_activity = px.bar(
    export_sales_by_activity,
    x=export_sales_by_activity.index,
    y="HT",
    # orientation="h",
    title="<b>Export Sales by activity</b>",
    color_discrete_sequence=["#0083B8"] * len(export_sales_by_activity),
    template="plotly_white"
)

fig_export_company_sales_activity.update_layout(
    xaxis_title="Activity", 
    yaxis_title="Total sales",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(tickmode="linear"),
    yaxis=(dict(showgrid=False))
)

fig_export_company_sales_activity.update_xaxes(categoryorder="total descending")

#EXPORT SALES PER GAMME [PIE CHART]
export_sales_per_gamme = df_export_init.groupby(by=["Ligne prod."]).sum()[["HT"]]

top_5 = export_sales_per_gamme.sort_values("HT", ascending=False).iloc[:5]
others = export_sales_per_gamme.loc[~export_sales_per_gamme.index.isin(top_5.index)]
other_sum = others["HT"].sum()
threshold = other_sum * 0.1

top_5_names = top_5.index.tolist()
top_5_names.append("Other")

top_5_values = top_5["HT"].tolist()
if other_sum > threshold:
    top_5_values.append(other_sum)
else:
    top_5_names.pop()


fig_export_sales_per_gamme = px.pie(
    df_export_init, 
    values= top_5_values,
    names= top_5_names,
    title="<b>Export Sales per product line</b>",
    color_discrete_sequence = ["#084594", "#2171b5", "#4292c6", "#6baed6", "#9ecae1", "#c6dbef"],
    template="plotly_white"
)

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

with tab1:
    left_column, middle_column, right_column = st.columns(3)
    with left_column:
        st.subheader(":bar_chart: Total Sales:")
        st.subheader(f"{total_sales:,} TND")
    with middle_column:
        st.subheader(":bar_chart: Total quantity sold:")
        st.subheader(f"{total_quantity_sold} unit")
    with right_column:
        st.subheader(":bar_chart: Average Sales Per Transaction:")
        st.subheader(f"{average_sale_by_transaction} TND")
    st.markdown("""---""")

    left_column, right_column = st.columns(2)
    left_column.plotly_chart(fig_yearly_sales, use_container_width=True)
    right_column.plotly_chart(fig_company_sales, use_container_width=True)

    left_column, right_column = st.columns(2)
    left_column.plotly_chart(fig_sales_per_gamme, use_container_width=True)
    right_column.plotly_chart(fig_sales_per_market, use_container_width=True)


with tab2:
   st.plotly_chart(fig_local_sales)
   left_column, middle_column, right_column = st.columns(3)
   left_column.plotly_chart(fig_local_company_sales, use_container_width=True)
   middle_column.plotly_chart(fig_local_sales_per_gamme, use_container_width=True)
   right_column.plotly_chart(fig_sales_per_city, use_container_width=True)

with tab3:
   st.plotly_chart(fig_export_sales)
   left_column, middle_column, right_column = st.columns(3)
   left_column.plotly_chart(fig_export_company_sales, use_container_width=True)
   middle_column.plotly_chart(fig_export_company_sales_activity, use_container_width=True)
   right_column.plotly_chart(fig_export_sales_per_gamme, use_container_width=True)
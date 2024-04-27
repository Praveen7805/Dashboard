import streamlit as st
import plotly.express as px
import matplotlib
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
st.set_page_config(page_title="Sales Dashboard",page_icon=":bar_chart",layout="wide")
st.title(":bar_chart: Sales Analysis in Dashboard")
st.markdown('<style>div.block-container{padding-top:1rem;</style>' , unsafe_allow_html=True)

file = st.file_uploader(":file_folder: Upload files" , type = ['txt','csv','xls','xlsx'])

if file is not None:
    filename = file.name
    df = pd.read_csv(filename,encoding = "ISO-8859-1")
    st.write(filename)
else:
    filename = "https://github.com/Praveen7805/Dashboard/blob/main/Superstore.csv"
    df = pd.read_csv(filename,encoding = "ISO-8859-1")
    st.write(filename)

col1 , col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

#min and max

start_Date = pd.to_datetime(df["Order Date"]).min()
end_Date = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Star date",start_Date))
with col2:
    date2 = pd.to_datetime(st.date_input("Star date", end_Date))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

#Region

st.sidebar.header("Choose your filter :")
region = st.sidebar.multiselect("Pick your region",df["Region"].unique())

if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

#State

state = st.sidebar.multiselect("Pick your state" , df2["State"].unique())

if not state:
    df3 = df.copy()
else:
    df3 = df2[df2["State"].isin(state)]

# city
city = st.sidebar.multiselect("Pick your city", df3["City"].unique())

if not region and not state and not city : fdf = df
elif not state and not city : fdf = df[df["Region"].isin(region)]
elif not region and not city : fdf = df[df["State"].isin(state)]
elif state and city: fdf = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city: fdf = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif state and region: fdf = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city : fdf = df3[df3["City"].isin(city)]
else:fdf = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]


category_df = fdf.groupby(by = ["Category"] , as_index = False)["Sales"].sum()
with col1:
    st.subheader("Category Wise Sales")
    fig = px.bar(category_df,x = "Category" , y = "Sales" , text = ['${:,.2f}'.format(x) for x in category_df["Sales"]] , template = "seaborn")
    st.plotly_chart(fig,use_container_width=True,height = 200)
with col2:
    st.subheader("Region Wise Sales")
    fig = px.pie(fdf , values = "Sales" , names = "Region" , hole = 0.5)
    fig.update_traces(text = fdf["Region"] , textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

c1 , c2 = st.columns(2)
with c1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap = "Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data",data = csv , file_name="Category.csv" , mime="text/csv" , help="Click here to download the data as csv file")
with c2:
    with st.expander("Region_ViewData"):
        region = fdf.groupby(by=["Region"], as_index=False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap = "Oranges"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data",data = csv , file_name="Region.csv" , mime="text/csv" , help="Click here to download the data as csv file")


fdf["month_year"] = fdf["Order Date"].dt.to_period("M")
st.subheader("Time Series Analysis")
linechart = pd.DataFrame(fdf.groupby(fdf["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart,x = "month_year" , y = "Sales" , labels={"Sales" : "Amount"} , height = 500 , width = 1000, template = "gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data of Time Series"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv")

# tree on region , category and subcategory

st.subheader("Hierarchial view of Sales using TreeMap")
fig3 = px.treemap(fdf,path = ["Region","Category","Sub-Category"] , hover_data=["Sales"] ,color="Sub-Category")
fig3.update_layout(width = 800,height = 650)
st.plotly_chart(fig3,use_container_width=True)

chart1 , chart2 = st.columns((2))
with chart1:
    st.subheader("Segment wise sales")
    fig = px.pie(fdf,values="Sales" , names = "Segment" , template="plotly_dark")
    fig.update_traces(text = fdf["Segment"] , textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)
with chart2:
    st.subheader("Category wise sales")
    fig = px.pie(fdf,values="Sales" , names = "Category" , template="gridon")
    fig.update_traces(text = fdf["Category"] , textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region","State","City","Category","Sales","Profit","Quantity"]]
    fig = ff.create_table(df_sample, colorscale = "Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise sub-Category Table")
    fdf["month"] = fdf["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data = fdf, values = "Sales", index = ["Sub-Category"],columns = "month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

# Create a scatter plot
data1 = px.scatter(fdf, x = "Sales", y = "Profit", size = "Quantity")
data1['layout'].update(title="Relationship between Sales and Profits using Scatter Plot.",
                       titlefont = dict(size=20),xaxis = dict(title="Sales",titlefont=dict(size=19)),
                       yaxis = dict(title = "Profit", titlefont = dict(size=19)))
st.plotly_chart(data1,use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))

# Download orginal DataSet
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")


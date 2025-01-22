
import pandas    as pd
import datetime 
from PIL import Image
import plotly.express as px  
import streamlit as st
import plotly.graph_objects as go
import streamlit.components.v1 as components


# Restaurant
html_title = """
<style>
    .title_test {
        font-weight: bold;
        padding: 5px;
        border-radius: 6px;
        margin-top: 30px; 
        text-align: center;
    }
</style>
<center><h1 class="title_test">Restaurant</h1></center>
"""
st.markdown(html_title, unsafe_allow_html=True)

st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
fl=st.file_uploader(":file_folder: Upload a file", type=(["csv","txt", "xlsx", "xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
else:
    df=pd.read_csv('test_data.csv')


#update
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)  # Use dayfirst=True if dates are in DD/MM/YYYY format

# Get the min and max dates 
startDate = df["Date"].min()
endDate = df["Date"].max()

col1, col2 = st.columns((2))

# Input start and end dates
with col1:
    date1 = st.date_input("Start Date", value=startDate)  
    date1 = pd.to_datetime(date1)  

with col2:
    date2 = st.date_input("End Date", value=endDate) 
    date2 = pd.to_datetime(date2)  

filtered_df = df[(df["Date"] >= date1) & (df["Date"] <= date2)].copy()

st.markdown("""
    <style>
        .sales-box {
            border: 2px solid #4CAF50;
            border-radius: 10px;
            padding: 15px;
            background-color: #f9f9f9;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin: 10px;
        }
        .highlight {
            color: #4CAF50;
        }
    </style>
""", unsafe_allow_html=True)

col1,col2,col3 =st.columns([0.4,0.3,0.3])
#  total
with col1:
    total_sales = filtered_df['Price'].sum()
    # 
    st.markdown(f"""
        <div class="sales-box">
            Total Sales: <br> <span style="color:#4CAF50;">${total_sales:,.2f}</span>
        </div>
    """, unsafe_allow_html=True)

with col2:
    food_sales = filtered_df[filtered_df['Category'] == 'food']['Price'].sum()
    st.markdown(f"""
    <div class="sales-box">
        Food Sales: <br> <span class="highlight">${food_sales:,.2f}</span>
    </div>
""", unsafe_allow_html=True)
with col3:
    drink_sales = filtered_df[filtered_df['Category'] == 'drink']['Price'].sum()
    st.markdown(f"""
    <div class="sales-box">
        Drink Sales: <br> <span class="highlight">${drink_sales:,.2f}</span>
    </div>
""", unsafe_allow_html=True)

st.sidebar.header("Choose your filters: ")

#Day of week 
day=st.sidebar.multiselect("Pick your Day of Week",df["Day Of Week"].unique())
if not day:
    df2=df.copy()
else:
    df2=df[df["Day Of Week"].isin(day)]

#Category
Category=st.sidebar.multiselect("Pick your Category",df2["Category"].unique())
if not Category:
    df3=df2.copy()
else:
    df3=df2[df2["Category"].isin(Category)]

#Menu
Menu=st.sidebar.multiselect("Pick your Menu",df3["Menu"].unique())

if not day and not Category  and not Menu:
    filtered_df=df
elif not Menu and not Category:
    filtered_df=df[df["Day Of Week"].isin(day)]
elif not day  and not Menu:
    filtered_df=df[df["Category"].isin(Category)]
elif Menu and  Category:
    filtered_df=df3[df3["Menu"].isin(Menu)&df["Category"].isin(Category)]
elif day and  Category:
    filtered_df=df3[df3["Category"].isin(Category)&df["Day Of Week"].isin(day )]
elif Menu and  day:
    filtered_df=df3[df3["Menu"].isin(Menu)&df["Day Of Week"].isin(day )]
elif Menu:
    filtered_df=df3["Menu"].isin(Menu)
else:
    filtered_df=df3[df3["Menu"].isin(Menu)&df3["Day Of Week"].isin(day )&df3["Category"].isin(Category)]


daily_sales= filtered_df.groupby(by=['Day Of Week'],as_index=False)['Price'].sum()



#  Daily  and   Category
col4,col5=st.columns([0.5,0.5])
with col4:
    st.subheader('Daily sales')
    fig=px.bar(daily_sales, x='Day Of Week',y="Price",text=[f"${x:,.2f}" for x in daily_sales["Price"]],
        template='seaborn')
    st.plotly_chart(fig,use_container_width=True,height=200)

Category_sale= filtered_df.groupby(by=['Category'],as_index=False)['Price'].sum()
with col5:
    st.subheader('Category with Sale')
    fig = px.pie(Category_sale, values='Price', names='Category', hole=0.5)
    fig.update_traces( text=Category_sale["Category"],  textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


# TS
filtered_df["month_year"] = filtered_df["Date"].dt.to_period("M")
st.subheader('Time Series Analysis')
linechart= pd.DataFrame (filtered_df.groupby (filtered_df ["month_year"].dt.strftime("%Y: %b")) ["Price"].sum()).reset_index()
fig2= px.line (linechart, x = "month_year", y="Price", labels = {"Sales": "Amount"}, height=500, width=1000, template="gridon")
st.plotly_chart (fig2, use_container_width=True)

#Frequently Ordered Menu
menu_frequency = filtered_df['Menu'].value_counts().reset_index()
menu_frequency.columns = ['Menu', 'count']
st.subheader("Frequently Ordered Menu Items")
fig3 = px.treemap(menu_frequency, 
                  path=["Menu"], 
                  values="count", 
                  hover_data=["count"], 
                  color="count",  
                  color_continuous_scale="Viridis") 
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

#staff
staff_data = df.groupby('Hour')[['Kitchen Staff', 'Drinks Staff']].sum().reset_index()
fig = px.bar(staff_data, x='Hour', y=['Kitchen Staff', 'Drinks Staff'], barmode='group', title="Kitchen Staff vs Drinks Staff by Hour", labels={'Hour': 'Hour', 'value': 'Staff Count'})
fig.update_layout(width=800, height=600)
st.plotly_chart(fig)





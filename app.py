import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import datetime
import os

#Streamlit Config
st.set_page_config(page_title='Dashboard',
                   page_icon=':bar_chart:',
                   layout='wide',
                   initial_sidebar_state="collapsed"
                   ) 
st.header(":bar_chart: Recruitment Dashboard")

#Upload excel File
@st.cache_data
def load_data(file):
    df_data = pd.read_csv(file)
    return df_data
df_data = st.file_uploader('')
if df_data is None:
    st.stop()
df_data = load_data(df_data)

# df_data = pd.read_csv('Candidate_Sample_Set.csv')

#Month Filter
col1, col2 = st.columns((2))
try:
    df_data["Application_Date"] = pd.to_datetime(df_data["Application_Date"])

        # Getting the min and max date 
    startDate = pd.to_datetime(df_data["Application_Date"]).min()
    endDate = pd.to_datetime(df_data["Application_Date"]).max()

    with col1:
        date1 = pd.to_datetime(st.date_input("Start Date", startDate))

    with col2:
        date2 = pd.to_datetime(st.date_input("End Date", endDate))

    df_data = df_data[(df_data["Application_Date"] >= date1) & (df_data["Application_Date"] <= date2)]
except:
    st.write('⚠️ Create Application_Date column to get a data filter')
#Sidebar Filters
st.sidebar.header('Filter Here:')
try:
    language = st.sidebar.multiselect(
        "Language",
        options=df_data['Language'].unique(),
        default=df_data['Language'].unique()
    )
except:
    st.sidebar.write('⚠️ Language - Create column to get the filter')

try:
    location = st.sidebar.multiselect(
        "Location",
        options=df_data['Location'].unique(),
        default=df_data['Location'].unique(),
    )
except:
    st.sidebar.write('⚠️ Location - Create column to get the filter')

try:
    gender = st.sidebar.multiselect(
        "Gender",
        options=df_data['Gender'].unique(),
        default=df_data['Gender'].unique()
    )
except:
    st.sidebar.write('⚠️ Gender - Create column to get the filter')
# recruitment_stages = st.sidebar.multiselect(
#     "Recruitment Stages",
#     options=df_data['Recruitment_Stages'].unique(),
#     default=df_data['Recruitment_Stages'].unique()
# )
# source = st.sidebar.multiselect(
#     "Source",
#     options=df_data['Source'].unique(),
#     default=df_data['Source'].unique()
# )
# status = st.sidebar.multiselect(
#     "Status",
#     options=df_data['Status'].unique(),
#     default=df_data['Status'].unique()
# )
try:
    company = st.sidebar.multiselect(
        "Company",
        options=df_data['Company'].unique(),
        default=df_data['Company'].unique()
    )
except:
    st.sidebar.write('⚠️ Company - Create column to get the filter')

try:
    df_selection = df_data.query(
        "Language == @language & Location == @location & Gender == @gender & Company == @company" #Can add "Recruitment_Stages","Status" and "Source"
    )
except:
    df_selection = df_data

st.sidebar.markdown("Developed by [GitHub](https://github.com/srdobolo), [LinkedIn](https://www.linkedin.com/in/joaomiguellima/)")

#TOP KPI'S
#Hired
try:
    hired = df_selection['Recruitment_Stages'].value_counts()['Hired']
except:
    hired = 0

#Applications Per Hire
try:    
    apps_per_hire = len(df_selection)/df_selection['Recruitment_Stages'].value_counts()['Hired']
except:
    apps_per_hire = 0

#Days to Hire
try:
    df_days_to_hire = df_selection.loc[df_selection['Recruitment_Stages'] == 'Hired']
    df_days_to_hire[['Application_Date','Hiring_Date']] = df_days_to_hire[['Application_Date','Hiring_Date']].apply(pd.to_datetime)
    df_days_to_hire['Days_To_Hire'] = (df_days_to_hire['Hiring_Date'] - df_days_to_hire['Application_Date']).dt.days
    days_to_hire = df_days_to_hire['Days_To_Hire'].mean()
    days_to_hire = days_to_hire.round()
except:
    days_to_hire = 0

#Success Rate
try:    
    success_rate = df_selection['Status'].value_counts()['Placement']/df_selection['Recruitment_Stages'].value_counts()['Hired']*100
except:
    success_rate = 0

first_column, second_column, third_column, fourth_column = st.columns (4)
with first_column:
    fig1 = go.Figure(
        go.Indicator(
            domain = {'x': [0, 1],'y': [0, 1]},
            value = hired,
            mode = "gauge+number", #"gauge+number+delta"
            title = {'text': "Hired"},
            delta = {'reference': 0},
            gauge = {'axis': {'range': [None, hired*apps_per_hire/2.5]}}
        )
    )
    fig1.update_layout(
        height=200,
        margin=dict(
            l=10,
            r=10,
            t=50,
            b=10,
            pad=8
        )
    )
    st.plotly_chart(fig1, use_container_width=True)

with second_column:
    fig2 = go.Figure(
        go.Indicator(
            domain = {'x': [0, 1], 'y': [0, 1]},
            value = success_rate,
            number = {'suffix': " %"},
            mode = "gauge+number", #"gauge+number+delta"
            title = {'text': "Success Rate"},
            delta = {'reference': 0},
            gauge = {'axis': {'range': [ 0, 100 ]}}
        )
    )
    fig2.update_layout(
        height=200,
        margin=dict(
            l=10,
            r=10,
            t=50,
            b=10,
            pad=8
        )   
    )
    st.plotly_chart(fig2, use_container_width=True)

with third_column:
    fig3 = go.Figure(
        go.Indicator(
            domain = {'x': [0, 1], 'y': [0, 1]},
            value = apps_per_hire,
            mode = "gauge+number", #"gauge+number+delta"
            title = {'text': "Applications per Hire"},
            delta = {'reference': 0},
            gauge = {'axis': {'range': [apps_per_hire*2, 0 ]}}
        )
    )
    fig3.update_layout(
        height=200,
        margin=dict(
            l=10,
            r=10,
            t=50,
            b=10,
            pad=8
        )
    )
    st.plotly_chart(fig3, use_container_width=True)

with fourth_column:
    fig4 = go.Figure(
        go.Indicator(
            domain = {'x': [0, 1], 'y': [0, 1]},
            value = days_to_hire,
            mode = "gauge+number", #"gauge+number+delta"
            title = {'text': "Days to Hire"},
            delta = {'reference': 0},
            gauge = {'axis': {'range': [days_to_hire*2 , 0 ]}}
        )
    )
    fig4.update_layout(
        height=200,
        margin=dict(
            l=10,
            r=10,
            t=50,
            b=10,
            pad=8
        )
    )
    st.plotly_chart(fig4, use_container_width=True)

col1, col2, col3 = st.columns(3)

#Recruitment Funnel
with col1:
    st.subheader('Recruitment Funnel')
    try:
        df_recruitment_funnel_index=['Hired',
                                     'Offer',
                                     'Interview',
                                     'Harver Test',
                                     'Phone Screening',
                                     'Applied']
        df_recruitment_funnel = pd.DataFrame(
            df_selection['Recruitment_Stages'].value_counts(),
            index=df_recruitment_funnel_index
        )
    
        df_recruitment_funnel=df_recruitment_funnel.cumsum()
        df_recruitment_funnel=df_recruitment_funnel.sort_values(by='Recruitment_Stages',ascending=False)

        recruitment_funnel = go.Figure(
            go.Funnel(
                y = df_recruitment_funnel.index,
                x = df_recruitment_funnel['Recruitment_Stages'],  
                textposition = "inside",
                textinfo = "percent initial"
            )    
        )
        recruitment_funnel.update_layout(
            showlegend=False,
            yaxis_title=None,
        )
        st.plotly_chart(recruitment_funnel, use_container_width=True)
    except:
        st.write('⚠️ Create Recruitment_Stages column to get this chart')

#Stages Pipeline Pie
with col2:
    st.subheader('Recruitment Stages Pipeline')
    try:
        df_stages_pipeline = pd.DataFrame(
            df_selection[['Application_Date',
                        'Phone_Screen_Date',
                        'Harver_Test_Date',
                        'Interview_Date',
                        'Offer_Date',
                        'Hiring_Date']]
        ).apply(pd.to_datetime)

        df_recruitment_stages = pd.DataFrame(
            df_selection[['Recruitment_Stages']]
        )

        df_stages_pipeline = pd.concat([df_recruitment_stages, df_stages_pipeline], axis=1)
        df_stages_pipeline = df_stages_pipeline.fillna(axis=1, method='ffill')
        df_stages_pipeline['Phone Screen'] = df_stages_pipeline['Phone_Screen_Date'] - df_stages_pipeline['Application_Date']
        df_stages_pipeline['HarverTest'] = df_stages_pipeline['Harver_Test_Date'] - df_stages_pipeline['Phone_Screen_Date']
        df_stages_pipeline['Interview'] = df_stages_pipeline['Interview_Date'] - df_stages_pipeline['Harver_Test_Date']
        df_stages_pipeline['Offer'] = df_stages_pipeline['Offer_Date'] - df_stages_pipeline['Interview_Date']
        df_stages_pipeline['Hire'] = df_stages_pipeline['Hiring_Date'] - df_stages_pipeline['Offer_Date']
        df_stages_pipeline.replace('0 days', np.nan, inplace=True)
        df_stages_pipeline = df_stages_pipeline.mean()
        df_stages_pipeline = df_stages_pipeline / np.timedelta64(1, 'D')
        df_stages_pipeline = df_stages_pipeline.round()
        
        stages_pipeline_pie = go.Figure(
            data=[
                go.Pie(
                    labels=['Phone Screen',
                            'HarverTest',
                            'Interview',
                            'Offer',
                            'Hire',
                            'Payment'],
                    values=df_stages_pipeline,
                    hole = 0.5
                    )
                ]
            )
        stages_pipeline_pie.update_layout(
            legend=dict(
                yanchor="bottom",
                y=0.01,
                xanchor="left",
                x=0.01,
                #number = {'suffix': 'Days'}
            ),
            
        )
        stages_pipeline_pie.update_traces(
            hoverinfo='label+percent',
            textinfo='value',
            textfont_size=15,
        )                        
        st.plotly_chart(stages_pipeline_pie, use_container_width=True)
    except:
        st.write('⚠️ Create Recruitment_Stages date columns to get this chart')                                                    
#Source Pie
with col3:
    st.subheader('Source')
    try:
        source_pie = go.Figure(
            data=[
                go.Pie(
                    labels=df_selection['Source'].unique(),
                    values=df_selection['Source'].value_counts(),
                )
            ]
        )
        source_pie.update_layout(
            legend=dict(
                yanchor="bottom",
                y=0.01,
                xanchor="left",
                x=0.01,
            )
        )
        source_pie.update_traces(
            hoverinfo='label+value',
        )                        
        st.plotly_chart(source_pie, use_container_width=True)
    except:
        st.write('⚠️ Create Source column to get this chart')               

col4, col5 = st.columns([2, 1])
#Sources Performance
with col4:
    st.subheader('Source Performance')
    try:
        df_source = pd.DataFrame(
            df_selection[['Source','Recruitment_Stages']]
        )

            #% Applied
        df_applied = pd.DataFrame(
            df_source['Source'].value_counts().to_frame('# Applied')
        )
        df_applied = df_applied.reset_index()
        df_applied['% Of Applications'] = df_applied['# Applied']/df_applied['# Applied'].sum()*100

            #% Hired
        df_hired = pd.DataFrame(
            df_source[df_source['Recruitment_Stages'] == 'Hired'].value_counts().to_frame('# Hired')
        )
        df_hired = df_hired.reset_index()

            #Source Performance
        df_source_performance = pd.concat([df_applied, df_hired], axis=1)
        df_source_performance.drop('Recruitment_Stages', axis='columns', inplace=True)
        df_source_performance.drop('Source', axis='columns', inplace=True)
        df_source_performance['% Of Hired'] = df_source_performance['# Hired']/df_source_performance['# Hired'].sum()*100 
        df_source_performance['% Of Conversion Rate'] = df_source_performance['# Hired']/df_source_performance['# Applied']*100 
        df_source_performance = df_source_performance.replace('',np.nan).fillna(0)
        df_source_performance.reset_index(drop=True, inplace=True)
        df_source_performance.rename(columns={"index": "Source"}, inplace=True)

        df_source_performance = st.dataframe(
            df_source_performance,
            column_config={
                "% Of Applications": st.column_config.ProgressColumn(
                    "% Of Applications",
                    help="% Of Applications Received",
                    format="%.2f", # corrigir simbolo %
                    min_value=0,
                    max_value=100,
                ),
                "% Of Hired": st.column_config.ProgressColumn(
                    "% Of Hired",
                    help="% Of Hired From Total Hires",
                    format="%.2f", # corrigir simbolo %
                    min_value=0,
                    max_value=100,
                ),
                "% Of Conversion Rate": st.column_config.ProgressColumn(
                    "% Of Conversion Rate",
                    help="% Of Hired From Each Source",
                    format="%.2f", # corrigir simbolo %
                    min_value=0,
                    max_value=100,
                ),
            },
            hide_index=True,
            use_container_width=True
        )
    except:
        st.write('⚠️ Create Source and Recruitment_Stages column to get this table') 

#Decline Reasons
with col5:
    st.subheader('Decline Reasons')
    try:
        df_decline_reasons = pd.DataFrame(
            df_selection[['Status','Decline_Reasons']]
        )
        df_decline_reasons = df_decline_reasons.loc[df_decline_reasons['Status'] == 'Rejected']

        # #Of Applications
        df_applications = pd.DataFrame(
            df_decline_reasons['Decline_Reasons'].value_counts().to_frame('# Of Applications')
        )
        df_applications['% Of Applications'] = (df_applications['# Of Applications']/df_applications['# Of Applications'].sum())*100

        df_decline_reasons = st.dataframe(
            df_applications,
            column_config={
                "% Of Applications": st.column_config.ProgressColumn(
                    "% Of Applications",
                    help="% Of Applications",
                    format="%.2f", # corrigir simbolo %
                    min_value=0,
                    max_value=100,
                )
            },
            hide_index=False,
            use_container_width=True
        )
    except:
        st.write('⚠️ Create Status and Decline_Reasons column to get this table') 

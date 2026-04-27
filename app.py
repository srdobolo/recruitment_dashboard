import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import datetime
import os
import sys

# 添加项目根目录到路径，以便导入 utils 模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 从共享模块导入统一的数据清洗函数
from utils.data_cleaner import clean_data

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
    df_data = clean_data(df_data)
    return df_data

df_data = st.file_uploader('')
if df_data is None:
    st.stop()
df_data = load_data(df_data)

# df_data = pd.read_csv('Candidate_Sample_Set.csv')

# 检查是否有日期列进行时间对比
has_application_date = 'Application_Date' in df_data.columns and not df_data['Application_Date'].isna().all()

# 侧边栏：对比区间选择
st.sidebar.header('📊 Time Period Comparison')

if has_application_date:
    enable_comparison = st.sidebar.checkbox('Enable Period Comparison', value=False)
    
    if enable_comparison:
        st.sidebar.subheader('Base Period (A)')
        try:
            base_start_date = pd.to_datetime(df_data["Application_Date"]).min()
            base_end_date = pd.to_datetime(df_data["Application_Date"]).max()
            
            base_start = st.sidebar.date_input("Start Date (A)", base_start_date)
            base_end = st.sidebar.date_input("End Date (A)", base_end_date)
            
            base_start = pd.to_datetime(base_start)
            base_end = pd.to_datetime(base_end)
        except:
            st.sidebar.write('⚠️ Unable to parse dates')
            base_start = None
            base_end = None
        
        st.sidebar.subheader('Comparison Period (B)')
        try:
            # 默认选择前一个时间段（比如前一个月）
            if base_start and base_end:
                period_days = (base_end - base_start).days
                comp_end_date = base_start - pd.Timedelta(days=1)
                comp_start_date = comp_end_date - pd.Timedelta(days=period_days)
                
                # 确保比较时间段不早于数据的最早日期
                min_date = pd.to_datetime(df_data["Application_Date"]).min()
                if comp_start_date < min_date:
                    comp_start_date = min_date
                
                comp_start = st.sidebar.date_input("Start Date (B)", comp_start_date)
                comp_end = st.sidebar.date_input("End Date (B)", comp_end_date)
            else:
                comp_start = st.sidebar.date_input("Start Date (B)")
                comp_end = st.sidebar.date_input("End Date (B)")
            
            comp_start = pd.to_datetime(comp_start)
            comp_end = pd.to_datetime(comp_end)
        except:
            st.sidebar.write('⚠️ Unable to parse dates')
            comp_start = None
            comp_end = None
else:
    enable_comparison = False
    st.sidebar.write('⚠️ Add Application_Date column for period comparison')

#Month Filter - 主时间段
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

    df_filtered = df_data[(df_data["Application_Date"] >= date1) & (df_data["Application_Date"] <= date2)]
except:
    st.write('⚠️ Create Application_Date column to get a data filter')
    df_filtered = df_data

#Sidebar Filters
st.sidebar.header('Filter Here:')
try:
    language = st.sidebar.multiselect(
        "Language",
        options=df_filtered['Language'].unique(),
        default=df_filtered['Language'].unique()
    )
except:
    st.sidebar.write('⚠️ Language - Create column to get the filter')
    language = []

try:
    location = st.sidebar.multiselect(
        "Location",
        options=df_filtered['Location'].unique(),
        default=df_filtered['Location'].unique(),
    )
except:
    st.sidebar.write('⚠️ Location - Create column to get the filter')
    location = []

try:
    gender = st.sidebar.multiselect(
        "Gender",
        options=df_filtered['Gender'].unique(),
        default=df_filtered['Gender'].unique()
    )
except:
    st.sidebar.write('⚠️ Gender - Create column to get the filter')
    gender = []

# recruitment_stages = st.sidebar.multiselect(
#     "Recruitment Stages",
#     options=df_filtered['Recruitment_Stages'].unique(),
#     default=df_filtered['Recruitment_Stages'].unique()
# )
# source = st.sidebar.multiselect(
#     "Source",
#     options=df_filtered['Source'].unique(),
#     default=df_filtered['Source'].unique()
# )
# status = st.sidebar.multiselect(
#     "Status",
#     options=df_filtered['Status'].unique(),
#     default=df_filtered['Status'].unique()
# )
try:
    company = st.sidebar.multiselect(
        "Company",
        options=df_filtered['Company'].unique(),
        default=df_filtered['Company'].unique()
    )
except:
    st.sidebar.write('⚠️ Company - Create column to get the filter')
    company = []

try:
    df_selection = df_filtered.query(
        "Language == @language & Location == @location & Gender == @gender & Company == @company" #Can add "Recruitment_Stages","Status" and "Source"
    )
except:
    df_selection = df_filtered

st.sidebar.markdown("Developed by [GitHub](https://github.com/srdobolo), [LinkedIn](https://www.linkedin.com/in/joaomiguellima/)")

# 招聘漏斗计算函数
def calculate_funnel_metrics(df):
    """
    计算招聘漏斗各阶段的数量和转化率
    阶段: Applied -> Phone Screening -> Harver Test -> Interview -> Offer -> Hired
    转化率关注: 
    - 申请到面试 (Applied -> Interview)
    - 面试到Offer (Interview -> Offer)
    - Offer到入职 (Offer -> Hired)
    - 整体转化率 (Applied -> Hired)
    """
    metrics = {}
    
    if 'Recruitment_Stages' not in df.columns:
        return metrics
    
    stage_counts = df['Recruitment_Stages'].value_counts()
    
    # 定义漏斗阶段顺序（从最早到最晚）
    funnel_stages = ['Applied', 'Phone Screening', 'Harver Test', 'Interview', 'Offer', 'Hired']
    
    # 确保所有阶段都有计数，没有则为0
    for stage in funnel_stages:
        metrics[stage] = int(stage_counts.get(stage, 0))
    
    # 计算转化率
    # 1. 申请到面试转化率: (Phone Screening + Harver Test + Interview + Offer + Hired) / Applied
    # 或者更简单: 实际进入面试阶段的人数 / 申请人数
    # 这里我们使用: Interview阶段及以上的人数 / Applied
    interview_plus = metrics.get('Interview', 0) + metrics.get('Offer', 0) + metrics.get('Hired', 0)
    total_applied = metrics.get('Applied', 0)
    
    if total_applied > 0:
        metrics['app_to_interview_rate'] = round(interview_plus / total_applied * 100, 2)
    else:
        metrics['app_to_interview_rate'] = 0
    
    # 2. 面试到Offer转化率: (Offer + Hired) / (Interview + Offer + Hired)
    interview_stage_total = interview_plus
    offer_plus = metrics.get('Offer', 0) + metrics.get('Hired', 0)
    
    if interview_stage_total > 0:
        metrics['interview_to_offer_rate'] = round(offer_plus / interview_stage_total * 100, 2)
    else:
        metrics['interview_to_offer_rate'] = 0
    
    # 3. Offer到入职转化率: Hired / (Offer + Hired)
    if offer_plus > 0:
        metrics['offer_to_hire_rate'] = round(metrics.get('Hired', 0) / offer_plus * 100, 2)
    else:
        metrics['offer_to_hire_rate'] = 0
    
    # 4. 整体转化率: Hired / Applied
    if total_applied > 0:
        metrics['overall_conversion_rate'] = round(metrics.get('Hired', 0) / total_applied * 100, 2)
    else:
        metrics['overall_conversion_rate'] = 0
    
    return metrics

# 时间段对比分析
if enable_comparison and has_application_date and base_start is not None:
    st.header('📊 Period Comparison Analysis')
    
    # 获取两个时间段的数据
    try:
        # 基础时间段数据
        df_base = df_data[(df_data["Application_Date"] >= base_start) & 
                          (df_data["Application_Date"] <= base_end)]
        
        # 应用筛选条件
        try:
            df_base = df_base.query(
                "Language == @language & Location == @location & Gender == @gender & Company == @company"
            )
        except:
            pass
        
        # 对比时间段数据
        df_comp = df_data[(df_data["Application_Date"] >= comp_start) & 
                          (df_data["Application_Date"] <= comp_end)]
        
        # 应用筛选条件
        try:
            df_comp = df_comp.query(
                "Language == @language & Location == @location & Gender == @gender & Company == @company"
            )
        except:
            pass
        
        # 计算两个时间段的漏斗指标
        base_metrics = calculate_funnel_metrics(df_base)
        comp_metrics = calculate_funnel_metrics(df_comp)
        
        if base_metrics and comp_metrics:
            # 显示两个时间段的基本信息
            st.subheader('Period Overview')
            col_period1, col_period2 = st.columns(2)
            
            with col_period1:
                st.metric(
                    label=f"Period A: {base_start.strftime('%Y-%m-%d')} to {base_end.strftime('%Y-%m-%d')}",
                    value=f"{len(df_base)} Applications",
                    delta=None
                )
            
            with col_period2:
                delta = len(df_base) - len(df_comp)
                st.metric(
                    label=f"Period B: {comp_start.strftime('%Y-%m-%d')} to {comp_end.strftime('%Y-%m-%d')}",
                    value=f"{len(df_comp)} Applications",
                    delta=f"{delta} vs Period A",
                    delta_color="normal" if delta >= 0 else "inverse"
                )
            
            # 显示转化率对比
            st.subheader('Conversion Rate Comparison')
            
            # 定义关键转化率指标
            conversion_metrics = [
                {'name': 'Application to Interview', 'key': 'app_to_interview_rate', 'label': 'App → Interview'},
                {'name': 'Interview to Offer', 'key': 'interview_to_offer_rate', 'label': 'Interview → Offer'},
                {'name': 'Offer to Hire', 'key': 'offer_to_hire_rate', 'label': 'Offer → Hire'},
                {'name': 'Overall Conversion', 'key': 'overall_conversion_rate', 'label': 'Overall'}
            ]
            
            # 创建4列显示各转化率
            cols = st.columns(4)
            
            for i, metric in enumerate(conversion_metrics):
                with cols[i]:
                    base_value = base_metrics.get(metric['key'], 0)
                    comp_value = comp_metrics.get(metric['key'], 0)
                    diff = base_value - comp_value
                    
                    st.metric(
                        label=metric['label'],
                        value=f"{base_value}% (A)",
                        delta=f"{diff:+.2f}% vs B",
                        delta_color="normal" if diff >= 0 else "inverse"
                    )
            
            # 显示详细的漏斗数据对比表
            st.subheader('Funnel Stage Details')
            
            funnel_stages = ['Applied', 'Phone Screening', 'Harver Test', 'Interview', 'Offer', 'Hired']
            
            comparison_data = {
                'Stage': [],
                'Period A (Count)': [],
                'Period B (Count)': [],
                'Difference': [],
                'Period A (%)': [],
                'Period B (%)': []
            }
            
            total_a = base_metrics.get('Applied', 0)
            total_b = comp_metrics.get('Applied', 0)
            
            for stage in funnel_stages:
                count_a = base_metrics.get(stage, 0)
                count_b = comp_metrics.get(stage, 0)
                diff = count_a - count_b
                
                comparison_data['Stage'].append(stage)
                comparison_data['Period A (Count)'].append(count_a)
                comparison_data['Period B (Count)'].append(count_b)
                comparison_data['Difference'].append(diff)
                comparison_data['Period A (%)'].append(round(count_a / total_a * 100, 2) if total_a > 0 else 0)
                comparison_data['Period B (%)'].append(round(count_b / total_b * 100, 2) if total_b > 0 else 0)
            
            df_comparison = pd.DataFrame(comparison_data)
            
            # 显示对比表格
            st.dataframe(
                df_comparison,
                column_config={
                    "Difference": st.column_config.NumberColumn(
                        "Difference (A-B)",
                        help="Count difference between Period A and Period B",
                        format="%d"
                    ),
                    "Period A (%)": st.column_config.ProgressColumn(
                        "Period A (%)",
                        help="Percentage of applicants in this stage for Period A",
                        format="%.2f%%",
                        min_value=0,
                        max_value=100,
                    ),
                    "Period B (%)": st.column_config.ProgressColumn(
                        "Period B (%)",
                        help="Percentage of applicants in this stage for Period B",
                        format="%.2f%%",
                        min_value=0,
                        max_value=100,
                    ),
                },
                hide_index=True,
                use_container_width=True
            )
            
            # 趋势图
            st.subheader('Conversion Rate Trends')
            
            # 准备图表数据
            chart_data = {
                'Conversion Type': [m['label'] for m in conversion_metrics],
                'Period A': [base_metrics.get(m['key'], 0) for m in conversion_metrics],
                'Period B': [comp_metrics.get(m['key'], 0) for m in conversion_metrics]
            }
            
            # 创建柱状对比图
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=chart_data['Conversion Type'],
                y=chart_data['Period A'],
                name=f'Period A ({base_start.strftime("%m/%d")}-{base_end.strftime("%m/%d")})',
                marker_color='#1f77b4'
            ))
            
            fig.add_trace(go.Bar(
                x=chart_data['Conversion Type'],
                y=chart_data['Period B'],
                name=f'Period B ({comp_start.strftime("%m/%d")}-{comp_end.strftime("%m/%d")})',
                marker_color='#ff7f0e'
            ))
            
            fig.update_layout(
                title='Conversion Rate Comparison by Period',
                xaxis_title='Conversion Stage',
                yaxis_title='Conversion Rate (%)',
                barmode='group',
                yaxis=dict(range=[0, 100]),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 漏斗图对比
            st.subheader('Funnel Chart Comparison')
            
            col_funnel1, col_funnel2 = st.columns(2)
            
            # 准备漏斗数据
            def prepare_funnel_data(metrics):
                stages = ['Applied', 'Phone Screening', 'Harver Test', 'Interview', 'Offer', 'Hired']
                values = [metrics.get(stage, 0) for stage in stages]
                # 移除值为0的阶段，但至少保留Applied和Hired
                filtered_stages = []
                filtered_values = []
                for s, v in zip(stages, values):
                    if v > 0 or s in ['Applied', 'Hired']:
                        filtered_stages.append(s)
                        filtered_values.append(v)
                return filtered_stages, filtered_values
            
            base_stages, base_values = prepare_funnel_data(base_metrics)
            comp_stages, comp_values = prepare_funnel_data(comp_metrics)
            
            with col_funnel1:
                st.markdown(f"**Period A: {base_start.strftime('%Y-%m-%d')} to {base_end.strftime('%Y-%m-%d')}**")
                
                if sum(base_values) > 0:
                    fig_funnel_a = go.Figure(go.Funnel(
                        y=base_stages,
                        x=base_values,
                        textposition="inside",
                        textinfo="value+percent initial",
                        marker={"color": "#1f77b4"}
                    ))
                    
                    fig_funnel_a.update_layout(
                        showlegend=False,
                        yaxis_title=None,
                        margin=dict(l=10, r=10, t=30, b=10)
                    )
                    
                    st.plotly_chart(fig_funnel_a, use_container_width=True)
                else:
                    st.write("No data for this period")
            
            with col_funnel2:
                st.markdown(f"**Period B: {comp_start.strftime('%Y-%m-%d')} to {comp_end.strftime('%Y-%m-%d')}**")
                
                if sum(comp_values) > 0:
                    fig_funnel_b = go.Figure(go.Funnel(
                        y=comp_stages,
                        x=comp_values,
                        textposition="inside",
                        textinfo="value+percent initial",
                        marker={"color": "#ff7f0e"}
                    ))
                    
                    fig_funnel_b.update_layout(
                        showlegend=False,
                        yaxis_title=None,
                        margin=dict(l=10, r=10, t=30, b=10)
                    )
                    
                    st.plotly_chart(fig_funnel_b, use_container_width=True)
                else:
                    st.write("No data for this period")
    except Exception as e:
        st.error(f"Error in period comparison: {e}")
        st.write("Please check your date selections and try again.")

# 分隔线
st.markdown("---")
st.header('📈 Current Period Dashboard')

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

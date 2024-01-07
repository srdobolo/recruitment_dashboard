import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import os

#Streamlit Config
st.set_page_config(page_title='Data View',
                   page_icon=':bar_chart:',
                   layout='wide',
                   initial_sidebar_state="collapsed"
                   )

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

#Data Cleaning
df_data = df_data.drop_duplicates()

# Data Editing
from typing import Any, Dict
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

def dataframe_explorer(df_data: pd.DataFrame, case: bool = False) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe
        case (bool, optional): If True, text inputs will be case sensitive. Defaults to True.

    Returns:
        pd.DataFrame: Filtered dataframe
    """

    random_key_base = pd.util.hash_pandas_object(df_data)

    df_data = df_data.copy()

    # Try to convert datetimes into standard format (datetime, no timezone)
    for col in df_data.columns:
        if is_object_dtype(df_data[col]):
            try:
                df_data[col] = pd.to_datetime(df_data[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df_data[col]):
            df_data[col] = df_data[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect(
            "Filter dataframe on",
            df_data.columns,
            key=f"{random_key_base}_multiselect",
        )
        filters: Dict[str, Any] = dict()
        for column in to_filter_columns:
            left, right = st.columns((1, 30))
            if is_categorical_dtype(df_data[column]) or df_data[column].nunique() < 30:
                left.write("↳")
                filters[column] = right.multiselect(
                    f"Values for {column}",
                    df_data[column].unique(),
                    default=list(df_data[column].unique()),
                    key=f"{random_key_base}_{column}",
                )
                df_data = df_data[df_data[column].isin(filters[column])]
            elif is_numeric_dtype(df_data[column]):
                left.write("↳")
                _min = float(df_data[column].min())
                _max = float(df_data[column].max())
                step = (_max - _min) / 100
                filters[column] = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                    key=f"{random_key_base}_{column}",
                )
                df_data = df_data[df_data[column].between(*filters[column])]
            elif is_datetime64_any_dtype(df_data[column]):
                left.write("↳")
                filters[column] = right.date_input(
                    f"Values for {column}",
                    value=(
                        df_data[column].min(),
                        df_data[column].max(),
                    ),
                    key=f"{random_key_base}_{column}",
                )
                if len(filters[column]) == 2:
                    filters[column] = tuple(map(pd.to_datetime, filters[column]))
                    start_date, end_date = filters[column]
                    df_data = df_data.loc[df_data[column].between(start_date, end_date)]
            else:
                left.write("↳")
                filters[column] = right.text_input(
                    f"Pattern in {column}",
                    key=f"{random_key_base}_{column}",
                )
                if filters[column]:
                    df_data = df_data[df_data[column].str.contains(filters[column], case=case)]
    select_column = st.multiselect(
        "Columns:",
        df_data.columns,
        default=['Fullname','Email','Phone_Number','Language','Company','Location','Recruitment_Stages','Status','Comments'])
    df_data = df_data[select_column]

    return df_data

#Dataframe
df_data = dataframe_explorer(df_data)

df_data = df_data.iloc[::-1]
df_data = st.data_editor(
    df_data,
    column_config={
        "Fullname": st.column_config.TextColumn(
            "Fullname",
            help="Type fullname as text",
            max_chars=50,
            required=True,
        ),
        "Email": st.column_config.TextColumn(
            "Email",
            help="Type email as text",
            max_chars=200,
            required=True,
        ),
        "Phone_Number": st.column_config.TextColumn(
            "Phone Number",
            help="Type phone number as XXX-XXX-XXX-XXX",
            max_chars=15,
            required=True,
        ),
        "Address": st.column_config.TextColumn(
            "Address",
            help="Type Address as text",
            max_chars=100,
            required=False,
        ),
        "DoB": st.column_config.DateColumn(       
            "DoB",
            help="select Date Of Birth",
        ),
        "Gender": st.column_config.SelectboxColumn(
            "Gender",
            width='small',
            help="Select Candidate Gender",
            options=[
                "F",
                "M",
                "Non-Binary",
            ],
            required=False,
        ),
        "Language": st.column_config.SelectboxColumn(
            "Language",
            width='small',
            help="Select Candidate Main Language",
            options=["NL",
                     "DE",
                     "FR",
                     "IT",
                     "CZ",
                     "HE",
                     "JA",
                     "PT",
                     "KO",
                     "SK",
                     "ES",
                     "ET",
                     "HU",
                     "PL",
                     "LT",
                     "RO",
                     "TR",
                     "NO",
                     "DA",
                     "SW",
                     "FI",
                     "LV",
                     "HR",
                     "RU",
                     "UK",
                     "AZ",
                     "IS",
                     "BG",
                     "EL",
                     "ZH",
                     "AR"
            ],
            required=False,
        ),
        "Recruitment_Stages": st.column_config.SelectboxColumn(
            "Recruitment Stages",
            help="Select Recruitment Stage Cadidate Is In",
            options=[
                "Interview",
                "Phone Screening",
                "Harver Test",
                "Offer",
                "Applied",
                "Hired"
            ],
            required=False,
        ),
        "Status": st.column_config.SelectboxColumn(
            "Status",
            width='small',
            help="Recruitment Process Status",
            options=[
                "On Hold",
                "Rejected",
                "Placement",
                "Credit Note",
                "Withdraw"
            ],
            required=False,
        ),
        "Decline_Reason": st.column_config.SelectboxColumn(
            "Decline Reason",
            width='small',
            help="If rejected or withdraw select decline reason",
            options=[
                "Behavior",
                "Technical",
                "Experience",
                "Language",
                "Motivation",
                "Profile",
                "Other"
            ],
            required=False,
        ),
    },
    hide_index=True,
    height=450,
    width=None,
    use_container_width=True,
    num_rows='dynamic',
    on_change=True
)

# Sidebar Form
# with st.sidebar.form(key='form', clear_on_submit=True):
#     fullname = st.text_input('Fullname',placeholder='Jane Doe') # required value @
#     email = st.text_input('Email', placeholder='jane.doe@gmail.com') # required value @
#     phone_number = st.text_input('Phone Number',placeholder='+123 987 654 321') # required value @
#     # address = st.text_input('Adress', placeholder='Street Name')
#     # dob = st.date_input('DoB', value=None)
#     # gender = st.selectbox("Gender",("M", "F", "Non-Binary"))

#     submit = st.form_submit_button(label='Submit')
#     if submit:
#         if not email or not phone_number:
#             st.warning('Ensure all fields are filled')
#             st.stop()
#         elif df_data['Email'].str.contains(email).any():
#             st.warning('A candidate with this email already exists')
#             st.stop()
#         elif df_data['Phone_Number'].str.contains(phone_number).any():
#             st.warning('A candidate with this phone number already exists')
#             st.stop()
#         else:
#             candidate_data = pd.DataFrame(
#                 [
#                     {
#                         "Fullname":fullname,
#                         "Email":email,
#                         "Phone_Number":phone_number
#                     }
#                 ]
#             )

#             # df_data = pd.concat([df_data, candidate_data], ignore_index=True)

st.sidebar.markdown("Developed by [GitHub](https://github.com/srdobolo), [LinkedIn](https://www.linkedin.com/in/joaomiguellima/)")

#Save Button
import io
# buffer to use for excel writer
buffer = io.BytesIO()

@st.cache_data
def convert_to_csv(df_data):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df_data.to_csv(index=False).encode('utf-8')
csv = convert_to_csv(df_data)

# download button 1 to download dataframe as csv
download1 = st.download_button(
    label="💾 Download as CSV",
    data=csv,
    file_name='st.Recuitment Dashboard.csv',
    mime='text/csv'
)

# # download button 2 to download dataframe as xlsx
# with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
#     # Write each dataframe to a different worksheet.
#     df_data.to_excel(writer, sheet_name='st.Recuitment Dashboard', index=False)

#     download2 = st.download_button(
#         label="💾 Download Excel",
#         data=buffer,
#         file_name='st.Recuitment Dashboard.csv.xlsx',
#         mime='application/vnd.ms-excel'
#     )

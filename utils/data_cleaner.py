import pandas as pd


def clean_data(df_data):
    """
    统一的数据清洗函数，用于招聘看板的所有页面。
    
    包含以下处理：
    1. 去除重复行
    2. 统一转换日期列格式
    3. 处理缺失值（使用 errors='coerce' 确保转换失败时设为 NaT）
    
    参数:
        df_data: 原始 pandas DataFrame
        
    返回:
        清洗后的 pandas DataFrame
    """
    # 去重
    df_data = df_data.drop_duplicates()
    
    # 尝试转换日期列
    date_columns = [
        'Application_Date', 
        'Phone_Screen_Date', 
        'Harver_Test_Date', 
        'Interview_Date', 
        'Offer_Date', 
        'Hiring_Date', 
        'DoB'
    ]
    
    for col in date_columns:
        if col in df_data.columns:
            try:
                df_data[col] = pd.to_datetime(df_data[col], errors='coerce')
            except Exception:
                pass
    
    return df_data

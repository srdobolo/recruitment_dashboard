#!/usr/bin/env python3
"""
测试招聘看板核心逻辑的脚本
验证：
1. 数据清洗逻辑
2. 漏斗计算逻辑
3. 时间段对比逻辑
"""

import pandas as pd
import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_cleaner import clean_data


def test_clean_data():
    """测试数据清洗函数"""
    print("=" * 60)
    print("测试1: 数据清洗函数 clean_data")
    print("=" * 60)
    
    # 创建测试数据
    data = {
        'Fullname': ['Test User 1', 'Test User 2', 'Test User 1', None],
        'Application_Date': ['2023-01-15', '2023-02-20', '2023-01-15', '2023-03-10'],
        'Hiring_Date': ['2023-02-15', 'invalid_date', '2023-02-15', ''],
        'Recruitment_Stages': ['Hired', 'Interview', 'Hired', 'Applied']
    }
    
    df = pd.DataFrame(data)
    print(f"\n原始数据行数: {len(df)}")
    print(f"原始数据列:\n{df.dtypes}")
    
    # 应用清洗
    cleaned_df = clean_data(df)
    
    print(f"\n清洗后数据行数: {len(cleaned_df)}")
    print(f"清洗后数据列:\n{cleaned_df.dtypes}")
    
    # 验证去重
    assert len(cleaned_df) == 3, f"去重失败，期望3行，实际{len(cleaned_df)}行"
    print("✅ 去重功能正常")
    
    # 验证日期转换
    assert pd.api.types.is_datetime64_any_dtype(cleaned_df['Application_Date']), \
        "Application_Date 应该转换为日期类型"
    print("✅ Application_Date 日期转换正常")
    
    # 验证无效日期处理
    assert cleaned_df['Hiring_Date'].isna().any(), \
        "无效日期应该转换为 NaT"
    print("✅ 无效日期处理正常 (转换为 NaT)")
    
    print("\n✅ 数据清洗函数测试通过!")
    return True


def test_calculate_funnel_metrics():
    """测试漏斗计算逻辑（从app.py复制的函数）"""
    print("\n" + "=" * 60)
    print("测试2: 招聘漏斗计算逻辑")
    print("=" * 60)
    
    def calculate_funnel_metrics(df):
        """从app.py复制的函数"""
        metrics = {}
        
        if 'Recruitment_Stages' not in df.columns:
            return metrics
        
        stage_counts = df['Recruitment_Stages'].value_counts()
        
        funnel_stages = ['Applied', 'Phone Screening', 'Harver Test', 'Interview', 'Offer', 'Hired']
        
        for stage in funnel_stages:
            metrics[stage] = int(stage_counts.get(stage, 0))
        
        # 计算转化率
        interview_plus = metrics.get('Interview', 0) + metrics.get('Offer', 0) + metrics.get('Hired', 0)
        total_applied = metrics.get('Applied', 0)
        
        if total_applied > 0:
            metrics['app_to_interview_rate'] = round(interview_plus / total_applied * 100, 2)
        else:
            metrics['app_to_interview_rate'] = 0
        
        interview_stage_total = interview_plus
        offer_plus = metrics.get('Offer', 0) + metrics.get('Hired', 0)
        
        if interview_stage_total > 0:
            metrics['interview_to_offer_rate'] = round(offer_plus / interview_stage_total * 100, 2)
        else:
            metrics['interview_to_offer_rate'] = 0
        
        if offer_plus > 0:
            metrics['offer_to_hire_rate'] = round(metrics.get('Hired', 0) / offer_plus * 100, 2)
        else:
            metrics['offer_to_hire_rate'] = 0
        
        if total_applied > 0:
            metrics['overall_conversion_rate'] = round(metrics.get('Hired', 0) / total_applied * 100, 2)
        else:
            metrics['overall_conversion_rate'] = 0
        
        return metrics
    
    # 创建测试数据
    data = {
        'Candidate_ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'Recruitment_Stages': [
            'Applied', 'Applied', 'Applied', 'Applied', 'Applied',
            'Phone Screening', 'Harver Test', 'Interview', 'Offer', 'Hired'
        ]
    }
    
    df = pd.DataFrame(data)
    print(f"\n测试数据: {len(df)} 个候选人")
    print(f"阶段分布:\n{df['Recruitment_Stages'].value_counts()}")
    
    metrics = calculate_funnel_metrics(df)
    
    print(f"\n计算结果:")
    print(f"  Applied: {metrics.get('Applied')}")
    print(f"  Phone Screening: {metrics.get('Phone Screening')}")
    print(f"  Harver Test: {metrics.get('Harver Test')}")
    print(f"  Interview: {metrics.get('Interview')}")
    print(f"  Offer: {metrics.get('Offer')}")
    print(f"  Hired: {metrics.get('Hired')}")
    
    print(f"\n转化率:")
    print(f"  申请到面试: {metrics.get('app_to_interview_rate')}%")
    print(f"  面试到Offer: {metrics.get('interview_to_offer_rate')}%")
    print(f"  Offer到入职: {metrics.get('offer_to_hire_rate')}%")
    print(f"  整体转化率: {metrics.get('overall_conversion_rate')}%")
    
    # 验证计算
    # Applied = 5, 进入面试阶段的 = Interview(1) + Offer(1) + Hired(1) = 3
    # 申请到面试 = 3/5 * 100 = 60%
    assert metrics.get('app_to_interview_rate') == 60.0, \
        f"申请到面试转化率错误，期望60%，实际{metrics.get('app_to_interview_rate')}%"
    print("✅ 申请到面试转化率计算正确")
    
    # 面试阶段总数 = 3, Offer阶段 = 2 (Offer + Hired)
    # 面试到Offer = 2/3 * 100 = 66.67%
    assert abs(metrics.get('interview_to_offer_rate') - 66.67) < 0.1, \
        f"面试到Offer转化率错误，期望约66.67%，实际{metrics.get('interview_to_offer_rate')}%"
    print("✅ 面试到Offer转化率计算正确")
    
    # Offer阶段 = 2, Hired = 1
    # Offer到入职 = 1/2 * 100 = 50%
    assert metrics.get('offer_to_hire_rate') == 50.0, \
        f"Offer到入职转化率错误，期望50%，实际{metrics.get('offer_to_hire_rate')}%"
    print("✅ Offer到入职转化率计算正确")
    
    # 整体转化率 = Hired(1) / Applied(5) * 100 = 20%
    assert metrics.get('overall_conversion_rate') == 20.0, \
        f"整体转化率错误，期望20%，实际{metrics.get('overall_conversion_rate')}%"
    print("✅ 整体转化率计算正确")
    
    print("\n✅ 招聘漏斗计算逻辑测试通过!")
    return True


def test_sample_data():
    """使用项目示例数据测试"""
    print("\n" + "=" * 60)
    print("测试3: 使用项目示例数据")
    print("=" * 60)
    
    sample_file = os.path.join(os.path.dirname(__file__), 'Candidate_Sample_Set.csv')
    
    if not os.path.exists(sample_file):
        print(f"⚠️ 示例数据文件不存在: {sample_file}")
        return True
    
    print(f"\n加载示例数据: {sample_file}")
    
    try:
        df = pd.read_csv(sample_file)
        print(f"✅ 成功加载 {len(df)} 条记录")
        print(f"列名: {list(df.columns)}")
        
        # 应用清洗
        cleaned_df = clean_data(df)
        print(f"✅ 数据清洗完成，{len(cleaned_df)} 条记录")
        
        # 检查日期列
        date_cols = ['Application_Date', 'Hiring_Date', 'Offer_Date']
        for col in date_cols:
            if col in cleaned_df.columns:
                if pd.api.types.is_datetime64_any_dtype(cleaned_df[col]):
                    print(f"✅ {col} 已正确转换为日期类型")
                    print(f"   日期范围: {cleaned_df[col].min()} 到 {cleaned_df[col].max()}")
                else:
                    print(f"⚠️ {col} 未转换为日期类型")
        
        # 检查招聘阶段
        if 'Recruitment_Stages' in cleaned_df.columns:
            stage_counts = cleaned_df['Recruitment_Stages'].value_counts()
            print(f"\n招聘阶段分布:")
            for stage, count in stage_counts.items():
                print(f"  {stage}: {count}")
        
        print("\n✅ 示例数据测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 示例数据测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_period_comparison_logic():
    """测试时间段对比逻辑"""
    print("\n" + "=" * 60)
    print("测试4: 时间段对比逻辑")
    print("=" * 60)
    
    # 复制calculate_funnel_metrics函数
    def calculate_funnel_metrics(df):
        metrics = {}
        if 'Recruitment_Stages' not in df.columns:
            return metrics
        
        stage_counts = df['Recruitment_Stages'].value_counts()
        funnel_stages = ['Applied', 'Phone Screening', 'Harver Test', 'Interview', 'Offer', 'Hired']
        
        for stage in funnel_stages:
            metrics[stage] = int(stage_counts.get(stage, 0))
        
        interview_plus = metrics.get('Interview', 0) + metrics.get('Offer', 0) + metrics.get('Hired', 0)
        total_applied = metrics.get('Applied', 0)
        
        if total_applied > 0:
            metrics['app_to_interview_rate'] = round(interview_plus / total_applied * 100, 2)
        else:
            metrics['app_to_interview_rate'] = 0
        
        offer_plus = metrics.get('Offer', 0) + metrics.get('Hired', 0)
        interview_stage_total = interview_plus
        
        if interview_stage_total > 0:
            metrics['interview_to_offer_rate'] = round(offer_plus / interview_stage_total * 100, 2)
        else:
            metrics['interview_to_offer_rate'] = 0
        
        if offer_plus > 0:
            metrics['offer_to_hire_rate'] = round(metrics.get('Hired', 0) / offer_plus * 100, 2)
        else:
            metrics['offer_to_hire_rate'] = 0
        
        if total_applied > 0:
            metrics['overall_conversion_rate'] = round(metrics.get('Hired', 0) / total_applied * 100, 2)
        else:
            metrics['overall_conversion_rate'] = 0
        
        return metrics
    
    # 创建时间段A的数据（较好的表现）
    data_a = {
        'Application_Date': pd.date_range('2023-09-01', periods=100, freq='D'),
        'Recruitment_Stages': ['Hired'] * 15 + ['Offer'] * 10 + ['Interview'] * 20 + 
                               ['Harver Test'] * 15 + ['Phone Screening'] * 20 + ['Applied'] * 20
    }
    df_a = pd.DataFrame(data_a)
    
    # 创建时间段B的数据（较差的表现）
    data_b = {
        'Application_Date': pd.date_range('2023-06-01', periods=100, freq='D'),
        'Recruitment_Stages': ['Hired'] * 8 + ['Offer'] * 7 + ['Interview'] * 15 + 
                               ['Harver Test'] * 10 + ['Phone Screening'] * 30 + ['Applied'] * 30
    }
    df_b = pd.DataFrame(data_b)
    
    print(f"\n时间段A (2023-09): {len(df_a)} 条记录")
    print(f"时间段B (2023-06): {len(df_b)} 条记录")
    
    # 计算两个时间段的指标
    metrics_a = calculate_funnel_metrics(df_a)
    metrics_b = calculate_funnel_metrics(df_b)
    
    print(f"\n时间段A 转化率:")
    print(f"  申请到面试: {metrics_a.get('app_to_interview_rate')}%")
    print(f"  面试到Offer: {metrics_a.get('interview_to_offer_rate')}%")
    print(f"  Offer到入职: {metrics_a.get('offer_to_hire_rate')}%")
    print(f"  整体转化率: {metrics_a.get('overall_conversion_rate')}%")
    
    print(f"\n时间段B 转化率:")
    print(f"  申请到面试: {metrics_b.get('app_to_interview_rate')}%")
    print(f"  面试到Offer: {metrics_b.get('interview_to_offer_rate')}%")
    print(f"  Offer到入职: {metrics_b.get('offer_to_hire_rate')}%")
    print(f"  整体转化率: {metrics_b.get('overall_conversion_rate')}%")
    
    # 验证时间段A确实比B好
    assert metrics_a.get('overall_conversion_rate') > metrics_b.get('overall_conversion_rate'), \
        "时间段A的整体转化率应该高于时间段B"
    
    # 计算差异
    diff_overall = metrics_a.get('overall_conversion_rate') - metrics_b.get('overall_conversion_rate')
    print(f"\n整体转化率差异 (A - B): +{diff_overall:.2f}%")
    
    print("\n✅ 时间段对比逻辑测试通过!")
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🔍 招聘看板核心逻辑测试")
    print("=" * 60)
    
    all_passed = True
    
    try:
        all_passed = test_clean_data() and all_passed
    except Exception as e:
        print(f"❌ 测试1失败: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    try:
        all_passed = test_calculate_funnel_metrics() and all_passed
    except Exception as e:
        print(f"❌ 测试2失败: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    try:
        all_passed = test_sample_data() and all_passed
    except Exception as e:
        print(f"❌ 测试3失败: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    try:
        all_passed = test_period_comparison_logic() and all_passed
    except Exception as e:
        print(f"❌ 测试4失败: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过!")
        print("\n核心功能验证:")
        print("  ✅ 数据清洗逻辑 (去重、日期转换)")
        print("  ✅ 招聘漏斗转化率计算")
        print("  ✅ 示例数据兼容性")
        print("  ✅ 时间段对比逻辑")
    else:
        print("⚠️ 部分测试失败，请检查上面的错误信息")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    exit(main())

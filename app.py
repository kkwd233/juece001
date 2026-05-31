import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def calculate_pv_annuity_factor(i, n):
    """计算等额年金现值系数 (P/A, i, n)"""
    if i == 0:
        return n
    return (1 - (1 + i) ** (-n)) / i

def calculate_npv(investment_cost, current_revenue, initial_growth_rate, growth_decay_rate, discount_rate, project_years, cost_increase_rate):
    npv_results = []

    for t in range(project_years + 1):
        future_cost = investment_cost * (1 + cost_increase_rate) ** t
        effective_growth_rate = max(0, initial_growth_rate * (1 - growth_decay_rate) ** t)

        cumulative_growth = 1.0
        for year in range(t):
            year_growth = max(0, initial_growth_rate * (1 - growth_decay_rate) ** year)
            cumulative_growth *= (1 + year_growth)

        future_revenue = current_revenue * cumulative_growth

        remaining_years = max(0, project_years - t)

        if discount_rate > 0 and remaining_years > 0:
            pv_annuity_factor = calculate_pv_annuity_factor(discount_rate, remaining_years)
            pv_revenue = future_revenue * pv_annuity_factor
            npv = (-future_cost + pv_revenue) / ((1 + discount_rate) ** t)
        elif remaining_years == 0:
            npv = -future_cost
        else:
            npv = float('inf')

        npv_results.append({
            '等待年份': t,
            '剩余年限': remaining_years,
            '投资成本': round(future_cost, 2),
            '年收益': round(future_revenue, 2),
            '有效增长率': round(effective_growth_rate * 100, 2),
            'NPV': round(npv, 2)
        })

    return npv_results

def find_optimal_time(npv_results):
    max_npv = max(npv_results, key=lambda x: x['NPV'])
    return max_npv

def analyze_discount_rate_sensitivity(investment_cost, current_revenue, initial_growth_rate, growth_decay_rate, project_years, cost_increase_rate, base_discount_rate):
    discount_rates = np.linspace(0.01, 0.2, 20)
    results = []

    for dr in discount_rates:
        npv_results = calculate_npv(investment_cost, current_revenue, initial_growth_rate, growth_decay_rate, dr, project_years, cost_increase_rate)
        optimal = find_optimal_time(npv_results)
        results.append({
            '折现率': round(dr * 100, 1),
            '最佳等待年份': optimal['等待年份'],
            '最大NPV': round(optimal['NPV'], 2)
        })

    return pd.DataFrame(results)

def main():
    st.set_page_config(page_title="项目投资时机决策模拟器", layout="wide")

    st.title("项目投资时机决策模拟器")
    st.markdown("帮助您判断项目应当现在投资，还是等待几年后再投资")

    with st.sidebar:
        st.header("基本参数")

        investment_cost = st.number_input("当前投资成本（万元）", value=1000, min_value=0, step=10)
        current_revenue = st.number_input("当前年收益（万元）", value=200, min_value=0, step=10)

        col_yr, col_yr_slider = st.columns([1, 2])
        with col_yr:
            project_years = st.number_input("项目年限", value=15, min_value=1, max_value=50, step=1)
        with col_yr_slider:
            project_years = st.slider("项目年限", min_value=1, max_value=50, value=int(project_years), step=1)

        col_dr, col_dr_slider = st.columns([1, 2])
        with col_dr:
            discount_rate = st.number_input("折现率", value=0.1, min_value=0.01, max_value=0.5, step=0.01, format="%.2f")
        with col_dr_slider:
            discount_rate = st.slider("折现率", min_value=0.01, max_value=0.5, value=discount_rate, step=0.01, format="%.2f")

        st.header("收益增长设置")

        col_igr, col_igr_slider = st.columns([1, 2])
        with col_igr:
            initial_growth_rate = st.number_input("初始收益率", value=0.15, min_value=0.0, max_value=1.0, step=0.01, format="%.2f")
        with col_igr_slider:
            initial_growth_rate = st.slider("初始收益率", min_value=0.0, max_value=1.0, value=initial_growth_rate, step=0.01, format="%.2f")

        col_gdr, col_gdr_slider = st.columns([1, 2])
        with col_gdr:
            growth_decay_rate = st.number_input("增长率变化率", value=0.08, min_value=-0.5, max_value=1.0, step=0.01, format="%.2f")
        with col_gdr_slider:
            growth_decay_rate = st.slider("增长率变化率", min_value=-0.5, max_value=1.0, value=growth_decay_rate, step=0.01, format="%.2f")

        st.header("成本变化设置")

        col_cir, col_cir_slider = st.columns([1, 2])
        with col_cir:
            cost_increase_rate = st.number_input("成本上升率", value=0.03, min_value=-0.5, max_value=1.0, step=0.01, format="%.2f")
        with col_cir_slider:
            cost_increase_rate = st.slider("成本上升率", min_value=0.0, max_value=1.0, value=cost_increase_rate, step=0.01, format="%.2f")

    npv_results = calculate_npv(investment_cost, current_revenue, initial_growth_rate, growth_decay_rate, discount_rate, project_years, cost_increase_rate)
    df_npv = pd.DataFrame(npv_results)
    optimal_time = find_optimal_time(npv_results)

    col_chart, col_optimal = st.columns([0.8, 0.2])

    with col_chart:
        st.subheader("NPV随等待时间变化曲线")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df_npv['等待年份'],
            y=df_npv['NPV'],
            mode='lines+markers',
            marker=dict(color='#2B4162', size=8),
            line=dict(color='#2B4162', width=2),
            name='NPV'
        ))

        fig.add_trace(go.Scatter(
            x=[optimal_time['等待年份']],
            y=[optimal_time['NPV']],
            mode='markers',
            marker=dict(color='red', size=14, symbol='star'),
            name='最佳投资点'
        ))

        fig.update_layout(
            xaxis_title='等待年份',
            yaxis_title='NPV（万元）',
            height=450,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        st.plotly_chart(fig, width='stretch')

    with col_optimal:
        st.subheader("最佳投资时机")
        st.metric("推荐等待年份", f"{optimal_time['等待年份']} 年")
        st.metric("该时点NPV", f"{optimal_time['NPV']} 万元")
        st.metric("该时点投资成本", f"{optimal_time['投资成本']} 万元")
        st.metric("该时点年收益", f"{optimal_time['年收益']} 万元")
        st.metric("剩余年限", f"{optimal_time['剩余年限']} 年")
        st.metric("该时点有效增长率", f"{optimal_time['有效增长率']}%")

        if optimal_time['等待年份'] == 0:
            st.success("建议立即投资！")
        else:
            st.info(f"建议等待 {optimal_time['等待年份']} 年后再投资")

    st.subheader("各等待年份NPV计算结果")
    st.dataframe(df_npv, width='stretch')

    col_growth, col_cost = st.columns(2)

    with col_growth:
        st.subheader("有效增长率变化曲线")
        fig_growth = px.line(df_npv, x='等待年份', y='有效增长率',
                             title='有效增长率随等待年份变化',
                             markers=True,
                             color_discrete_sequence=['#1B9E77'])

        fig_growth.update_layout(
            xaxis_title='等待年份',
            yaxis_title='有效增长率 (%)',
            height=400
        )
        st.plotly_chart(fig_growth, width='stretch')

    with col_cost:
        st.subheader("投资成本变化曲线")
        fig_cost = px.line(df_npv, x='等待年份', y='投资成本',
                           title='投资成本随等待年份变化',
                           markers=True,
                           color_discrete_sequence=['#D95F02'])

        fig_cost.update_layout(
            xaxis_title='等待年份',
            yaxis_title='投资成本（万元）',
            height=400
        )
        st.plotly_chart(fig_cost, width='stretch')

    st.subheader("折现率敏感性分析")
    df_sensitivity = analyze_discount_rate_sensitivity(investment_cost, current_revenue, initial_growth_rate, growth_decay_rate, project_years, cost_increase_rate, discount_rate)

    fig_sensitivity = px.line(df_sensitivity, x='折现率', y='最佳等待年份',
                              title='折现率变化对最佳投资时机的影响',
                              markers=True,
                              color_discrete_sequence=['#2B4162'])

    fig_sensitivity.update_layout(
        xaxis_title='折现率 (%)',
        yaxis_title='最佳等待年份',
        height=400
    )
    st.plotly_chart(fig_sensitivity, width='stretch')

    st.dataframe(df_sensitivity, width='stretch')

    with st.expander("公式说明"):
        st.markdown("""
        **等额年金现值系数 (P/A, i, n)**：
        $$P/A, i, n = \\frac{1 - (1+i)^{-n}}{i}$$

        **NPV计算公式**：
        $$NPV(t) = \\frac{-C_0(1+\\alpha)^t + R_t \\times P/A, i, n-t}{(1+i)^t}$$

        其中：
        - $C_0$：当前投资成本
        - $\\alpha$：成本上升率
        - $R_t$：第t年的年收益
        - $i$：折现率
        - $n$：项目总年限
        - $n-t$：等待t年后的剩余经营年限
        """)

if __name__ == "__main__":
    main()
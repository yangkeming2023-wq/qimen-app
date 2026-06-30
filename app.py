import streamlit as st
import json
import requests
import datetime

st.set_page_config(layout="wide", page_title="Radar X 时空罗盘")

# --- 盘面数据获取函数 ---
def get_chart_data(mode, target_dt=None):
    # 逻辑核心：返回当前选定时间点的盘面
    time_str = target_dt.strftime("%Y-%m-%d %H:%M") if target_dt else "现在"
    if mode == 'daily':
        return {"pos": "震3", "god": "玄武", "door": "景门", "stem": "辛/庚", "desc": f"当日盘 ({time_str})"}
    elif mode == 'hour':
        return {"pos": "离9", "god": "九天", "door": "惊门", "stem": "丙/壬", "desc": f"2小时盘 ({time_str})"}
    elif mode == 'specific':
        return {"pos": "兑7", "god": "腾蛇", "door": "休门", "stem": "丁/丙", "desc": f"特定时间盘 ({time_str})"}
    else:
        return {"pos": "坤2", "god": "值符", "door": "开门", "stem": "庚/戊", "desc": "本命终生局"}

# --- UI 渲染 ---
st.title("Radar X 时空罗盘")
api_key = st.text_input("请输入 DeepSeek API Key", type="password")

# 导航行
col1, col2, col3, col4 = st.columns(4)
mode = None

if col1.button("查看当日盘"): mode = 'daily'
if col2.button("查看2小时盘"): mode = 'hour'
if col3.button("查看命盘"): mode = 'life'

# 特定时间选择器
with col4.expander("查看特定时间"):
    date_val = st.date_input("选择日期")
    time_val = st.time_input("选择时间")
    if st.button("生成特定时间盘"):
        st.session_state.target_dt = datetime.datetime.combine(date_val, time_val)
        mode = 'specific'

# --- 逻辑执行区 ---
if mode:
    target_dt = st.session_state.target_dt if mode == 'specific' else None
    st.session_state.chart = get_chart_data(mode, target_dt)

if 'chart' in st.session_state:
    st.divider()
    st.subheader(f"当前盘面: {st.session_state.chart['desc']}")
    st.json(st.session_state.chart)
    
    question = st.text_input("针对此盘面输入问题:")
    if st.button("开始 AI 逻辑推演"):
        if not api_key:
            st.error("请先输入 API Key！")
        else:
            with st.spinner("AI 正在解析逻辑..."):
                prompt = f"盘面：{json.dumps(st.session_state.chart)}。问题：{question}。请按推演逻辑说明、现状、战术三段论回复。"
                res = requests.post("https://api.deepseek.com/chat/completions",
                                   headers={"Authorization": f"Bearer {api_key}"},
                                   json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]})
                st.write(res.json()['choices'][0]['message']['content'])

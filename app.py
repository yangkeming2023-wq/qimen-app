import streamlit as st
import json
import requests
import datetime

# --- 1. 核心排盘模拟 (保持绝对独立) ---
def get_chart_data(mode):
    # 逻辑：根据模式返回全新的数据字典，确保不会引用旧缓存
    now = datetime.datetime.now()
    if mode == 'daily':
        return {"pos": "震3", "god": "玄武", "door": "景门", "stem": "辛/庚", "desc": "今日环境大盘"}
    elif mode == 'hour':
        return {"pos": "离9", "god": "九天", "door": "惊门", "stem": "丙/壬", "desc": "当前2小时切片"}
    else:
        return {"pos": "坤2", "god": "值符", "door": "开门", "stem": "庚/戊", "desc": "终生命局"}

# --- 2. 初始化环境 ---
st.set_page_config(layout="wide")
if 'key' not in st.session_state: st.session_state.key = ""
if 'page' not in st.session_state: st.session_state.page = 'home'

# --- 3. 极简逻辑路由 ---
if st.session_state.page == 'home':
    st.title("Radar X 时空罗盘")
    st.session_state.key = st.text_input("请输入 DeepSeek API Key", type="password")
    
    col1, col2, col3 = st.columns(3)
    # 点击按钮时，直接写入 session 并触发跳转
    if col1.button("查看当日盘"):
        st.session_state.chart = get_chart_data('daily')
        st.session_state.page = 'result'
        st.rerun()
    if col2.button("查看2小时盘"):
        st.session_state.chart = get_chart_data('hour')
        st.session_state.page = 'result'
        st.rerun()
    if col3.button("查看命盘"):
        st.session_state.chart = get_chart_data('life')
        st.session_state.page = 'result'
        st.rerun()

elif st.session_state.page == 'result':
    st.subheader(f"当前盘面逻辑: {st.session_state.chart['desc']}")
    st.write(st.session_state.chart) # 显示纯净数据
    
    question = st.text_input("请输入你想测算的问题")
    if st.button("开始逻辑推演"):
        # 严格封装 AI 指令
        prompt = f"""
        【背景】：这是一张奇门遁甲盘面数据：{json.dumps(st.session_state.chart)}
        【任务】：
        1. 必须说明你提取了盘面的哪些符号（如：值符、景门）作为判断依据。
        2. 基于这些符号，进行推演逻辑说明。
        3. 给出结论。
        【问题】：{question}
        """
        try:
            res = requests.post("https://api.deepseek.com/chat/completions",
                               headers={"Authorization": f"Bearer {st.session_state.key}"},
                               json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]})
            st.markdown("### 推演结论")
            st.write(res.json()['choices'][0]['message']['content'])
        except Exception as e:
            st.error("请检查 Key 或网络，数据未能同步：" + str(e))
            
    if st.button("返回首页（重置）"):
        st.session_state.page = 'home'
        st.rerun()

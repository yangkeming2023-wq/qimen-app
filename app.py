import streamlit as st
import json
import requests
import datetime

# --- 配置 ---
st.set_page_config(layout="centered", page_title="Radar X 时空罗盘")

# --- 核心排盘模拟数据 (用于测试逻辑是否通畅) ---
def get_chart_data(mode):
    # 此处逻辑：根据点击的 mode 返回不同的数据，确保页面能感知到变化
    if mode == 'daily':
        return {"pos": "震3", "god": "玄武", "door": "景门", "stem": "辛/庚", "desc": "当日能量场"}
    elif mode == 'hour':
        return {"pos": "离9", "god": "九天", "door": "惊门", "stem": "丙/壬", "desc": "当前2小时能量场"}
    else:
        return {"pos": "坤2", "god": "值符", "door": "开门", "stem": "庚/戊", "desc": "本命终生局"}

# --- UI 逻辑流 ---
st.title("Radar X 时空罗盘")

# 1. API Key 处理
api_key = st.text_input("请输入 DeepSeek API Key", type="password")

# 2. 功能入口
col1, col2, col3 = st.columns(3)
mode = None

if col1.button("查看当日盘"): mode = 'daily'
if col2.button("查看2小时盘"): mode = 'hour'
if col3.button("查看命盘"): mode = 'life'

# 3. 逻辑触发与展示区
if mode:
    # 状态存入 session，防止点击后数据丢失
    st.session_state.chart = get_chart_data(mode)
    st.session_state.mode = mode

# 如果已有数据，则显示盘面与推演入口
if 'chart' in st.session_state:
    st.divider()
    st.success(f"已加载: {st.session_state.chart['desc']}")
    st.json(st.session_state.chart) # 确认数据已正确切换
    
    question = st.text_input("针对此盘面输入你要测算的问题:")
    if st.button("开始 AI 逻辑推演"):
        if not api_key:
            st.error("请先在上方输入 API Key！")
        else:
            with st.spinner("AI 正在深度解析..."):
                prompt = f"""
                【盘面】：{json.dumps(st.session_state.chart)}
                【任务】：根据盘面逻辑进行详细推演，并说明你依据的符号（如门、星）。
                【问题】：{question}
                """
                try:
                    res = requests.post("https://api.deepseek.com/chat/completions",
                                       headers={"Authorization": f"Bearer {api_key}"},
                                       json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]})
                    
                    st.markdown("### AI 推演建议")
                    st.write(res.json()['choices'][0]['message']['content'])
                except Exception as e:
                    st.error("推演失败，请检查 Key 或网络：" + str(e))

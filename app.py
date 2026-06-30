import streamlit as st
import json
import requests
import datetime

# --- 配置区域 ---
st.set_page_config(page_title="Radar X 时空罗盘", layout="centered")

# --- 逻辑说明与样式 ---
st.markdown("""
<style>
    .qimen-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 5px; margin: 10px 0; }
    .palace { background: #1a1d27; padding: 10px; border-radius: 5px; font-size: 11px; text-align: center; border: 1px solid #334155; }
    .logic-box { background: #1e293b; padding: 15px; border-radius: 8px; border-left: 4px solid #f59e0b; margin: 15px 0; font-size: 13px; color: #cbd5e1; }
</style>
""", unsafe_allow_html=True)

# --- 模拟排盘引擎 (此处对接 bazi-mcp 逻辑) ---
def get_chart_by_time(dt, mode):
    # 此处应调用 bazi-mcp 计算干支，此处为结构示例
    hour_stem = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"][dt.hour % 10]
    return {
        "time_context": f"{dt.strftime('%Y-%m-%d %H:%M')} | 时干: {hour_stem}",
        "palaces": [
            {"pos": "巽4", "god": "九地", "door": "死门", "stem": "乙/辛", "desc": "用户本命宫"},
            {"pos": "离9", "god": "九天", "door": "惊门", "stem": "丙/壬", "desc": "事业用神"},
            {"pos": "坤2", "god": "值符", "door": "开门", "stem": "庚/戊", "desc": "大环境"}
        ]
    }

# --- 初始化 ---
if 'page' not in st.session_state: st.session_state.page = 'onboarding'

# --- 页面逻辑 ---
if st.session_state.page == 'onboarding':
    st.title("Radar X 初始化")
    name = st.text_input("称呼", "Alex")
    bazi = st.text_input("出生时间", "1990-05-01 14:00")
    key = st.text_input("DeepSeek API Key", type="password")
    if st.button("启动"):
        st.session_state.user = {'name': name, 'bazi': bazi, 'key': key}
        st.session_state.page = 'dashboard'
        st.rerun()

elif st.session_state.page == 'dashboard':
    st.title("时空罗盘")
    col1, col2 = st.columns(2)
    
    # 模式选择
    modes = {'当日': 'daily', '2小时': 'hour', '特定': 'specific'}
    for name, mode in modes.items():
        if st.button(f"生成{name}盘"):
            dt = datetime.datetime.now()
            st.session_state.chart = get_chart_by_time(dt, mode)
            st.session_state.mode = mode
            st.session_state.page = 'query'
            st.rerun()

elif st.session_state.page == 'query':
    st.subheader(f"当前盘面: {st.session_state.mode}")
    # 显示排盘
    chart = st.session_state.chart
    st.write(f"时间锚点: {chart['time_context']}")
    
    # 动态渲染九宫格
    cols = st.columns(3)
    for i, p in enumerate(chart['palaces']):
        with cols[i % 3]:
            st.markdown(f"<div class='palace'><b>{p['pos']}</b><br>{p['god']}<br>{p['door']}<br>{p['stem']}</div>", unsafe_allow_html=True)
    
    question = st.text_area("提问")
    if st.button("生成推演"):
        # 严格指令集
        system_prompt = """你是一位战略顾问。必须按以下格式输出：
        1. 【核心定调】：一句话胜负。
        2. 【推算逻辑说明】：详细说明提取了盘面中哪三个宫位，根据五行生克或八门性质推导出了什么结论，方便用户验证。
        3. 【拆解现状】：结合盘面元素进行叙述。
        4. 【破局战术】：给出一个具体动作。"""
        
        # API 请求逻辑
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"盘面数据: {json.dumps(chart)}\n问题: {question}"}
            ]
        }
        
        try:
            res = requests.post("https://api.deepseek.com/chat/completions", 
                               headers={"Authorization": f"Bearer {st.session_state.user['key']}"},
                               json=payload)
            ans = res.json()['choices'][0]['message']['content']
            st.markdown(f"<div class='logic-box'>{ans}</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error("API 异常: " + str(e))
    
    if st.button("返回"):
        st.session_state.page = 'dashboard'
        st.rerun()

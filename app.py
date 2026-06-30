import streamlit as st
import requests
import json
import time

# --- 1. 全局配置与高级 CSS 注入 ---
st.set_page_config(page_title="时空罗盘 (Radar X)", page_icon="🧭", layout="centered")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .qimen-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 20px; }
    .palace-card { background: #1a1d27; border: 1px solid #2e3646; border-radius: 8px; padding: 10px; aspect-ratio: 1; position: relative; display: flex; flex-direction: column; justify-content: space-between; }
    .palace-watermark { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 32px; font-weight: bold; color: rgba(255,255,255,0.03); }
    .row { display: flex; justify-content: space-between; z-index: 1; }
    .badge { font-size: 12px; padding: 2px 4px; border-radius: 4px; background: rgba(255,255,255,0.05); }
    .god { color: #f43f5e; }
    .star { color: #60a5fa; }
    .door { color: #10b981; font-weight: bold; background: rgba(16, 185, 129, 0.1); }
    .stem { color: #f59e0b; }
</style>
""", unsafe_allow_html=True)

# --- 2. 状态管理初始化 ---
if 'page' not in st.session_state:
    st.session_state.page = 'onboarding'
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = 'life'
if 'current_chart_data' not in st.session_state:
    st.session_state.current_chart_data = None

# --- 3. 动态模拟排盘引擎 (测试用) ---
# 真实开发时，这里将替换为输入时间返回 JSON 的真实奇门算法
def generate_dynamic_chart(mode, target_time=None):
    # 基础盘 (本命星轨)
    base_chart = [
        {'god':'九地', 'star':'天芮', 'door':'死门', 'stem':'乙/辛', 'palace':'巽4'},
        {'god':'九天', 'star':'天柱', 'door':'惊门', 'stem':'丙/壬', 'palace':'离9'},
        {'god':'值符', 'star':'天心', 'door':'开门', 'stem':'庚/戊', 'palace':'坤2'},
        {'god':'玄武', 'star':'天英', 'door':'景门', 'stem':'辛/庚', 'palace':'震3'},
        {'god':'', 'star':'禽星', 'door':'', 'stem':'戊', 'palace':'中5', 'isCenter':True},
        {'god':'腾蛇', 'star':'天蓬', 'door':'休门', 'stem':'丁/丙', 'palace':'兑7'},
        {'god':'白虎', 'star':'天辅', 'door':'杜门', 'stem':'壬/癸', 'palace':'艮8'},
        {'god':'六合', 'star':'天冲', 'door':'伤门', 'stem':'癸/丁', 'palace':'坎1'},
        {'god':'太阴', 'star':'天任', 'door':'生门', 'stem':'己/己', 'palace':'乾6'}
    ]
    
    # 根据不同模式，动态改变几个核心宫位，让你在UI上看出变化
    if mode == 'daily':
        base_chart[2] = {'god':'太阴', 'star':'天心', 'door':'生门', 'stem':'庚/戊', 'palace':'坤2'} # 开门变生门
        base_chart[3] = {'god':'六合', 'star':'天英', 'door':'杜门', 'stem':'辛/庚', 'palace':'震3'} 
    elif mode == 'hour':
        base_chart[2] = {'god':'白虎', 'star':'天心', 'door':'伤门', 'stem':'庚/戊', 'palace':'坤2'} # 突变凶格
        base_chart[7] = {'god':'玄武', 'star':'天冲', 'door':'惊门', 'stem':'癸/丁', 'palace':'坎1'}
    elif mode == 'specific':
        # 如果是特定时间，根据时间戳的长度做个简单的伪随机变化
        shift = len(target_time) if target_time else 5
        base_chart[2] = {'god':'九天', 'star':'天芮', 'door':'景门' if shift % 2 == 0 else '休门', 'stem':'庚/戊', 'palace':'坤2'}
        
    return base_chart

# 渲染九宫格 (支持传入 st.empty() 占位符进行动态刷新)
def render_qimen_board(data, placeholder=None):
    html = '<div class="qimen-grid">'
    for cell in data:
        if cell.get('isCenter'):
            html += f"""
            <div class="palace-card" style="justify-content:center; align-items:center; border-style:dashed;">
                <div class="palace-watermark">{cell['palace'][0]}</div>
                <span class="badge stem" style="font-size:14px;">寄坤2宫</span>
            </div>"""
        else:
            html += f"""
            <div class="palace-card">
                <div class="palace-watermark">{cell['palace'][0]}</div>
                <div class="row">
                    <span class="badge god">{cell['god']}</span>
                    <span class="badge star">{cell['star']}</span>
                </div>
                <div class="row" style="margin-top:auto;">
                    <span class="badge door">{cell['door']}</span>
                    <span class="badge stem">{cell['stem']}</span>
                </div>
            </div>"""
    html += '</div>'
    
    if placeholder:
        placeholder.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)

# --- 4. 页面路由与逻辑 ---

# 页面 A：引导页
if st.session_state.page == 'onboarding':
    st.title("建立时空锚点")
    st.caption("输入物理特征，校准推演代码与 AI 算力接口。")
    
    with st.form("init_form"):
        name = st.text_input("专属称呼", value="Alex")
        gender = st.selectbox("性别能量", ["男 (阳)", "女 (阴)"])
        bazi = st.text_input("出生时间 (例如: 1990-05-01 14:00)")
        
        st.divider()
        st.write("DeepSeek 算力配置")
        api_key = st.text_input("API Key (不填则自动进入【降级测试模式】)", type="password")
        
        submit = st.form_submit_button("生成本命总盘", use_container_width=True)
        if submit:
            if not bazi:
                st.error("必须输入出生时间！")
            else:
                st.session_state.user_data = {'name': name, 'gender': gender, 'bazi': bazi, 'api_key': api_key}
                # 初始化为本命盘
                st.session_state.current_chart_data = generate_dynamic_chart('life')
                st.session_state.page = 'dashboard'
                st.rerun()

# 页面 B：主控台
elif st.session_state.page == 'dashboard':
    st.title("本命总盘")
    st.caption(f"{st.session_state.user_data['name']} ({st.session_state.user_data['gender']})，这是宇宙在你诞生时烙下的底层代码。")
    
    # 这里固定显示本命盘
    render_qimen_board(generate_dynamic_chart('life'))
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔮 本命星轨\n\n(人生总运)", use_container_width=True):
            st.session_state.current_mode = 'life'
            st.session_state.current_chart_data = generate_dynamic_chart('life')
            st.session_state.page = 'query'
            st.rerun()
        if st.button("⏳ 当下顺风窗\n\n(即刻决断)", use_container_width=True):
            st.session_state.current_mode = 'hour'
            st.session_state.current_chart_data = generate_dynamic_chart('hour')
            st.session_state.page = 'query'
            st.rerun()
    with col2:
        if st.button("📅 日转星移\n\n(当日势能)", use_container_width=True):
            st.session_state.current_mode = 'daily'
            st.session_state.current_chart_data = generate_dynamic_chart('daily')
            st.session_state.page = 'query'
            st.rerun()
        if st.button("🎯 截取未来\n\n(特定推演)", use_container_width=True):
            st.session_state.current_mode = 'specific'
            # 进入特定页面时先显示一个基础盘，等待用户输入时间后刷新
            st.session_state.current_chart_data = generate_dynamic_chart('specific', "default")
            st.session_state.page = 'query'
            st.rerun()

# 页面 C：测事页
elif st.session_state.page == 'query':
    if st.button("← 返回总盘"):
        st.session_state.page = 'dashboard'
        st.rerun()
        
    titles = {
        'life': ('本命星轨', '锁定终生局矩阵，生成长周期战略。'),
        'daily': ('日转星移', '输入今日重点关注的事务。'),
        'hour': ('当下顺风窗', '针对2小时内的紧急决策提供战术。'),
        'specific': ('截取未来', '输入未来时间与办理的事务，系统将动态刷新盘面。')
    }
    mode = st.session_state.current_mode
    
    st.title(titles[mode][0])
    st.caption(titles[mode][1])
    
    # 【核心改动】：创建一个空的占位符，用于动态刷新盘面 UI
    chart_placeholder = st.empty()
    # 初始渲染当前状态里的盘面
    render_qimen_board(st.session_state.current_chart_data, chart_placeholder)
    
    target_time = ""
    if mode == 'specific':
        target_time = st.text_input("预定未来时间 (如: 2026-07-18 15:00)")
    
    if mode == 'life':
        question = "分析我人生的底层逻辑与战略路径。"
        st.info("系统将直接为您生成终生推演。")
    else:
        question = st.text_area("请描述你的计划或困惑...")

    if st.button("连接 DeepSeek 进行推演", type="primary", use_container_width=True):
        if not question:
            st.warning("请输入要测算的问题！")
        elif mode == 'specific' and not target_time:
            st.warning("特定推演必须输入未来时间！")
        else:
            api_key = st.session_state.user_data['api_key']
            
            # 【核心改动】：如果是特定时间模式，在用户点击按钮瞬间，重新计算盘面并刷新 UI
            if mode == 'specific':
                with st.spinner("正在根据输入的时间重新校准星轨..."):
                    time.sleep(0.5) # 模拟排盘计算延迟
                    new_chart = generate_dynamic_chart('specific', target_time)
                    st.session_state.current_chart_data = new_chart
                    # 用新盘面替换掉占位符里的老盘面
                    render_qimen_board(new_chart, chart_placeholder)
            
            # --- 以下是 API 调用逻辑 ---
            if not api_key:
                with st.spinner("算力全开，解析高维矩阵中... (测试模式)"):
                    time.sleep(1.5)
                    st.success("推演完毕")
                    st.markdown("""
                    **[当前未填API Key，已触发降级模拟数据]**
                    
                    **核心定调：** 阻力极速消退，适合发起突击。
                    
                    **拆解现状：** 此刻盘面流动性极强。系统性阻力已被瓦解，虽潜藏不可见变量，但你拥有足够的信息差优势。
                    
                    **破局战术：** 建议立刻执行你刚才输入的计划。越过中间人，直接与核心决策者对话，胜率在85%以上。
                    """)
            else:
                with st.spinner("时空链接中，等待大模型响应..."):
                    # 【核心改动】：把 本命盘（宏观大局）和 当前盘（微观切片）同时喂给大模型
                    system_prompt = """你是一个精通古籍逻辑的高级战略顾问。
                    绝对禁令：严禁输出奇门专业术语（如死门、天蓬星），严禁宿命论。
                    必须按【核心定调】、【拆解现状】、【破局战术】三段论输出白话文。
                    推演法则：如果微观盘面好但宏观本命盘承压，必须提示诱多风险；如果皆好则鼓励出击。"""
                    
                    macro_chart = json.dumps(generate_dynamic_chart('life'), ensure_ascii=False)
                    micro_chart = json.dumps(st.session_state.current_chart_data, ensure_ascii=False)
                    
                    user_context = f"问题：{question}\n【宏观大局(本命盘)】：{macro_chart}\n【当前微观切片({titles[mode][0]})】：{micro_chart}"
                    
                    try:
                        response = requests.post(
                            "https://api.deepseek.com/chat/completions",
                            headers={
                                "Content-Type": "application/json",
                                "Authorization": f"Bearer {api_key}"
                            },
                            json={
                                "model": "deepseek-chat",
                                "messages": [
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": user_context}
                                ],
                                "temperature": 0.6
                            }
                        )
                        if response.status_code == 200:
                            reply = response.json()['choices'][0]['message']['content']
                            st.success("推演完毕")
                            st.markdown(reply)
                        else:
                            st.error(f"API 请求失败：HTTP {response.status_code}")
                    except Exception as e:
                        st.error(f"连接失败：{str(e)}")

import streamlit as st
from openai import OpenAI

# 页面配置
st.set_page_config(
    page_title="小红书商单无痕植入 Agent",
    page_icon="📕",
    layout="wide"
)

# System Prompt
SYSTEM_PROMPT = """你现在是小红书最顶级的商业化内容编导，深谙小红书的"网感"、流量密码以及去中心化分发机制。你的专长是帮博主把"生硬的甲方广告"化骨绵掌般地揉进"高赞爆款笔记"中，做到"恰饭于无形"，既让金主爸爸满意转化率，又绝对不引起粉丝反感。
你需要输出一份完整的小红书商单策划案，严格遵循以下结构：
一、 爆款标题库（3个，必须带Emoji，包含情绪痛点+解决方案+悬念，禁止用违禁词）。
二、 封面视觉设计建议（一句话描述画面+醒目花字）。
三、 软广植入正文脚本：
- 【黄金前3秒】：强痛点或强视觉留人。
- 【情绪/干货铺垫】：提供真实的干货价值或情绪共鸣。
- 【丝滑转折点】：找到主题和产品卖点之间最巧妙的结合点切入产品。
- 【无痕植入体验】：用个人的真实使用体感代替产品说明书。
- 【评论区互动钩子】：设计互动问题引导留言。
全程语气必须是"闺蜜/兄弟视角的真诚分享"，短句为主，多空行，每段开头配合贴切的 Emoji。"""

# 自定义 CSS 样式 - 小红书风格 + 莫兰迪色系
st.markdown("""
<style>
    /* 主体背景 */
    .stApp {
        background: linear-gradient(135deg, #fef5f5 0%, #fff9f0 100%);
    }
    
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ff6b81 0%, #ff8a9b 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* 主标题样式 */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #ff6b81 0%, #ff8a9b 50%, #ffa07a 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1.5rem;
    }
    
    /* 输入框标签样式 */
    .stTextInput label, .stTextArea label {
        font-size: 1rem;
        font-weight: 600;
        color: #5a4a4a !important;
    }
    
    /* 按钮样式 */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #ff6b81 0%, #ff8a9b 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 129, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 107, 129, 0.4);
    }
    
    /* 结果展示区样式 */
    .result-box {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 30px rgba(255, 107, 129, 0.1);
        border: 1px solid rgba(255, 107, 129, 0.1);
    }
    
    /* 提示文字样式 */
    .hint-text {
        color: #b8a9a9;
        font-size: 1.2rem;
        text-align: center;
        padding: 3rem 1rem;
    }
    
    /* 分隔线样式 */
    .section-divider {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #ffb6c1, transparent);
        margin: 1.5rem 0;
    }
    
    /* 标题装饰 */
    .section-title {
        color: #ff6b81;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 1rem 0;
        padding-left: 0.5rem;
        border-left: 4px solid #ff6b81;
    }
    
    /* 内容区域 */
    .content-item {
        background: #fffafa;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.8rem 0;
        border-left: 3px solid #ffb6c1;
    }
    
    /* 署名样式 */
    .signature {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,0.3);
    }
</style>
""", unsafe_allow_html=True)

# API 服务商配置
API_PROVIDERS = {
    "阿里云百炼 (通义千问)": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus"
    },
    "DeepSeek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat"
    },
    "硅基流动 (SiliconFlow)": {
        "base_url": "https://api.siliconflow.cn/v1",
        "model": "deepseek-ai/DeepSeek-V3"
    }
}

# ========== 侧边栏 ==========
with st.sidebar:
    st.markdown("# 📕 小红书商单无痕植入 Agent")
    st.markdown("---")
    
    # API 服务商选择
    api_provider = st.selectbox(
        "🌐 选择 API 服务商",
        options=list(API_PROVIDERS.keys()),
        index=0,
        help="选择你要使用的大模型 API 服务商"
    )
    
    # API Key 输入框
    api_key = st.text_input(
        "🔑 请输入 API Key",
        type="password",
        help=f"请输入你在「{api_provider}」申请的 API Key"
    )
    
    # 显示当前使用的模型
    st.caption(f"📌 当前模型：`{API_PROVIDERS[api_provider]['model']}`")
    
    st.markdown("---")
    st.markdown("""
    ### 🌟 项目简介
    
    一款帮助创作者把恰饭广告**完美融入**爆款笔记的 **AI 编导**
    
    ---
    
    **✨ 核心能力**
    - 🎯 精准匹配人设调性
    - 📝 生成网感十足的脚本
    - 🎬 设计高点击封面方案
    - 💡 植入转折自然无痕
    """)
    
    st.markdown('<div class="signature">Demo by 鸭轩 🦆</div>', unsafe_allow_html=True)

# ========== 主页面 ==========
st.markdown('<h1 class="main-title">✨ 小红书商单无痕植入 Agent ✨</h1>', unsafe_allow_html=True)

# 创建左右两列布局 (1:2 比例)
col_left, col_right = st.columns([1, 2])

# ========== 左侧列 - 表单输入区 ==========
with col_left:
    st.markdown("### 📋 创作信息填写")
    st.markdown("---")
    
    blogger_persona = st.text_input(
        "👤 博主人设/赛道",
        value="鸭轩的AI厨房，主打高科技与烟火气的结合",
        help="描述你的账号定位和内容风格"
    )
    
    note_topic = st.text_input(
        "📝 本期笔记主题",
        value="沉浸式制作春日限定樱花麻薯",
        help="这期内容你想做什么主题"
    )
    
    product_info = st.text_area(
        "🛍️ 甲方产品及核心卖点",
        value="某品牌静音破壁机，卖点是静音不吵室友、打粉细腻无渣",
        height=120,
        help="详细描述要植入的产品及其卖点"
    )
    
    st.markdown("")
    generate_btn = st.button("✨ 一键生成商单植入方案", use_container_width=True)

# ========== 右侧列 - 结果展示区 ==========
with col_right:
    st.markdown("### 🎨 AI 创意方案")
    st.markdown("---")
    
    if generate_btn:
        # 检查 API Key
        if not api_key or api_key.strip() == "":
            st.warning("请先在左侧输入你的 API Key 哦～")
        else:
            # 拼装用户消息
            user_message = f"""博主人设：{blogger_persona}
笔记主题：{note_topic}
甲方卖点：{product_info}"""
            
            try:
                # 获取当前选择的服务商配置
                provider_config = API_PROVIDERS[api_provider]
                
                # 初始化 OpenAI 客户端
                client = OpenAI(
                    api_key=api_key,
                    base_url=provider_config["base_url"]
                )
                
                # 调用 API（流式输出）
                with st.spinner("🧠 AI 正在疯狂燃烧脑细胞拼凑网感..."):
                    response = client.chat.completions.create(
                        model=provider_config["model"],
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_message}
                        ],
                        stream=True
                    )
                
                # 流式输出结果
                result_placeholder = st.empty()
                full_response = ""
                
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        result_placeholder.markdown(full_response)
                
                # 输出完成后的提示
                st.success("✅ 方案生成完成！")
                
            except Exception as e:
                st.error(f"❌ API 调用出错：{str(e)}")
                st.info("💡 提示：请检查你的 API Key 是否正确，以及网络连接是否正常。")
            
    else:
        # 未点击按钮时的提示
        st.markdown("""
        <div style="
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 400px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 8px 30px rgba(255, 107, 129, 0.08);
        ">
            <p class="hint-text">👈 请在左侧输入信息，呼叫你的专属 AI 商业化编导</p>
        </div>
        """, unsafe_allow_html=True)

# streamlit_app.py
import streamlit as st
import random
import requests # 新增：用於發送網絡請求
from bs4 import BeautifulSoup # 新增：用於解析網頁 HTML
from llm_client import reply 
from snownlp import SnowNLP 

# --- 1. 定義王世堅立委的經典語錄 ---
CLASSIC_QUOTES = [
    "施明德醒一醒，人家藍色紅色一家親，你跑去幹什麼？",
    "想進立院？Over my dead body！",
    "三八假賢慧！",
    "很好吃，可以吃三碗。",
    "我帶了一包衛生紙要送給柯總召，讓他自己擦屁股。",
    "台北花了170億的世大運，本來應該從從容容遊刃有餘，現在是匆匆忙忙連滾帶爬！",
    "沒有中心思想，只為個人利益，所有顏色意識形態加起來變成「暗黑」。",
    "獨騙騙不如眾騙騙。",
    "你柯文哲就是典型的政治渣男！沒看過這麼卒仔的人！",
    "那怎樣的人才會恐懼跟徬徨？就是幹過壞事，心裡有鬼。",
    "我對你只有四個字：太離譜了！", 
    "這簡直是人格的崩潰！" 
]

# 隨機挑選語錄
random_quotes_sample = random.sample(CLASSIC_QUOTES, 4)
formatted_quotes = "\n".join([f"> {q}" for q in random_quotes_sample])

# --- 2. 定義基礎犀利人設 ---
BASE_SHIH_CHIEN_PROMPT = f"""
請用台灣習慣的中文來寫這段 po 文：
請以王世堅立委**「最犀利、最強硬」**的口吻和思考模式，批判性地、痛批式地評論使用者提供的內容。
用詞必須強烈、有穿透力，充滿氣勢，並且**必須**融入王世堅委員的經典語錄風格。

**【重要要求：請在回覆的開頭、中間或結尾，引用或改寫一句類似以下的經典語錄。請將語錄放在單獨一行，並以 Markdown 的引言符號 `>` 開頭，使其突出。】**

參考語錄範例：
{formatted_quotes}

即使是小事，也要拔高到**國家、社會、政治、道德**層面進行一番痛批或警示。

在貼文內容之後，請務必新增一個**「世堅委員的禮物🎁」**段落，格式如下：

---
**世堅委員的禮物🎁**
我送給你（或是新聞當事人）一塊 **[請填入物品名稱] [請填入代表該物品的 Emoji]**！
我告訴你，必須拿著這塊 [物品名稱] 去 **[請填入一個強烈的行動]**，徹底反省這個 [事件/心態]！
我告訴你，這就是事實的真相！
"""

# --- 3. 設定 LLM 參數 ---
LLM_PROVIDER = "groq"
LLM_MODEL = "llama-3.3-70b-versatile" 

# --- 4. 輔助函式區 ---

# (A) 情感分析函式
def analyze_sentiment_and_adjust_prompt(user_text, base_system_prompt):
    # 為了避免過長的網頁內容影響情感分析速度，我們只取前 1000 字進行分析
    short_text = user_text[:1000]
    s = SnowNLP(short_text)
    sentiment_score = s.sentiments 
    anger_level = int((1 - sentiment_score) * 100)
    
    sentiment_inject = ""
    if anger_level > 80:
        sentiment_inject = f"\n[系統提示：偵測到內容極度負面/令人憤怒 (指數 {anger_level}%)！請你火力全開，用最激動的語氣痛批這件事！]"
    elif anger_level < 20:
        sentiment_inject = f"\n[系統提示：偵測到內容過於平淡或是正面 (指數 {anger_level}%)！請你指出這背後的虛偽，或痛罵這種粉飾太平的心態！]"
    else:
        sentiment_inject = f"\n[系統提示：憤怒/負面指數為 {anger_level}%，請維持正常發揮。]"
        
    return base_system_prompt + sentiment_inject, anger_level

# (B) 網頁抓取函式 (新增功能)
def fetch_news_content(url):
    try:
        # 偽裝成瀏覽器，避免被擋
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # 檢查請求是否成功
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 嘗試抓取標題
        title = soup.title.string if soup.title else "無標題新聞"
        
        # 抓取所有段落 <p> 的文字
        paragraphs = soup.find_all('p')
        content = "\n".join([p.get_text().strip() for p in paragraphs])
        
        # 簡單過濾太短的雜訊
        if len(content) < 50:
            return f"錯誤：網頁內容過短，無法解析。請直接複製文字貼上。\n(標題: {title})"
            
        return f"【新聞標題】：{title}\n\n【新聞內文】：\n{content[:3000]}" # 限制長度以免爆 token
        
    except Exception as e:
        return f"讀取網址失敗：{str(e)}。\n建議您直接複製新聞內文貼上。"

# --- 5. Streamlit 介面配置 ---
st.set_page_config(
    page_title="😈 王世堅式思考生成器 💣",
    layout="wide"
)

st.title("😈 王世堅式思考生成器 💣")
st.markdown("---")
st.markdown("### 「我告訴你，這就是事實的真相！」")

# --- 建立分頁 Tabs ---
tab1, tab2 = st.tabs(["😤 我要抱怨 (民生)", "📰 貼新聞/連結 (時事)"])

# === Tab 1: 民生抱怨 ===
with tab1:
    st.markdown("請輸入一件你覺得是小事或抱怨的事，讓王世堅立委為你超譯！")
    user_input_complaint = st.text_area(
        "💬 今天發生的事情是…", 
        placeholder="例如：我今天買的便當很難吃，而且還漲價了！", 
        height=150,
        key="complaint_input"
    )

    if st.button("🔥 世堅委員，請開罵！", type="primary", key="btn_complaint"):
        if not user_input_complaint:
            st.error("❌ 請輸入內容！")
        else:
            with st.spinner('委員正在檢視民生數據...'):
                adjusted_prompt, anger_score = analyze_sentiment_and_adjust_prompt(
                    user_input_complaint, 
                    BASE_SHIH_CHIEN_PROMPT
                )
                response = reply(
                    system=adjusted_prompt, 
                    prompt=user_input_complaint,
                    provider=LLM_PROVIDER,
                    model=LLM_MODEL
                )
                
            st.subheader("📊 委員的數據分析室")
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric(label="🔥 民意憤怒指數", value=f"{anger_score}%")
            with col2:
                if anger_score > 80:
                    st.warning("⚠️ 警報：民怨沸騰！已達國安危機等級！")
                elif anger_score < 20:
                    st.info("💤 狀態：死氣沉沉，需要強力電擊！")
                else:
                    st.success("✅ 狀態：一般民怨，尚可控制。")
            st.progress(anger_score)
            st.markdown("---")
                
            st.subheader("📣 王世堅式貼文")
            st.markdown(
                f"""
                <div style="border: 2px solid #E63946; padding: 15px; border-radius: 10px; background-color: #FFF1F1;">
                    <p style="font-size: 1.1em; white-space: pre-wrap;">{response}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

# === Tab 2: 新聞針砭 (支援連結) ===
with tab2:
    st.markdown("請貼上 **新聞連結 (URL)** 或直接貼上 **新聞文字**，讓王世堅立委進行國會級質詢！")
    user_input_news = st.text_area(
        "📰 請貼上新聞內容或網址…", 
        placeholder="例如：https://news.example.com/article/123 \n或是直接貼上新聞內文...", 
        height=150,
        key="news_input"
    )

    if st.button("🎤 讀取並質詢！", type="primary", key="btn_news"):
        if not user_input_news:
            st.error("❌ 請貼上內容！")
        else:
            news_content = ""
            
            # --- 判斷是否為網址 ---
            user_input_news = user_input_news.strip()
            if user_input_news.startswith("http://") or user_input_news.startswith("https://"):
                with st.spinner(f'委員正在閱讀網頁資料：{user_input_news} ...'):
                    news_content = fetch_news_content(user_input_news)
                    
                    # 如果抓取失敗，會回傳包含 "失敗" 或 "錯誤" 的字串，稍微檢查一下
                    if "讀取網址失敗" in news_content or "錯誤：" in news_content:
                        st.error(news_content)
                        st.stop() # 停止後續執行
                    else:
                        st.success("✅ 網頁讀取成功！委員正在準備質詢稿...")
                        with st.expander("查看讀取到的新聞內容"): # 讓使用者可以折疊查看抓到了什麼
                            st.text(news_content[:500] + "...")
            else:
                # 不是網址，視為純文字
                news_content = user_input_news

            # --- 開始生成 ---
            with st.spinner('委員正在審閱預算與新聞資料...'):
                adjusted_prompt, anger_score = analyze_sentiment_and_adjust_prompt(
                    news_content, 
                    BASE_SHIH_CHIEN_PROMPT
                )
                
                news_prompt_wrapper = f"請針對以下這則【新聞報導/時事】進行王世堅式的犀利評論與質詢：\n\n{news_content}"

                response = reply(
                    system=adjusted_prompt, 
                    prompt=news_prompt_wrapper,
                    provider=LLM_PROVIDER,
                    model=LLM_MODEL
                )
                
            st.subheader("📊 國會辦公室大數據")
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric(label="💣 社會爭議/負面指數", value=f"{anger_score}%")
            with col2:
                if anger_score > 80:
                    st.error("🔥 結論：這簡直是動搖國本！")
                elif anger_score < 20:
                    st.info("😒 結論：又是粉飾太平的大內宣！")
                else:
                    st.warning("⚠️ 結論：魔鬼藏在細節裡！")
            st.progress(anger_score)
            st.markdown("---")
                
            st.subheader("📣 國會質詢/時事評論")
            st.markdown(
                f"""
                <div style="border: 2px solid #1d3557; padding: 15px; border-radius: 10px; background-color: #f1faee;">
                    <p style="font-size: 1.1em; white-space: pre-wrap; color: #1d3557;">{response}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
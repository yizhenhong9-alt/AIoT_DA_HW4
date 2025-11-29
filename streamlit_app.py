import streamlit as st
import random
import requests
from bs4 import BeautifulSoup
from llm_client import reply, analyze_emotion_via_llm # <-- 關鍵修改：導入新的函式
import json # 雖然在 llm_client 裡使用，但這裡也確保有導入以防萬一

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

# (A) 情緒分析函式 (大幅修改，改為呼叫 LLM_CLIENT 的 JSON 分析)
def analyze_emotion_and_adjust_prompt(user_text, base_system_prompt):
    
    # 呼叫 LLM 進行情緒分析
    emotion_data = analyze_emotion_via_llm(user_text, provider=LLM_PROVIDER, model=LLM_MODEL)
    
    # 錯誤處理
    if "error" in emotion_data:
        return base_system_prompt + f"\n[系統提示：情緒分析失敗，請使用一般語氣。錯誤: {emotion_data['error']}]", "分析失敗", 0

    dominant_emotion = emotion_data.get("dominant_emotion", "質疑")
    intensity_score = emotion_data.get("intensity_score", 50)
    
    sentiment_inject = ""
    # 根據 JSON 輸出的核心情緒和強度來調整 Prompt
    if "憤怒" in dominant_emotion or "失望" in dominant_emotion and intensity_score > 80:
        sentiment_inject = f"\n[系統提示：偵測到內容核心情緒為【{dominant_emotion}】(強度 {intensity_score}%)！請你火力全開，用最激動的語氣痛批這件事，並將其升級為政治弊案！]"
    elif "輕視" in dominant_emotion or "質疑" in dominant_emotion:
        sentiment_inject = f"\n[系統提示：內容情緒為【{dominant_emotion}】(強度 {intensity_score}%)！請你以嚴謹的態度進行質詢，並提出尖銳的、邏輯層面的疑問！]"
    elif "中立" in dominant_emotion or "平靜" in dominant_emotion and intensity_score < 30:
        sentiment_inject = f"\n[系統提示：偵測到內容過於平靜/中立 ({intensity_score}%)！請你指出這背後的虛偽，或痛罵這種粉飾太平的心態！]"
    else:
        sentiment_inject = f"\n[系統提示：偵測到核心情緒為【{dominant_emotion}】(強度 {intensity_score}%)，請維持正常犀利發揮。]"

    return base_system_prompt + sentiment_inject, dominant_emotion, intensity_score

# (B) 網頁抓取函式 (不變)
def fetch_news_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "無標題新聞"
        paragraphs = soup.find_all('p')
        content = "\n".join([p.get_text().strip() for p in paragraphs])
        
        if len(content) < 50:
            return f"錯誤：網頁內容過短，無法解析。請直接複製文字貼上。\n(標題: {title})"
            
        return f"【新聞標題】：{title}\n\n【新聞內文】：\n{content[:3000]}"
        
    except Exception as e:
        return f"讀取網址失敗：{str(e)}。\n建議您直接複製新聞內文貼上。"

# --- 5. Streamlit 介面配置與邏輯 ---
st.set_page_config(
    page_title="😈 王世堅式思考生成器 💣",
    layout="wide"
)

st.title("😈 王世堅式思考生成器 💣")
st.markdown("---")
st.markdown("### 「我告訴你，這就是事實的真相！」")

tab1, tab2 = st.tabs(["😤 我要抱怨 (民生)", "📰 貼新聞/連結 (時事)"])

# === Tab 1 & Tab 2 邏輯合併處理 ===

def run_analysis_and_reply(user_input, is_news_mode):
    # --- 1. 執行情緒分析 (需要先執行) ---
    with st.spinner('委員正在調閱資料，進行情緒分析...'):
        # 這裡會執行對 LLM 的第一次呼叫 (JSON 分析)
        adjusted_prompt, dominant_emotion, intensity_score = analyze_emotion_and_adjust_prompt(
            user_input, 
            BASE_SHIH_CHIEN_PROMPT
        )
        
    # 顯示數據
    st.subheader("📊 委員的數據分析室")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric(label="核心情緒", value=f"{dominant_emotion}")
        st.metric(label="強度指數", value=f"{intensity_score}%")
    with col2:
        # 根據情緒給予評語
        if "憤怒" in dominant_emotion or "失望" in dominant_emotion:
            st.warning(f"⚠️ 警報：情緒趨向【{dominant_emotion}】！已達高層關注等級！")
        elif "輕視" in dominant_emotion or "質疑" in dominant_emotion:
            st.info(f"🧐 狀態：情緒趨向【{dominant_emotion}】，需要理性且尖銳的質詢！")
        else:
            st.success(f"✅ 狀態：情緒趨向【{dominant_emotion}】，請指出這背後的弊端。")
    st.progress(intensity_score)
    st.markdown("---")

    # --- 2. 執行貼文生成 (主呼叫) ---
    with st.spinner('委員正在撰寫犀利貼文與質詢稿...'):
        if is_news_mode:
             final_prompt = f"請針對以下這則【新聞報導/時事】進行王世堅式的犀利評論與質詢：\n\n{user_input}"
        else:
             final_prompt = user_input
             
        response = reply(
            system=adjusted_prompt, 
            prompt=final_prompt,
            provider=LLM_PROVIDER,
            model=LLM_MODEL
        )

    # 3. 顯示結果
    st.subheader("📣 王世堅式貼文/國會質詢")
    style_div = """
    <div style="border: 2px solid #E63946; padding: 15px; border-radius: 10px; background-color: #FFF1F1;">
        <p style="font-size: 1.1em; white-space: pre-wrap;">{response}</p>
    </div>
    """ if not is_news_mode else """
    <div style="border: 2px solid #1d3557; padding: 15px; border-radius: 10px; background-color: #f1faee;">
        <p style="font-size: 1.1em; white-space: pre-wrap; color: #1d3557;">{response}</p>
    </div>
    """
    st.markdown(style_div.format(response=response), unsafe_allow_html=True)


# --- Tab 1: 民生抱怨 邏輯 ---
with tab1:
    st.markdown("請輸入一件你覺得是小事或抱怨的事，讓王世堅立委為你超譯！")
    user_input_complaint = st.text_area(
        "💬 今天發生的事情是…", 
        placeholder="例如：我今天買的便當很難吃，而且還漲價了！", 
        height=150,
        key="complaint_input"
    )
    if st.button("🔥 世堅委員，請開罵！", type="primary", key="btn_complaint"):
        if user_input_complaint:
            run_analysis_and_reply(user_input_complaint, is_news_mode=False)
        else:
            st.error("❌ 請輸入內容！")

# === Tab 2: 新聞針砭 邏輯 ---
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
            user_input_news = user_input_news.strip()
            
            # --- 判斷是否為網址，並進行爬蟲 ---
            if user_input_news.startswith("http://") or user_input_news.startswith("https://"):
                with st.spinner(f'委員正在閱讀網頁資料：{user_input_news} ...'):
                    news_content = fetch_news_content(user_input_news)
                    
                    if "讀取網址失敗" in news_content or "錯誤：" in news_content:
                        st.error(news_content)
                        st.stop()
                    else:
                        st.success("✅ 網頁讀取成功！")
                        with st.expander("查看讀取到的新聞內容"): 
                            st.text(news_content[:500] + "...")
            else:
                news_content = user_input_news

            # --- 開始運行分析與生成 ---
            run_analysis_and_reply(news_content, is_news_mode=True)

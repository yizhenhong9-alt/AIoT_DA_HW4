# 😈 王世堅式思考生成器 (Shih Chien Style Generator)

> **「我告訴你，這就是事實的真相！」** —— 讓王世堅立委為您生活中的大小事進行超譯，並對時事新聞進行國會級質詢。

## 📸 應用程式展示 (Demo)

| 介面功能 | 圖表引用 |
| :--- | :--- |
| **圖 1：民生抱怨專區** | 請見專案截圖 **(圖 1)**：展示使用者輸入、LLM 結構化情緒分析結果，以及生成的貼文。 |
| **圖 2：時事質詢專區** | 請見專案截圖 **(圖 2)**：展示貼上新聞 URL 或文字後的爬蟲讀取狀態、數據分析結果，以及最終的國會質詢評論。 |

-----

## 📖 專案簡介

本專案係基於 [yenlung/AI-Demo](https://github.com/yenlung/AI-Demo) 中的 **【Demo04】用 OpenAI\_API 打造員瑛式思考生成器.ipynb** 實作範例進行**深度學習專題實作與功能延伸**。

本專案開發了一款名為「王世堅式思考生成器」的互動式 AI 應用程式，旨在利用生成式 AI 技術模擬台灣知名立委王世堅的獨特問政風格與批判思維。系統透過**向 LLM 發出結構化分析請求**，偵測文本背後的**核心情緒（例如：憤怒、質疑）**，並據此動態調整委員的憤怒值與開罵力道。

本專案模擬了台灣知名立委王世堅的獨特問政風格。它不僅能處理使用者的日常抱怨，還能直接讀取新聞連結，將內容拔高到「國安危機」等級進行犀利批判。

## ✨ 核心功能

### 1\. 兩大模式切換 (Tabs)

  * **😤 我要抱怨 (民生專區)**：針對便當漲價、塞車等生活瑣事進行宣洩。委員將會指出這背後的結構性問題（或單純借題發揮）。
  * **📰 貼新聞/連結 (時事質詢)**：
      * **支援網址讀取**：直接貼上新聞 URL，系統自動爬取標題與內文。
      * **國會質詢模式**：針對新聞事件進行嚴肅且犀利的政治評論。

### 2\. 📊 國會大數據 (結構化情緒分析)

  * **專業分析**：使用 LLM 輸出 **JSON 格式** 進行分析，判斷文本的**核心情緒**（如憤怒、質疑、失望）及**強度指數**。
  * **數據展現**：在介面顯示 **核心情緒** 與 **強度指數**。
  * **動態 Prompt**：
      * **趨向憤怒/失望**：委員火力全開，將其升級為政治弊案。
      * **趨向輕視/質疑**：委員以嚴謹的態度進行質詢，並提出尖銳的、邏輯層面的疑問。

### 3\. 😈 經典重現與禮物機制

  * **動態語錄**：每次回答都會隨機引用經典金句（如「Over my dead body」、「政治渣男」），並以 Markdown 引言區塊 (`>`) 強調。
  * **委員的禮物**：AI 根據話題內容，自動送出一件具象化的「Emoji 禮物」（如 🧹 掃帚、🎻 小提琴、🥪 便當），並以此要求執行強烈的反省行動。

## 📂 專案結構

```text
shih-chien-llm-app/
├── .env                  # 存放 API Key 的環境變數檔 (請勿上傳至 GitHub)
├── llm_client.py         # 處理 AISuite 與 LLM 溝通的邏輯（含 JSON 分析）
├── streamlit_app.py      # 主程式：包含介面、爬蟲、情緒分析結果展示邏輯
├── requirements.txt      # 專案依賴套件列表
└── README.md             # 專案說明文件
```

## 🛠️ 安裝與設定

### 1\. 環境準備

確保您的電腦已安裝 Python 3.9 或以上版本。

```bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境 (Windows)
.\venv\Scripts\activate

# 啟動虛擬環境 (macOS/Linux)
source venv/bin/activate
```

### 2\. 安裝依賴套件

本專案集成了多個強大套件。

```bash
# 核心 LLM、Streamlit、爬蟲工具
pip install aisuite[groq] streamlit python-dotenv requests beautifulsoup4
```

### 3\. 設定 API 金鑰

本專案使用 **Groq** 提供的 Llama-3 模型。

1.  前往 [Groq Console](https://console.groq.com/) 申請免費 API Key。
2.  在專案根目錄建立 `.env` 檔案。
3.  填入金鑰：

<!-- end list -->

```env
GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## 🚀 如何執行

在終端機執行：

```bash
streamlit run streamlit_app.py
```

瀏覽器將自動開啟應用程式（預設 `http://localhost:8501`）。

Streamlit.app: https://aiotdahw4-7114056010.streamlit.app/

## 📝 使用指南

### 情境 A：生活不如意

1.  點選 **「😤 我要抱怨」** 分頁。
2.  輸入：「今天下大雨忘了帶傘，全身濕透。」
3.  按下 **「🔥 世堅委員，請開罵！」**。
4.  查看\*\*「核心情緒」\*\*分析結果，並閱讀委員如何將其連結到「城市基礎建設的失敗」並領取您的禮物。

### 情境 B：看到不爽的新聞

1.  點選 **「📰 貼新聞/連結」** 分頁。
2.  貼上一則新聞網址（例如：`https://news.example.com/...`）。
3.  按下 **「🎤 讀取並質詢！」**。
4.  系統會自動抓取內文，並生成一篇針對該事件的國會質詢稿。

## 💡 技術棧

  * **專案起源**: [yenlung/AI-Demo](https://github.com/yenlung/AI-Demo)
  * **Frontend**: [Streamlit](https://streamlit.io/)
  * **LLM Engine**: [AISuite](https://github.com/andrewyng/aisuite) & [Groq](https://groq.com/)
  * **Core Analysis**: LLM-driven Structured JSON Analysis (取代 SnowNLP)
  * **Web Crawler**: `requests` + `BeautifulSoup4`
  * **Language**: Python

## 🤝 貢獻與聲明

  * **Disclaimer**: 本專案純屬程式開發練習與娛樂用途，內容由 AI 生成，不代表真實人物立場。
  * 歡迎提交 PR 擴充更多「經典語錄」或優化爬蟲功能。

-----

Copyright © 2025 Shih-Chien Generator Project

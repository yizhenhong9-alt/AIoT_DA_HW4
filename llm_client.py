import aisuite as ai
import os
from dotenv import load_dotenv
import json

# 載入 .env 檔案（如果您使用方法 A 設置金鑰）
load_dotenv() 

def reply(system: str, prompt: str, provider: str = "groq", model: str = "llama-3.3-70b-versatile") -> str:
    """
    呼叫 LLM 並取得回覆（用於生成貼文）。
    """
    
    # 檢查 API 金鑰是否已載入環境變數
    if provider == "groq" and not os.getenv('GROQ_API_KEY'):
        return "錯誤：找不到 Groq API 金鑰。請檢查 .env 檔案或環境變數設定。"
    
    try:
        client = ai.Client()
    except Exception as e:
        return f"錯誤：初始化 AI Client 失敗。{e}"

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt}
    ]

    try:
        response = client.chat.completions.create(
            model=f"{provider}:{model}", 
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"錯誤：LLM 呼叫失敗。請檢查模型名稱或 API 權限。詳情: {e}"

def analyze_emotion_via_llm(text_to_analyze: str, provider: str = "groq", model: str = "llama-3.3-70b-versatile") -> dict:
    """
    呼叫 LLM 進行精確的情緒分析，並要求 JSON 輸出。
    """
    
    if provider == "groq" and not os.getenv('GROQ_API_KEY'):
        return {"error": "API Key Missing"}

    try:
        client = ai.Client()
    except Exception as e:
        return {"error": f"Client Init Failed: {e}"}

    # 設計專門的 System Prompt，要求分析情緒並以 JSON 格式輸出
    system_prompt = """
    你是一位專門分析社會與政治情緒的專家。
    請分析以下文本內容的情緒傾向、強度與主旨，並嚴格以 JSON 格式輸出。
    JSON 格式必須包含以下鍵值：
    - "dominant_emotion": 核心情緒 (例如: 憤怒, 質疑, 恐懼, 失望, 輕視, 中立)。
    - "intensity_score": 該情緒的強度分數 (0 到 100)。
    - "critique_target": 文本批判或討論的對象 (例如: 柯文哲, 電價政策, 便當漲價, 使用者本人)。
    - "justification": 簡單說明為何會得出這個情緒判斷 (用中文)。
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text_to_analyze}
    ]

    try:
        # 使用 JSON 模式強制 LLM 輸出為結構化數據 (Groq/Llama3 支援)
        response = client.chat.completions.create(
            model=f"{provider}:{model}", 
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        # 解析並返回 JSON
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        print(f"JSON analysis failed: {e}")
        return {"error": "LLM JSON 解析失敗", "dominant_emotion": "錯誤", "intensity_score": 0}

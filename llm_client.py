# llm_client.py
import aisuite as ai
import os
from dotenv import load_dotenv

# 載入 .env 檔案（如果您使用方法 A 設置金鑰）
load_dotenv() 

def reply(system: str, prompt: str, provider: str = "groq", model: str = "llama-3.3-70b-versatile") -> str:
    """
    呼叫 LLM 並取得回覆。
    """
    
    # 檢查 API 金鑰是否已載入環境變數
    if provider == "groq" and not os.getenv('GROQ_API_KEY'):
        return "錯誤：找不到 Groq API 金鑰。請檢查 .env 檔案或環境變數設定。"
    
    try:
        # ai.Client() 會自動查找 os.environ 中的金鑰
        client = ai.Client()
    except Exception as e:
        return f"錯誤：初始化 AI Client 失敗。{e}"

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt}
    ]

    try:
        # 使用 f"{provider}:{model}" 指定模型和供應商
        response = client.chat.completions.create(
            model=f"{provider}:{model}", 
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        # 捕獲並返回任何 API 呼叫錯誤
        return f"錯誤：LLM 呼叫失敗。請檢查模型名稱或 API 權限。詳情: {e}"
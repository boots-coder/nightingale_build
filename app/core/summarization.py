import os
import json
from openai import OpenAI

# --- 安全提示 ---
# 强烈建议：不要在代码中硬编码API Key。
# 请在终端中设置环境变量：
# export OPENAI_API_KEY='你的真实API Key'
# PyCharm中也可以在运行配置里设置环境变量。
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def _chunk_transcript(transcript: str) -> list[str]:
    """一个简单的辅助函数，将文本按句子分割并添加索引。"""
    # 这里的实现可以更复杂，例如使用NLTK等库，但为了简单起见，我们先用句号分割
    sentences = transcript.split('.')
    return [f"[{i}]: {sentence.strip()}." for i, sentence in enumerate(sentences) if sentence.strip()]

def generate_summaries_from_text(transcript: str) -> dict:
    """
    调用LLM从文本生成两种摘要和溯源信息。
    """
    chunked_transcript = "\n".join(_chunk_transcript(transcript))

    prompt = f"""
    You are a highly skilled medical note analyst. Your task is to process a patient-clinician dialogue and generate two distinct summaries based on it.

    **Instructions:**
    1.  Generate a **Clinician Summary** in a structured SOAP (Subjective, Objective, Assessment, Plan) format.
    2.  Generate a **Patient Summary** that is empathetic, easy to understand, and includes clear next steps.
    3.  **Crucially, every single point in both summaries MUST be grounded in the provided dialogue.** At the end of each point, you MUST cite the source sentence index(es) in the format `[S#]` or `[S#, S#]`.
    4.  Your final output must be a single, valid JSON object, and nothing else. Do not include any explanatory text before or after the JSON.

    **Dialogue with Sentence Indexes:**
    {chunked_transcript}

    **Required JSON Output Format:**
    {{
      "clinician_summary": {{
        "subjective": "Patient's subjective complaints with source citations like [S0] or [S1, S2].",
        "objective": "Objective findings from the dialogue with source citations [S#].",
        "assessment": "Clinician's assessment with source citations [S#].",
        "plan": "Treatment and follow-up plan with source citations [S#]."
      }},
      "patient_summary": {{
        "greeting": "A friendly opening statement.",
        "points": [
          "A summary point for the patient, easy to understand, with source citations [S#].",
          "Another summary point with source citations [S#]."
        ],
        "next_steps": "Clear, actionable next steps for the patient, with source citations [S#]."
      }}
    }}
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106", # 或者 gpt-4-turbo-preview
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a helpful medical assistant designed to output JSON."},
            {"role": "user", "content": prompt}
        ]
    )

    try:
        summary_data = json.loads(response.choices[0].message.content)
        return summary_data
    except (json.JSONDecodeError, IndexError) as e:
        print(f"Error parsing LLM response: {e}")
        # 在真实应用中，这里需要更健壮的错误处理和重试机制
        return {}
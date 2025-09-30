import os
import json
from openai import OpenAI

# --- 安全提示 ---
# 强烈建议：不要在代码中硬编码API Key。
# 请在终端中设置环境变量：
# export OPENAI_API_KEY='你的真实API Key'
# PyCharm中也可以在运行配置里设置环境变量。
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 在文件顶部添加
import nltk

# 首次运行时需要下载NLTK的句子分割模型
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    nltk.download('punkt')

# 在文件顶部，确保有 import nltk
import nltk


def _chunk_transcript(transcript: str) -> tuple[str, dict]:
    """
    使用NLTK将文本分割成带精确位置的句子，并生成用于Prompt的文本和位置地图。
    *** 此为修复版本，强制使用标准的 'punkt' tokenizer ***
    """
    # 1. 明确加载我们知道存在的标准英文punkt模型
    try:
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    except LookupError:
        print("Standard 'punkt' tokenizer not found. Downloading...")
        nltk.download('punkt')
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    # 2. 使用加载好的tokenizer来分割句子，并获取它们的span
    sentence_spans = tokenizer.span_tokenize(transcript)

    prompt_text_lines = []
    location_map = {}

    for i, span in enumerate(sentence_spans):
        start_char, end_char = span
        sentence = transcript[start_char:end_char]

        prompt_text_lines.append(f"[{i}]: {sentence}")
        location_map[i] = {"start": start_char, "end": end_char}

    return "\n".join(prompt_text_lines), location_map
def generate_summaries_from_text(transcript: str) -> tuple[dict, dict]:
    """
    调用LLM从文本生成两种摘要和溯源信息，并返回位置地图。
    """
    # 修改这一行
    chunked_transcript_for_prompt, location_map = _chunk_transcript(transcript)

    prompt = f"""
    You are a highly skilled medical note analyst. Your task is to process a patient-clinician dialogue and generate two distinct summaries based on it.

    **Instructions:**
    1.  Generate a **Clinician Summary** in a structured SOAP (Subjective, Objective, Assessment, Plan) format.
    2.  Generate a **Patient Summary** that is empathetic, easy to understand, and includes clear next steps.
    3.  **Crucially, every single point in both summaries MUST be grounded in the provided dialogue.** At the end of each point, you MUST cite the source sentence index(es) in the format `[S#]` or `[S#, S#]`.
    4.  Your final output must be a single, valid JSON object, and nothing else. Do not include any explanatory text before or after the JSON.

    **Dialogue with Sentence Indexes:**
    {chunked_transcript_for_prompt}

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
        # 在函数返回时，同时返回 summary_data 和 location_map
        return summary_data, location_map
    except (json.JSONDecodeError, IndexError) as e:
        print(f"Error parsing LLM response: {e}")
        return {}, {}
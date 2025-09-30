import spacy

# 加载spaCy模型，建议在应用启动时加载一次，避免重复加载
# 我们暂时先放在这里，后续可以优化
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model 'en_core_web_sm'...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# 定义需要被脱敏的实体标签
PHI_LABELS = {"PERSON", "GPE", "LOC", "DATE", "ORG", "TIME"}

def redact_text(text: str) -> str:
    """
    使用spaCy识别并脱敏文本中的PHI信息。
    这是一个简化的实现。
    """
    doc = nlp(text)
    redacted_text = list(text)

    for ent in doc.ents:
        if ent.label_ in PHI_LABELS:
            # 用占位符替换实体文本
            start = ent.start_char
            end = ent.end_char
            redacted_text[start:end] = f"[{ent.label_}]".ljust(len(ent.text))

    return "".join(redacted_text)
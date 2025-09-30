import pytest
from app.core.redaction import redact_text

def test_phi_is_redacted():
    """
    测试包含多种PHI的文本是否能被成功脱敏。
    """
    # 1. 准备一个包含多种PHI的合成样本
    sample_text = "The patient, John Appleseed, called on 2025-09-30 from his home in New York. " \
                  "He works for Apple Inc. and mentioned feeling dizzy at 8 AM this morning."

    # 2. 调用脱敏函数
    redacted_output = redact_text(sample_text)

    print(f"\nOriginal:  {sample_text}")
    print(f"Redacted:  {redacted_output}")

    # 3. 断言：原始的PHI信息不应该出现在输出中
    assert "John Appleseed" not in redacted_output
    assert "2025-09-30" not in redacted_output
    assert "New York" not in redacted_output
    assert "Apple Inc." not in redacted_output
    assert "8 AM" not in redacted_output

    # 4. 断言：占位符应该出现在输出中
    assert "[PERSON]" in redacted_output
    assert "[DATE]" in redacted_output
    assert "[GPE]" in redacted_output  # GPE = Geopolitical Entity
    assert "[ORG]" in redacted_output
    assert "[TIME]" in redacted_output
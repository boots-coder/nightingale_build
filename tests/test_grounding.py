import pytest
import re

def test_anchor_parsing_handles_complex_cases():
    """
    测试我们能否从一段文本中正确地解析出所有的溯源锚点，
    包括在一个中括号内有多个逗号分隔的数字的复杂情况。
    """
    # 1. 准备一个包含多种锚点格式的合成摘要
    summary_content = """
    {
      "subjective": "Patient complains of dizziness [S0, S1]. Also mentions headache [S3].",
      "plan": "Recommend CT scan and blood pressure monitoring [S4]."
    }
    """

    # 2. 更新的、更稳健的解析逻辑
    anchors_found = []
    # 步骤A: 找到所有完整的 [S...] 块
    citation_blocks = re.findall(r'\[S[^\]]*\]', summary_content)
    # citation_blocks 会是 ['[S0, S1]', '[S3]', '[S4]']

    # 步骤B: 从每个块中提取所有数字
    for block in citation_blocks:
        numbers = re.findall(r'\d+', block)
        anchors_found.extend(numbers)

    # 3. 定义我们期望找到的结果
    expected_anchors = ['0', '1', '3', '4']

    print(f"\nFound anchors: {anchors_found}")
    print(f"Expected anchors: {expected_anchors}")

    # 4. 断言：找到的结果与期望的结果应该完全一致 (排序后比较)
    assert sorted(anchors_found) == sorted(expected_anchors)
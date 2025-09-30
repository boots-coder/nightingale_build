# Nightingale - VoiceAI Patient Experience Prototype

## 1. 核心目标 (Objective)
本项目是为 Nightingale 48小时构建挑战赛而创建的功能完备原型。它旨在通过**语音优先的临床工作流**，提升从**诊前**到**诊中**再到**诊后**的完整患者体验。项目严格遵循三大核心原则：**隐私保护 (Privacy)**、**来源可追溯性 (Provenance)** 和 **低延迟 (Low Latency)**。


## 2. 核心功能 (Key Features)
- **身份认证与知情同意**：API 接口强制要求在处理任何数据前，必须获得患者的知情同意。
- **PHI 自动脱敏**：内置的 `spaCy` 模块可自动识别并遮蔽文本中的个人健康信息（PHI），确保日志和下游系统的安全。
- **双重摘要生成**：同一段对话可为**临床医生**生成结构化的SOAP格式摘要，为**患者**生成友好、可执行的摘要。
- **来源可追溯性 (Provenance)**：每一条摘要中的关键信息，都通过 `[S#]` 锚点链接回原始对话的具体句子，实现完全的可验证性。
- **模块化与可测试性**：项目采用清晰的模块化结构，并附有单元测试 (`pytest`) 保证核心功能的正确性。


## 3. API 文档和展示
本项目采用 FastAPI 构建，自带交互式 API 文档 (Swagger UI)。启动服务后，可访问以下地址进行实时 API 测试与交互：  
**[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**  


本项目包含一个交互式Web界面，用于直观地演示核心的“来源可追溯性”功能。

![Provenance Highlighting Demo](static/img_1.png)
![Provenance Highlighting Demo](static/img_2.png)
![Provenance Highlighting Demo](static/img_3.png)

*(上图演示：在右侧摘要中点击 `[S#]` 锚点后，左侧原文中的对应句子会自动滚动到视图并高亮显示。)*



## 4. 技术栈 (Tech Stack)
- **后端框架**：FastAPI
- **数据库**：SQLite（通过 SQLAlchemy ORM 进行交互）
- **AI & NLP**：
  - 摘要生成：OpenAI GPT-3.5-Turbo
  - PHI 脱敏：`spaCy`（`en_core_web_sm` 模型）
- **API 交互与验证**：Pydantic
- **测试框架**：Pytest


## 5. 项目结构
```
nightingale_build/
├── app/                  # 核心应用代码
│   ├── api/              # API 端点逻辑
│   ├── core/             # 核心业务逻辑 (脱敏, 摘要)
│   ├── db/               # 数据库模型和会话管理
│   ├── schemas/          # Pydantic 数据校验模型
│   └── main.py           # FastAPI 应用主入口
├── tests/                # 单元测试
├── .gitignore
├── Attribution.txt       # 第三方库署名
├── README.md             # 项目说明
└── requirements.txt      # Python 依赖
```


## 6. 安装与运行
1. **克隆仓库**：
   ```bash
   git clone <your-repo-url>
   cd nightingale_build
   ```

2. **创建并激活 Conda 环境**：
   ```bash
   conda create --name nightingale python=3.10 -y
   conda activate nightingale
   ```

3. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

4. **设置 OpenAI API Key (重要!)**：
   ```bash
   # 在 macOS/Linux
   export OPENAI_API_KEY='你的真实API Key'
   ```

5. **启动服务**：
   ```bash
   uvicorn app.main:app --reload
   ```
   服务将在 `http://127.0.0.1:8000` 运行。


## 7. 如何测试
本项目包含一套单元测试来验证核心功能的正确性。
- **运行所有测试**：
  ```bash
  pytest
  ```
- **单独运行某个测试文件 (例如脱敏测试)**：
  ```bash
  pytest tests/test_redaction.py
  ```


## 8. 如何扩展 API
本项目的模块化设计使得添加新的 API 端点非常简单：
1. **定义 Schema**：在 `app/schemas/` 目录下为新数据定义 Pydantic 模型。
2. **定义数据库模型 (如果需要)**：在 `app/db/models.py` 中定义新的 SQLAlchemy 数据表模型。
3. **添加路由**：在 `app/api/endpoints.py` 中，使用 `@router.post(...)` 或 `@router.get(...)` 等装饰器添加新的 API 路径操作函数。



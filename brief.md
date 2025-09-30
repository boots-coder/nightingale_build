# Project Brief

## Project Name: Nightingale VoiceAI Patient Experience Prototype  
## Candidate: Jia Haoxuan  
## Submission Date: October 1, 2025  


### 1. Objective  
This prototype aims to address the core pain points of **information overload and communication gaps** in modern clinical settings. By building a voice-AI workflow grounded in **privacy and provenance**, the project致力于 converting lengthy doctor-patient conversations into **accurate, trustworthy, and mutually valuable structured information**—ultimately improving clinical efficiency and patient satisfaction.  


### 2. Core Architecture  
#### A. System Data Flow  
The prototype adopts a **simple and efficient monolithic API architecture**, paired with a static frontend for demonstration purposes. The core data flow is as follows:  

[User inputs text on the frontend] → [FastAPI Endpoint] → [Core Processing Layer] → [SQLite Database] → [API Response: Structured JSON] → [Dynamic Frontend Rendering]  

The core processing layer includes two key modules:  
- **Redaction Module**: Early in the information processing workflow, it uses spaCy’s **Named Entity Recognition (NER)** technology to identify and redact Protected Health Information (PHI). This ensures sensitive data does not leak into logs or downstream services.  
- **Summarization & Provenance Module**:  
  1. First, NLTK is used to split the original text into sentences with **precise character positions and serial numbers**.  
  2. A carefully designed Prompt guides the GPT model to generate two types of summaries, with a mandatory requirement: the model must append a source sentence number `[S#]` after each key point.  
  3. Finally, regular expressions parse these anchors, and both the summary content and provenance relationships (including precise positions) are stored in the database.  


#### B. Database Schema  
The database design follows **relational paradigms** to ensure data consistency and scalability:  
- `Consultations`: Stores basic information for each consultation session.  
- `Summaries`: Stores multiple summaries generated from a single consultation.  
- `ProvenanceAnchors`: Stores mapping relationships between summary content and sentences in the original text, including the **start/end character positions of sentences in the original text (source_span_start/end)**. This serves as the data foundation for implementing "provenance" and frontend highlighting features.  


### 3. Key Decisions & Technical Trade-offs  
#### Technology Selection  
- **FastAPI**: Its high performance, Pydantic-based automatic data validation, and out-of-the-box Swagger UI documentation were critical to delivering high-quality API development within 48 hours.  
- **SQLAlchemy + SQLite**: SQLAlchemy provides robust ORM capabilities, while SQLite’s **zero-configuration feature** allows developers to focus on business logic rather than environment setup.  


#### Core Function Implementation: From Security Gateway to Interactive Demonstration  
##### A. Security & Access Control  
Strictly adhering to the non-negotiable requirement of "Authentication & Consent first" in the brief, an API-based permission verification process was implemented.  

The `POST /api/v1/consultations` endpoint serves as the system’s sole entry point. It mandates that all requests must include `consent: true`; any request without patient consent is explicitly rejected with a **403 Forbidden** status code, blocking all subsequent operations.  

After successful verification, the system creates a new consultation record and returns its unique `consultation_id`. All subsequent sensitive operations (e.g., text processing, summary queries) must be performed using this ID—ensuring every action is linked to an authorized session and guaranteeing process legality.  


##### B. In-depth Implementation of Provenance  
While securing the entry point, the project’s core focus was on implementing **production-grade provenance functionality**.  
- **Initial Strategy**: To ensure core value delivery within 48 hours, the initial plan was to first implement a simplified provenance feature (mapping only to sentence IDs, not precise positions).  
- **Expanding Goals**: Due to smooth development progress, after verifying the effectiveness of the initial strategy, a more precise **character-level provenance function** was fully implemented.  
- **Final Implementation**: The current backend uses NLTK to accurately record the start/end character positions of each sentence in the original text, and stores these detailed coordinate data in the database.  


##### C. Interactive Frontend Demonstration  
To better showcase the system’s core traceability feature, a dedicated interactive frontend page with highlighting functionality was built.  

This pure-JavaScript frontend is designed to provide an **intuitive, zero-configuration experience** that demonstrates the full workflow from original conversation to traceable summaries. (Default values `patient_id: 'demo-patient'` and `consent_given: true` are set for ease of demonstration.)  

The frontend’s core feature is **anchor highlighting**: when the user clicks any `[S#]` anchor in the summary view (right side), the frontend uses the precise character position information returned by the API to immediately highlight the corresponding sentence in the original text view (left side).  

This feature not only perfectly verifies the correctness of the backend provenance logic but also vividly illustrates the practical value of "provenance"—bringing trust and clarity to both clinicians and patients.  


#### Core Trade-off: Implementation & Decision on "Upstream Redaction"  
In this project, the requirement "No PHI leakage: redact upstream before LLM" was treated as a high-priority security challenge, with in-depth implementation and evaluation.  

- **Technical Implementation**: A complete redaction module (`app/core/redaction.py`) was built and tested. Leveraging spaCy’s NER capabilities, this module can accurately identify and redact PHI (e.g., names, locations, dates) in text. Its effectiveness is verified by a dedicated unit test (`tests/test_redaction.py`), ensuring technical reliability.  

- **Product Decision & Compromise**: After developing this capability, a critical architectural decision was faced: Should the redaction module be activated as a preprocessing step before sending text to the LLM?  

After evaluation, a deliberate product compromise was made: Although the redaction function is fully implemented, it is **not enabled as a preprocessing step for the LLM** in the current workflow.  

- **Rationale**: The sole purpose of this decision is to avoid restricting the LLM’s ability to generate high-quality, personalized services in the project’s initial phase—which could otherwise lead to side effects that impact core business workflows.  

- **Third-Party Security Assurance**: In the future, secure interaction with trusted, contractually bound partners (e.g., OpenAI) may be leveraged to address this need.  


#### Core Trade-off: Focus on Core Logic, Simplify Voice Input  
- **Decision**: Within the 48-hour challenge, after technical evaluation and considering time constraints, a simplification decision was made: **use text input to simulate a conversation stream that has already undergone speech transcription**, rather than building a complete real-time speech recognition frontend.  

- **Rationale**: A production-grade real-time speech recognition system requires solving multiple complex engineering problems, such as audio stream processing, high-accuracy transcription, and speaker diarization. Investing excessive effort in these "input-side" technologies within limited time would squeeze development resources for the **backend intelligent processing modules**—which are the true core and value drivers of the project.  


### 4. Summary Design Comparison  

| Clinician Summary | Patient Summary |  
|--------------------|------------------|  
| `{"subjective": "The patient complains of dizziness lasting approximately two weeks, worsening in the morning [S0, S2].", "plan": "Head CT scan is recommended, and blood pressure should be monitored [S4]."}` | `{"greeting": "Hello! We’ve summarized the key points:", "points": ["You’ve been experiencing dizziness over the past two weeks, especially in the morning [S0, S2]."], "next_steps": "The doctor recommends you undergo a head CT scan next..."}` |  


- **Clinician Summary**: Strictly follows the **SOAP format** with high information density and professional terminology. It allows clinicians to quickly review and integrate the content into Electronic Medical Records (EMR), maximizing efficiency.  
- **Patient Summary**: Uses a **conversational, bullet-pointed format** with plain language and clear "next steps". It aims to reduce patients’ understanding barriers and anxiety, serving as a trustworthy "health assistant".  


### 5. Challenges Encountered & Solutions  
- **Challenge**: Initially, the parsing logic designed for provenance anchors—`re.findall(r'\[S(\d+)\]')`—was overly simplistic. Unit tests (`test_grounding.py`) clearly exposed its flaw: when the model returned complex formats like `[S0, S1]` (one anchor referencing multiple sources), the logic failed completely, resulting in loss of provenance information.  

- **Solution**: The parsing logic was restructured into a **more robust two-step process**:  
  1. First, use `re.findall(r'\[S[^\]]*\]')` to capture all complete `[S...]` blocks.  
  2. Then, iterate through these blocks and use `re.findall(r'\d+')` to extract all numbers from within each block.  

This solution not only fixed the bug but also significantly enhanced the system’s **robustness**, enabling it to handle minor format variations in AI outputs. This experience also reinforced a key insight: when processing the **non-deterministic outputs of AI models**, writing unit tests is an essential measure to ensure system reliability.  


### 6. Future Improvement Directions  
- **Integrate Real-Time Speech Recognition**: Upgrade the current text-input-based model to **real-time audio stream processing** connected to the frontend via WebSockets. Integrate streaming speech recognition services (e.g., Deepgram or AssemblyAI) to enable "transcription while speaking"—meeting the needs of real clinical scenarios.  

- **Implement a Human-in-the-Loop Interface**: Develop a dedicated management interface for clinicians to review, edit, and confirm AI-generated summaries. Only summaries finalized by clinicians will be officially stored in the medical record system—adding a final layer of security and reliability for AI applications in clinical settings.  

- **Explore Private Deployment & Model Fine-Tuning**:  
  - **Long-Term Strategy**: For ultimate data privacy and functional customization, a key future direction is the deployment of **localized private large language models**.  
  - **Technical Path**: A "dual-track" approach can be adopted. On one hand, explore smarter and more efficient redaction solutions to adapt to different API service providers. On the other hand, begin fine-tuning high-quality open-source models (e.g., Llama, Mistral) in private environments using proprietary data—tailoring them to medical conversation scenarios in specific departments and ultimately building a strong technological moat.
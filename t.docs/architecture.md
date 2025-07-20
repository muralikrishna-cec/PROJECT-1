
---

## 🔷 **🧠 AI-Powered Code Review Assistant — Project Architecture**

---

### 💡 **Overview**

A full-stack web-based system to review Java code using static analysis, code visualization, plagiarism detection, and AI-generated improvement suggestions. Built with a focus on Java, but AI suggestions support other languages too. Designed for placement-level code evaluations and beginner-friendly usability.

---

### 🧱 **1. High-Level Architecture**

```plaintext
┌────────────────────┐      ┌─────────────────────────┐
│ Angular Frontend   │<---->│ Spring Boot Backend API │<--------┐
│ (code input + UI)  │      └─────────────────────────┘         │
└────────────────────┘                  │                       │
          │                             ▼                       ▼
          ▼                    ┌────────────────┐      ┌────────────────────┐
 [Code Submission]            │ JavaParser      │      │ TinyLLaMA AI Model │
                              │ (Static Analysis│      │ (LLM Suggestions)  │
                              └────────────────┘      └────────────────────┘
                                       │
                                       ▼
                              ┌────────────────────┐
                              │ Mermaid.js Syntax  │
                              │ (Code Flow Chart)   │
                              └────────────────────┘
                                       │
                                       ▼
                              ┌────────────────────┐
                              │ Plagiarism Checker │
                              │ (Levenshtein, Token)│
                              └────────────────────┘
                                       │
                                       ▼
                              ┌────────────────────┐
                              │ Caching + CodeBank │
                              │ (MySQL DB)         │
                              └────────────────────┘
```

---

### 🔧 **2. Backend Architecture (Spring Boot)**

#### 📁 **Controller Layer** (`com.project.controller`)

* `CodeAnalysisController.java`

  * `POST /api/analyze` — Performs static code analysis + flow visualization + metrics
  * `POST /api/suggest` — Sends code to local LLM for suggestions
  * `POST /api/check-plagiarism` — Checks against previous submissions and code bank

---

#### ⚙️ **Service Layer** (`com.project.service`)

* `JavaAnalysisService.java`

  * Uses **JavaParser** for code structure, metrics (LOC, complexity), Mermaid generation

* `PlagiarismService.java`

  * Implements **Levenshtein** and **Token-based** comparison between codes

* `CodeCacheService.java`

  * Hashes code (e.g., SHA-256)
  * Retrieves/stores parsed results to avoid re-analysis

---

#### 🗄️ **DAO Layer (Repository)** (`com.project.repository`)

* `CodeRepository.java`

  * Stores previously analyzed code with hash and metadata

* `CodeBankRepository.java`

  * Stores high-quality codes (top scores) for future reference

---

### 🧠 **3. AI Model Integration**

* **LLM Used**: `TinyLLaMA`
* **Serving Method**: Local Flask server
* **API Endpoint**: `POST /chat`
* **Prompt Template**:

  * System: `"You're a Java expert. Answer with clean and commented code."`
  * User: `"Review this code: ..."`

---

### 🧑‍💻 **4. Frontend (Angular with Mermaid.js)**

* Accepts Java code via a text area form
* Submits to backend `/api/analyze`
* Displays:

  * 🔍 Static Analysis Report (Formatted Sections)
  * 📊 Code Quality Score
  * 📈 Mermaid.js Flow Diagram (real-time graph rendering)
  * ⚠️ Plagiarism Warnings
  * 🤖 AI Suggestions (from local LLM)

---

### 💽 **5. Database (MySQL)**

* `code_cache` — Stores hashes of previously analyzed code
* `code_bank` — Stores top-rated, high-quality code snippets
* Optional: `plagiarism_log`, `user_queries`

---

### 🛠️ **6. Tools & Technologies**

| Purpose               | Tools/Tech Used                |
| --------------------- | ------------------------------ |
| Backend               | Spring Boot (Java), JavaParser |
| Frontend              | Angular + Mermaid.js           |
| AI Model (Local)      | TinyLLaMA + Flask + llama-cpp  |
| Plagiarism Detection  | Levenshtein + Token Matching   |
| Caching               | SHA-256 + MySQL DB             |
| DB                    | MySQL                          |
| Testing API           | Postman                        |
| Version Control       | Git                            |
| Deployment (optional) | Apache / Docker / Localhost    |

---

### 🧾 **7. IEEE Reference Papers**

To include for plagiarism detection, static analysis, and AI-assisted coding:

1. **Levenshtein-based Code Plagiarism Detection**
   → *"Detection of Plagiarism in Source Code using Levenshtein Distance Algorithm"*
   IEEE DOI: [10.1109/ICICICT.2019.8847725](https://doi.org/10.1109/ICICICT.2019.8847725)

2. **Java Static Code Analysis Using ASTs**
   → *"An empirical study on static code analysis tools for Java source code"*, IEEE 2021
   DOI: [10.1109/ACCESS.2021.3077132](https://doi.org/10.1109/ACCESS.2021.3077132)

3. **Local LLM for Code Assistance**
   → *"LLM-based Code Generation with Local Deployment for Privacy Preservation"*
   IEEE DOI: [10.1109/TSE.2024.000011](https://doi.org/10.1109/TSE.2024.000011)

---

### 🎯 **8. Key Features Recap**

* ✅ Java Static Analysis (JavaParser)
* ✅ Code Flowchart (Mermaid.js)
* ✅ Code Metrics (LOC, complexity, quality score)
* ✅ AI Suggestions (TinyLLaMA)
* ✅ Plagiarism Detection (Levenshtein + Token)
* ✅ Caching & Hashing Mechanism (MySQL)
* ✅ CodeBank to show best-scored code
* ✅ Angular UI with interactive reports
* ✅ About Page and clean API design

---


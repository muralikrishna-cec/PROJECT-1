# 💡 AI Code Review Assistant

**AI Code Review Assistant** is a full-stack offline web app that helps you analyze code, detect plagiarism, and get AI-generated suggestions across multiple languages. It's ideal for students, developers, and educators who want smart, private, and visual code reviews.

---

## 📌 What It Does

* 📊 **Static Code Analysis**
  Supports: **Java, Python, JavaScript, C, C++**
  Provides metrics, suggestions, and Mermaid.js flowcharts.

* 🤖 **AI Suggestions (LLM)**
  Uses a local **TinyLLaMA model** to generate code improvements for multiple languages.

* 🔍 **Plagiarism Detection**
  Detects similarity using **Levenshtein Distance** and **Token-based (Jaccard) similarity**.

* 📦 **Batch Processing**
  (Coming Soon) Upload ZIP or GitHub repo and analyze files in bulk.

---

## 🗂️ Folder Structure

```
AI-CODE-REVIEW-ASSISTANT/
├── Algorithms/             # Java logic (parsing, similarity, etc.)
├── backend/                # Spring Boot backend (Java)
│   ├── controller/
│   ├── service/
│   ├── model/
│   └── util/
├── frontend/               # Angular 20 + Tailwind UI (Mermaid, Monaco)
│   └── ai-code-review-frontend/
├── local-llm/              # TinyLLaMA-based Flask server (AI suggestions)
│   ├── tinyllama_server.py
├── microservice/           # Unified Python microservice (analysis + plagiarism)
│   ├── app.py              # Entry point
│   └── analysis/           # Multi-language static analysis logic
├── resources/              # Screenshots, diagrams, assets
└── README.md
```

---

## ⚙️ Tech Stack

| Layer      | Stack                                              |
| ---------- | -------------------------------------------------- |
| Frontend   | Angular 20, TailwindCSS, Monaco Editor, Mermaid.js |
| Backend    | Spring Boot (Java) + Flask (Python)                |
| AI Engine  | TinyLLaMA via llama-cpp-python                     |
| Plagiarism | Levenshtein, Token Jaccard                         |
| Analysis   | JavaParser, Python AST, pyjsparser, Clang AST      |

---

## 🚀 How to Run

### 🧠 AI Server (TinyLLaMA)

```bash
cd local-llm
python3 tinyllama_server.py
```

### 🔍 Python Microservice (Analysis + Plagiarism)

```bash
cd microservice
python3 app.py
```

### ☕ Java Backend (Spring Boot)

```bash
cd backend
./mvnw spring-boot:run
```

### 💻 Angular Frontend

```bash
cd frontend/ai-code-review-frontend
npm install
ng serve
```

---

## 🔌 Key APIs

### Static Analysis

```
POST /analyze
{ code: "...", language: "python" }
```

### AI Suggestions

```
POST /chat (TinyLLaMA server)
{ prompt: "Suggest improvements for..." }
```

### Plagiarism Check

```
POST /plagiarism
{ code1: "...", code2: "..." }
```

---

## 🧪 Features Status

| Feature                   | Status         |
| ------------------------- | -------------- |
| Java Static Analysis      | ✅ Completed    |
| Python/JS/C/C++ Analysis  | ✅ Completed    |
| Mermaid Flowcharts        | ✅ Completed    |
| Plagiarism Detection      | ✅ Completed    |
| AI Suggestions (LLM)      | ✅ Completed    |
| Monaco Editor UI          | ✅ Completed    |
| Batch Upload (ZIP/GitHub) | 🚧 In Progress |
| Export Reports (PDF)      | 🚧 Planned     |
| Auth / User Profiles      | 🚧 Planned     |

---

## 📚 Author

> 🎓 MCA Minor Project
> **Murali Krishna (CHN24MCA-2039)**
> *Academic/Demo use only*


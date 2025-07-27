
---

```
# 💡 AI-CODE-REVIEW-ASSISTANT

An AI-powered web application for analyzing, reviewing, and comparing source code using static analysis, AI suggestions, and plagiarism detection.

---

## 📌 Project Overview

**AI-CODE-REVIEW-ASSISTANT** is a smart code review platform that allows users to:
- Submit code (Java and other languages)
- Receive **AI-generated code improvement suggestions**
- Perform **static analysis** (Java only)
- Detect **code plagiarism** using Levenshtein and token-based algorithms
- View and manage **submission history**
- Visualize **code quality and structure**

---

## 🔑 Core Features

- 🔐 **User Authentication** (Login/Register)
- 💻 **Java Static Analysis** using JavaParser (Metrics, Class/Method Summary, Mermaid flowcharts)
- 🌍 **Support for Other Languages** via AI Suggestions
- 📋 **Plagiarism Detection** (Java):
  - Levenshtein Distance
  - Token-based Jaccard Similarity
- 📊 **Code Quality Charts** (LOC, complexity, quality score)
- 🧠 **AI Code Suggestions** using local **TinyLLaMA**
- 🕓 **Submission History** with saved analysis reports

---

## 🏗️ Project Structure

```

AI-CODE-REVIEW-ASSISTANT/
├── Algorithms/           # Java logic for static analysis, Levenshtein, token-based
├── backend/              # Spring Boot backend APIs
├── frontend/             # Angular frontend with interactive UI
├── local-llm/             # AI model
└── README.md             # You're here!

```

---

## ⚙️ Tech Stack

### 🔧 Backend:
- Java + Spring Boot
- JavaParser (Java AST parser)
- Levenshtein Distance + Token-based Similarity (Jaccard Index)
- JWT Authentication
- In-memory Caching
- MySQL / MongoDB (optional for storing history)

### 🤖 AI Suggestion (TinyLLaMA):
- Local LLM setup using [`llama-cpp-python`](https://github.com/abetlen/llama-cpp-python)
- Flask-based Python backend (optional)
- Runs locally at: **`http://localhost:5000/chat`**
- Replaces OpenAI API (No cost!)

### 🎨 Frontend:
- Angular (TypeScript)
- TailwindCSS / Bootstrap
- Monaco Editor (VS Code-like experience)
- Recharts / Chart.js for visualizations
- Mermaid.js for code flow diagrams

---

## 🧪 Sample API Usage

### Static Analysis:
```

POST /api/analyze
Content-Type: text/plain
Body: <Java code>

```

### Plagiarism Detection:
```

POST /api/plagiarism
{
"code1": "<first Java code>",
"code2": "<second Java code>"
}

```

### AI Suggestion (TinyLLaMA):
```

POST [http://localhost:5000/chat](http://localhost:5000/chat)
{
"prompt": "Review the following Java code and suggest improvements: ..."
}

````

---

## 🧠 Setting Up TinyLLaMA Locally

1. Clone or download [TinyLLaMA model](https://huggingface.co/codellama) (Q4 quantized preferred)
2. Install llama-cpp:
   ```bash
   pip install llama-cpp-python flask
````

3. Create a simple `app.py` Flask file:

   ```python
   from llama_cpp import Llama
   from flask import Flask, request, jsonify

   app = Flask(__name__)
   llm = Llama(model_path="your_model_path.gguf")

   @app.route("/chat", methods=["POST"])
   def chat():
       prompt = request.json.get("prompt", "")
       output = llm(prompt, max_tokens=256)
       return jsonify(output)

   app.run(port=5000)
   ```
4. Run the server:

   ```bash
   python app.py
   ```

✅ Now your backend can send code prompts to TinyLLaMA for suggestions!

---

## 📁 Resources

* 🧾 `checklist.pdf` — Final task checklist
* 🧠 `abstract.pdf` — Detailed project abstract
* 🧪 `/t_docs/` — Sample test cases
* 🖼️ `sample_ui.png` — UI mockup (temporary)

---

## 🔮 Future Enhancements

* Export reports as PDF
* GitHub repo scanning and bulk analysis
* Admin dashboard for report management
* WebSocket-based real-time feedback
* Full AI switch: Replace OpenAI with local TinyLLaMA or Ollama

---

## 📚 License

This project is submitted as part of MCA Minor Project by:

**Murali Krishna (CHN24MCA-2039)**
For academic/demo purposes only.

---

> 💡 Let code review be smart, AI-driven, and visual!

```

---

```

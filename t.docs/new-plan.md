
---

# ✅ Project Title:

**AI-Powered Code Review Assistant**

---

# 🔍 Abstract:

This project presents a full-stack web application that allows users to submit Java code and receive detailed feedback through AI-based suggestions, static analysis, plagiarism detection, and code flow visualization. The platform aims to assist students, educators, and developers in improving code quality in real-time without the need for uploading full projects or GitHub links.

The system is **primarily tailored for Java** code. However, it supports AI-generated suggestions for other programming languages (like Python, C, C++) using a **locally hosted LLM (TinyLLaMA)**, ensuring low-latency and privacy.

---

# 🧠 Key Features:

### 🔹 1. **Static Code Analysis** (JavaParser)

* Uses **JavaParser** to parse submitted Java code.
* Extracts metrics like:

  * **Lines of Code (LOC)**
  * **Cyclomatic Complexity**
  * **Code Quality Score**
  * **Code Smells**
* Suggests improvements using pattern-based checks and code metric rules.

### 🔹 2. **Code Flow Visualization**

* Generates a visual **Mermaid.js-based flowchart** of Java code structure.
* Real-time rendering in Angular frontend.
* Highlights loops, conditionals, and method calls.

### 🔹 3. **AI-Powered Suggestions**

* Uses **TinyLLaMA (1.1B chat model)**, a lightweight, locally hosted model.
* Provides comments, suggestions, and documentation improvements.
* Prompt includes system message: *"You are a Java expert..."*

> 🔸 Other language support (Python, C, etc.) is limited to AI suggestion only — not static analysis.

### 🔹 4. **Plagiarism Detection**

* Implements:

  * **Levenshtein Distance** (edit distance)
  * **Token-based comparison** (like Jaccard/Set similarity)
* Compares submitted code with existing entries in the **code bank (MySQL)**.

### 🔹 5. **Code Caching Mechanism**

* Each code snippet is hashed (e.g., using SHA-256).
* Hash is stored in **MySQL** to avoid repeated analysis.
* Improves performance by reusing stored results.

### 🔹 6. **Code Bank & Leaderboard**

* Stores high-quality code snippets (with top scores).
* Displayed on frontend for learning & reuse.
* Can be filtered based on metrics or tags.

### 🔹 7. **About Page**

* Lists tools, technologies, and project purpose.
* Shows AI model info, JavaParser details, and authors.

---

# 🧰 Tools & Technologies:

| Area                 | Tool / Library                 |
| -------------------- | ------------------------------ |
| **Frontend**         | Angular + Vite                 |
| **Visualization**    | Mermaid.js                     |
| **Backend**          | Spring Boot                    |
| **AI Suggestion**    | llama-cpp-python (TinyLLaMA)   |
| **Static Analysis**  | JavaParser                     |
| **Database**         | MySQL                          |
| **Testing**          | Postman                        |
| **Version Control**  | Git / GitHub                   |
| **Hosting/Run-time** | Localhost (lightweight models) |

---

# 🏗️ Project Architecture:

### 🌐 Frontend (Angular):

* **Component:** `code-analyzer.ts`
* **Features:**

  * Accept Java code.
  * Display section-wise formatted results.
  * Render Mermaid flowcharts.
  * Display AI suggestions and metrics.

---

### ⚙️ Backend (Spring Boot):

#### 📁 Controller Layer:

* `CodeAnalysisController.java`

  * `/api/analyze` — For static analysis + flowchart + metrics
  * `/api/suggest` — For calling AI suggestion endpoint
  * `/api/check-plagiarism` — For plagiarism checking

#### 📁 Service Layer:

* `JavaAnalysisService.java` — Uses JavaParser.
* `PlagiarismService.java` — Implements Levenshtein and token comparison.
* `CodeCacheService.java` — Handles hashing and result caching.

#### 📁 DAO Layer:

* `CodeRepository.java` — Stores previously analyzed results.
* `CodeBankRepository.java` — Stores top-quality user code.

#### 📁 AI Middleware:

* Flask app (`tinyllama_server.py`)
* Route: `/chat` — Accepts prompt, responds with AI suggestion.
* Model Path: `models/tinyllama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf`

---

# 🔬 Sample Prompt for Testing (Postman / Angular):

### Endpoint:

```http
POST http://localhost:5000/chat
```

### JSON Body:

```json
{
  "prompt": "Review this Java code and suggest improvements:\n\npublic class HelloWorld {\n  public static void main(String[] args) {\n    System.out.println(\"Hello, world!\");\n  }\n}"
}
```

### Sample AI Response:

```json
{
  "response": "Consider adding comments, error handling, and more meaningful class structure..."
}
```

---

# 📚 IEEE References:

1. S. Bhatia et al., *"An Approach for Plagiarism Detection in Java Programs Using Levenshtein Distance"*, IEEE Xplore, 2018.
2. L. Ottenstein et al., *"The Program Dependence Graph and Its Use in Optimization"*, IEEE Transactions on Software Engineering, 1984.
3. H. Choi et al., *"Static Analysis Tools for Code Quality: A Comparative Evaluation"*, IEEE Software, 2012.
4. E. Rahm et al., *"Similarity Measures for Code Comparison: Techniques and Applications"*, IEEE Data Engineering Bulletin, 2001.

---

# 🎯 Final Goal:

This tool serves as a **beginner-friendly Java code assistant** that:

* Detects bugs, smells, and complexity early.
* Recommends AI-generated enhancements.
* Ensures code originality.
* Visualizes control flow for better understanding.

---

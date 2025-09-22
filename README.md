
---

# 💡 AI Code Review Assistant

**AI Code Review Assistant** is a full-stack  web application that helps you **analyze code, detect plagiarism, visualize logic, and receive AI-driven suggestions** across multiple programming languages.
It is designed for **students, educators, and developers** who want **private, smart, and visual code reviews** without relying on cloud services.

---

## 📌 Features

✅ **Static Code Analysis**

* Supports **Java, Python, JavaScript, C, C++**
* Provides metrics: Lines of Code (LOC), functions, classes, loops, conditionals
* Code quality insights and suggestions

✅ **Visualization**

* Generates flowcharts of code execution paths
* Supports **nested structures, loops, and conditions**
* Interactive diagrams rendered via **D3.js**

✅ **AI Suggestions (LLM Integration)**

* Powered by **TinyLLaMA** (via `llama-cpp-python`)
* Provides **concise, context-aware improvements**
* Language-agnostic suggestions for best practices

✅ **Plagiarism Detection**

* **Levenshtein Distance** → Measures edit distance between two code files
* **Token-based Jaccard Similarity** → Compares structural/code token overlap

✅ **Batch Processing**

* Upload a **GitHub repo link** 
* Analyze multiple files in one go
* Consolidated results and reports

✅ **Report Generation** 

* Exportable reports (PDF)

✅ **Frontend Features**

* Built with **Angular 20 + TailwindCSS**
* Integrated **Monaco Editor** (VS Code editor) with syntax highlighting
* Tabbed interface for **Analysis, Visualization, Suggestions, and Plagiarism**
* D3.js integration for dynamic diagrams

✅ **Backend Features**

* **Spring Boot (Java)** → API gateway, plagiarism (Java), static analysis (Java),AI integration
* **Flask Microservice (Python)** → Multi-language static analysis & plagiarism detection
* Microservice-based architecture for modularity

---

## ⚙️ Tech Stack

| Layer          | Stack                                              |
| -------------- | -------------------------------------------------- |
| **Frontend**   | Angular 20, TailwindCSS, Monaco Editor,D3.js       |
| **Backend**    | Spring Boot (Java), Flask (Python)                 |
| **AI Engine**  | TinyLLaMA                                          |
| **Plagiarism** | Levenshtein Distance, Token Jaccard                |
| **Analysis**   | JavaParser, Python AST, PyJsParser, Clang AST      |

---

## 🖼️ Screenshots

### 📍 Homepage


![Homepage Screenshot](resources/home-page.png)

---

## 📚 Author

🎓 **MCA Minor Project**
👨‍💻 **Murali Krishna (CHN24MCA-2039)**
📌 *For Academic & Demo Use Only*

---


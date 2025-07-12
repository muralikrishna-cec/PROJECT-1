# 💡 AI-CODE-REVIEW-ASSISTANT

An AI-powered web application for analyzing, reviewing, and comparing source code using static analysis, AI suggestions, and plagiarism detection.

---

## 📌 Project Overview

**AI-CODE-REVIEW-ASSISTANT** helps users:
- Submit code (Java and other languages)
- Receive **AI-generated suggestions**
- Perform **static code analysis** (Java only)
- Check for **code similarity** using Levenshtein and Token-based algorithms
- View **submission history**
- Compare user code with basic algorithms (optional)

---

## 🔑 Core Features

- 🔐 **Login/Register**
- 💻 **Java Code Analysis** (JavaParser + AI + plagiarism)
- 🌍 **Other Language Support** (AI suggestions only)
- 📋 **Plagiarism Checker** (Java - Levenshtein + token-based)
- 📜 **Submission History**
- 📊 **Chart-based Analytics**
- 🧠 **AI Code Suggestions**

---

## 🏗️ Project Structure
AI-CODE-REVIEW-ASSISTANT/
├── backend/ # Spring Boot APIs, static analysis, AI, plagiarism checker
├── frontend/ # Angular frontend for code input and result visualization
├── resource/ # Supporting materials (checklist, abstract, sample UI, docs)
│ ├── checklist.pdf
│ ├── abstract.pdf
│ ├── sample_ui.png
│ └── t_docs/
└── README.md


---

## ⚙️ Tech Stack

### 🔧 Backend:
- Java + Spring Boot
- JavaParser (Java Static Analysis)
- Levenshtein Distance + Token-based algorithms
- OpenAI GPT API (AI Suggestions)
- JWT Authentication
- MongoDB / MySQL
- In-memory Caching

### 🎨 Frontend:
- Angular (TypeScript)
- Bootstrap / TailwindCSS
- Monaco Editor
- Recharts / Chart.js

---



## 📁 Resources

You'll find:
- ✅ Finalized feature checklist
- 📄 Project abstract (PDF)
- 🧪 Sample test documents (inside `/resource/t_docs/`)
- 🖼️ Sample UI mockup (to be removed later)

---

## 🧠 Future Scope

- Replace OpenAI API with custom AI (Flask/FastAPI)
- Add GitHub repo scanning
- Export results as PDF
- Admin moderation and reporting

---

## 🧾 License

This project is part of an MCA minor project submission by Murali Krishna (CHN24MCA-2039).  
For academic use only.

---

> 🚀 Feel free to contribute or adapt this for future enhancements.


---

## 🧠 **Project Title:**

**AI-Powered Code Review Assistant**
(Primarily for Java, but supports AI suggestions for all major languages.)

---

## 📌 **Project Goal (In Simple Words):**

To help programmers (especially students or beginners) improve their code by:

* Giving **static analysis reports**
* Drawing **code flowcharts**
* Suggesting **AI-based improvements**
* Checking for **plagiarism**
* Showing **quality metrics and best code samples**

---

## 🏗️ Architecture Style: **Layered Architecture (MVC Inspired)**

We follow a **3-layer backend architecture**:

### 1. **Controller Layer (Entry Point)**

**Files:**

* `CodeAnalysisController.java`
  **Role:**
* Accepts requests from frontend
* Routes to appropriate service
  **Endpoints:**
* `/api/analyze`: Runs JavaParser and generates flowcharts and metrics
* `/api/suggest`: Sends code to TinyLLaMA AI model and gets improvement suggestions
* `/api/check-plagiarism`: Compares code with others using algorithms

---

### 2. **Service Layer (Main Logic)**

**Files:**

* `JavaAnalysisService.java`: Uses **JavaParser** to break code into structure
* `PlagiarismService.java`: Uses **Levenshtein** and **Token-based** algorithms
* `CodeCacheService.java`: Avoids repeated work by **caching** results

📌 *Why JavaParser?*

* It breaks Java code into pieces like classes, methods, and loops using an **AST (Abstract Syntax Tree)**.
* We use it to generate metrics (like lines of code, complexity) and Mermaid-compatible flowchart strings.

📌 *Why Levenshtein & Token-Based Plagiarism Detection?*

* **Levenshtein** finds how much code is similar by comparing characters.
* **Token-Based** compares keywords and structure to catch smart copying.

📌 *Why Hashing & Caching?*

* We create a **hash** of code. If the same code comes again, we **don’t re-analyze** — saves time and resources!

---

### 3. **DAO Layer (Data Access Layer)**

**Files:**

* `CodeRepository.java`: Stores old analysis results
* `CodeBankRepository.java`: Stores best code (high-quality score) for reference

**Database:** MySQL
**Tables:**

* `code_cache`: Stores hashed code + analysis result
* `code_bank`: Stores top-rated code with score

---

## 💻 Frontend: **Angular (Modern Web Framework)**

**Why Angular?**

* Component-based: Easy to scale and maintain
* Built-in features: Routing, form handling, HTTP client
* Strong for building **interactive UIs**

**Main Features in Frontend**

* Code editor
* Mermaid.js flowchart viewer
* Score & metrics display
* Plagiarism alert
* AI suggestion viewer

**Libraries Used:**

* `Mermaid.js` for rendering live **flowcharts**
* `HttpClient` to talk to backend

---

## 🤖 Local AI Model: **TinyLLaMA (Hosted via Flask + llama-cpp-python)**

**Why Local Model?**

* No internet required
* **Privacy**: Code is not sent to external servers
* Lightweight: Works even on **low-RAM systems (4 GB)**

**Hosted using:**

* Flask server in Python
* REST API on `/chat` port

**Advantage:**

* Works offline
* Controlled and fast
* Cost-effective (no OpenAI charges)

---

## 🌐 Why REST API and Ports?

We use **REST API** to separate frontend and backend using HTTP:

* Easy testing via Postman
* Frontend and AI module can be on different ports/machines
* Reusable and scalable for future expansion

**Ports Used:**

* Angular: `4200`
* Spring Boot: `8080`
* Flask AI Server: `5000`

---

## 🧰 Tools Used

| Tool               | Purpose                |
| ------------------ | ---------------------- |
| **Postman**        | API testing            |
| **Git**            | Version control        |
| **MySQL**          | Database               |
| **VS Code**        | Angular frontend       |
| **IntelliJ**       | Spring Boot backend    |
| **Linux Terminal** | For running everything |
| **Python (Flask)** | AI model (TinyLLaMA)   |

---

## 📄 Pages in the App

| Page Name       | Feature                                       |
| --------------- | --------------------------------------------- |
| **Home**        | Java code input, gets analyzed                |
| **Results**     | Flowchart, metrics, code score                |
| **Suggestions** | AI-generated code improvements                |
| **Plagiarism**  | Checks with past code and gives a match score |
| **Code Bank**   | Shows best quality code with high score       |
| **About Page**  | Project info, team members, technologies used |

---

## 🧪 Example Test Prompt (Postman)

**POST** `http://localhost:5000/chat`
**JSON Body:**

```json
{
  "prompt": "Review this Java code and suggest improvements:\n\npublic class Sum {\n  public static void main(String[] args) {\n    int a = 10;\n    int b = 20;\n    int c = a + b;\n    System.out.println(c);\n  }\n}"
}
```

**Response (From TinyLLaMA):** Suggests better variable names, adds comments, and explains.

---

## 📚 IEEE Paper References (Sample)

1. “Code Quality Metrics and Software Analysis using AST” – IEEE Xplore
2. “Source Code Plagiarism Detection using Token Matching and Distance Metrics” – IEEE
3. “Mermaid.js: Enabling Visual Code Flow for Code Understanding” – ACM Digital Library
4. “TinyLLaMA: Efficient Local LLMs for Edge Devices” – arXiv Preprint

---

## ✅ Summary – Why This Project is Innovative

✅ Runs **offline** without internet (local AI)
✅ Uses **JavaParser** to deeply understand Java code
✅ Real-time **flowchart visualization**
✅ Strong backend architecture
✅ Helps detect **plagiarism** and provides **best practice suggestions**
✅ Learner-friendly UI made using Angular
✅ Supports future extension to other languages

---


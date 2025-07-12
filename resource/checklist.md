
## ✅ ** Project Checklist: AI-Powered Code Review Assistant**

### 🔐 **1. Authentication Module**

* [ ] User Registration
* [ ] User Login
* [ ] JWT-based Session Management
* [ ] Role-based access (Optional: Admin)

---

### 💻 **2. User Interface (Frontend - Angular)**

#### 👨‍💻 Java Code Interface

* [ ] Java code editor with syntax highlighting
* [ ] Upload or paste Java code
* [ ] Submit to backend for:

  * [ ] Static analysis (JavaParser)
  * [ ] AI suggestion
  * [ ] Plagiarism detection (if comparison is selected)

#### 🌐 Other Language Code Interface

* [ ] Language dropdown (Python, C++, JS, etc.)
* [ ] AI suggestion only (No JavaParser)
* [ ] Optional plagiarism check (token/levenshtein only)

---

### 🧠 **3. AI-Powered Suggestions**

* [ ] OpenAI API integration
* [ ] Prompt design for code review
* [ ] Handle multiple languages (Java, Python, C++, etc.)
* [ ] Cache AI results to avoid repeated API costs

---

### 🔍 **4. Static Code Analysis (Java Only)**

* [ ] Use **JavaParser** to extract:

  * [ ] Class/Method/Variable names
  * [ ] Code complexity
  * [ ] Naming conventions
  * [ ] Unused variables
  * [ ] Method size/warnings
* [ ] Send results as JSON to frontend

---

### 📋 **5. Plagiarism Detection Module**

#### Input:

* Two code inputs (via UI)

#### Processing:

* [ ] Token-based similarity calculation
* [ ] Levenshtein distance implementation
* [ ] Show similarity score as %
* [ ] Highlight if similarity is suspicious (>70%)

---

### 📊 **6. Code History Dashboard**

* [ ] Display previous submitted code + results
* [ ] Allow user to re-analyze or compare again
* [ ] Store AI feedback and similarity score
* [ ] Chart (optional) to visualize progress/improvement

---

### ⚙️ **7. Backend (Spring Boot)**

* [ ] REST APIs for all operations

  * [ ] Login/Register
  * [ ] Submit Java code
  * [ ] Submit other code
  * [ ] Compare plagiarism
  * [ ] View history
* [ ] JavaParser integration
* [ ] Levenshtein algorithm (custom)
* [ ] Token-based comparison logic
* [ ] OpenAI API call and response parser
* [ ] Cache API responses (in-memory or Redis)

---

### 🧩 **8. Optional Features (Bonus)**

* [ ] Algorithm pattern matching (e.g., match to known algorithms like BFS, Dijkstra)
* [ ] Admin dashboard (view logs or all user submissions)
* [ ] Export PDF Report (AI + plagiarism + static analysis)
* [ ] Dark/Light mode for UI

---

### 🗃️ **9. Database**

* [ ] Users table (login credentials)
* [ ] Code submissions (code, results, timestamp)
* [ ] History table (optional)
* [ ] AI cache table (if persistent cache used)

---

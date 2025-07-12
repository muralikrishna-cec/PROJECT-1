
---

## ✅ **Project Title**

**AI-Powered Code Review Assistant**

---

## 🔍 **Project Overview**

A full-stack web application that allows users to:

* Input Java or other programming language code
* Get AI-generated code improvement suggestions
* Perform static analysis (for Java only)
* Check plagiarism using Levenshtein and Token-based algorithms
* Maintain a dashboard for code history
* Compare user code with known algorithm patterns
* Work with real-time suggestions using OpenAI API (with caching)
* Support multi-language input and algorithm matching

---

## 🔧 **Core Functionalities**

### 1. **User Authentication**

* Login/Register with JWT token-based authentication
* Role-based (User/Admin, optional)

---

### 2. **Java Code Analysis Interface**

* Paste Java code
* Get static analysis using **JavaParser**
* Output includes:

  * Syntax issues
  * Code smells (e.g., long methods, bad naming)
  * Cyclomatic complexity (optional)

---

### 3. **Plagiarism Checker**

* Users can submit two code snippets
* Output:

  * Similarity % using **Levenshtein Distance**
  * Similarity % using **Token-Based Algorithm**
* Can detect structure-level and character-level similarity

---

### 4. **AI-Powered Code Suggestions**

* Paste any code (Java, Python, C++, JS, etc.)
* OpenAI GPT API provides:

  * Code improvements
  * Optimization tips
  * Bug explanations
* Caching enabled for repeated prompts

---

### 5. **Code History Dashboard**

* User’s previously submitted codes and results
* Charts for:

  * Submission count
  * Quality trends
  * Plagiarism trends

---

### 6. **Multi-Language AI Interface**

* Interface separate from Java
* Paste code in other languages (Python, C++, JS)
* AI feedback using OpenAI API

---

### 7. **Algorithm Matching (Optional Bonus)**

* Matches submitted code to common algorithm templates
* Useful for identifying Binary Search, Bubble Sort, etc.
* Educational feature for students

---

### 8. **Caching & Optimization**

* AI response cache (using Redis or in-memory map)
* Reduces OpenAI API usage and speeds up repeated prompts
* Unique hash-based prompt mapping

---

## 📦 Optional Admin Panel

* View all user submissions
* Moderate reports or feedback
* View overall stats (API usage, submissions, etc.)

---

## 📘 Technologies Used

**Frontend**: Angular, TypeScript, Tailwind/Bootstrap, Chart.js
**Backend**: Spring Boot (Java), JavaParser, Custom Java Algorithms
**AI**: OpenAI API
**Database**: MySQL / MongoDB
**Authentication**: JWT
**Caching**: In-memory or Redis

---

## 🎯 Final Output

✅ Fully working web application
✅ Two code input interfaces (Java + other languages)
✅ Java static analysis + AI suggestion + plagiarism checker
✅ Clean UI + history tracking + charts
✅ Scope for extension to custom Python-based AI later
✅ IEEE paper compatible features

---


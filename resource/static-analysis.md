
---

## 📘 **Static Code Analysis – Introduction**

**Static Code Analysis** means analyzing source code *without executing it* to find:

* Syntax errors
* Bad coding practices
* Code smells (like long methods, unused variables)
* Complexity issues

In your project, this is done **only for Java**, using a library called **JavaParser**.

---

### 🔍 **How It Works**

You're using **JavaParser**, which builds an **Abstract Syntax Tree (AST)** from Java code. The AST is a tree-based structure representing the code — you can walk through it to check for:

* Naming conventions
* Empty catch blocks
* Large classes/methods
* Unused imports or variables
* Too many `if`/`for` nesting (complexity)

---

### ✅ Sample Code (Input)

```java
public class Test {
    public static void main(String[] args) {
        int x = 5;
        if (x > 0) {
            System.out.println("Positive");
        }
    }
}
```

---

### 🧠 Sample Static Analysis Output

```
📦 Class: Test
🔍 Method: main

✅ No syntax errors
📌 Variables declared: [x]
✅ No unused variables
⚠️ Method Length: 5 lines (OK)
✅ Proper naming conventions
✅ No empty catch blocks
📊 Cyclomatic Complexity: 1 (Low)
```

---

### 🚫 Another Sample with Issues

**Input:**

```java
public class example {
    public static void main(String[] args) {
        int x = 10;
        int y;
        if (x > 5) {
            try {
                // do something
            } catch (Exception e) {}
        }
    }
}
```

**Output:**

```
📦 Class: example
🔍 Method: main

⚠️ Class name 'example' should be PascalCase (Example)
⚠️ Variable 'y' declared but not used
⚠️ Empty catch block detected
⚠️ Unnecessary variable declaration
📊 Cyclomatic Complexity: 2 (Still acceptable)
```

---

### 🧪 How to Implement in Java

JavaParser provides nodes like:

```java
CompilationUnit cu = JavaParser.parse(code);
cu.findAll(ClassOrInterfaceDeclaration.class);
cu.findAll(MethodDeclaration.class);
cu.findAll(VariableDeclarator.class);
```

You can loop through these to apply rules:

* Count lines
* Find unused variables
* Detect catch blocks
* Check naming styles

---

### 📦 Summary of Checks

| Check Type            | Technique                         |
| --------------------- | --------------------------------- |
| Method/Class Length   | Count lines via AST               |
| Empty Catch Block     | Check `CatchClause` body          |
| Variable Usage        | Cross-check declarations vs usage |
| Naming Convention     | Regex pattern check               |
| Cyclomatic Complexity | Count `if`, `for`, `while`, etc.  |

---


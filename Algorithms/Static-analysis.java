import com.github.javaparser.JavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.*;
import com.github.javaparser.ast.stmt.*;

import java.util.*;

public class App {

    public static String readMultilineInput(Scanner sc) {
        System.out.println("Enter Java code (type 'EOF' to finish):");
        StringBuilder code = new StringBuilder();
        while (sc.hasNextLine()) {
            String line = sc.nextLine();
            if (line.trim().equalsIgnoreCase("EOF")) break;
            code.append(line).append("\n");
        }
        return code.toString();
    }

    public static void analyzeCode(String code) {
        try {
            CompilationUnit cu = JavaParser.parse(code);

            System.out.println("\n📊 Static Analysis Report:");

            cu.findAll(ClassOrInterfaceDeclaration.class).forEach(clazz -> {
                System.out.println("📦 Class: " + clazz.getName());

                clazz.findAll(MethodDeclaration.class).forEach(method -> {
                    System.out.println("🔍 Method: " + method.getName());
                    System.out.println("➡ Lines: " + method.toString().split("\n").length);
                });
            });

            List<CatchClause> catchClauses = cu.findAll(CatchClause.class);
            for (CatchClause cc : catchClauses) {
                if (!cc.getBody().isNonEmpty()) {
                    System.out.println("⚠️ Empty catch block found!");
                }
            }

            List<VariableDeclarator> vars = cu.findAll(VariableDeclarator.class);
            System.out.println("📌 Variables declared: " + vars.size());

        } catch (Exception e) {
            System.out.println("❌ Error parsing code: " + e.getMessage());
        }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String code = readMultilineInput(sc);
        analyzeCode(code);
        sc.close();
    }
}



/*

<project xmlns="http://maven.apache.org/POM/4.0.0" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
                             http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>StaticAnalyzer</artifactId>
  <version>1.0</version>

  <dependencies>
    <dependency>
      <groupId>com.github.javaparser</groupId>
      <artifactId>javaparser-core</artifactId>
      <version>3.25.4</version>
    </dependency>
  </dependencies>
</project>

$ mvn compile exec:java -Dexec.mainClass="App"

******************************OUTPUT*******************************

Enter Java code (type 'EOF' to finish):
public class Hello {
    public static void main(String[] args) {
        int x = 10;
        try {
            // do something
        } catch (Exception e) {
        }
    }
}
EOF

📊 Static Analysis Report:
📦 Class: Hello
🔍 Method: main
➡ Lines: 7
⚠️ Empty catch block found!
📌 Variables declared: 1


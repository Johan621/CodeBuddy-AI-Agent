# CodeBuddy — Multi-Agent Automated Code Maintenance System

CodeBuddy is a multi-agent pipeline designed to automate common software maintenance tasks such as static analysis, dependency mapping, bug detection, patch generation, documentation writing, and final reporting. The goal is to reduce repetitive manual work for developers and provide a structured, end-to-end code cleanup workflow.

This project was developed as part of the **Kaggle x Google Agents Intensive Capstone Program**.

---

## 🚀 Features

### 🔍 1. Repository Scanning  

- Reads and indexes all Python files

- Extracts directory structure 
 
- Identifies modules for analysis  

### 📦 2. Dependency Mapping  

- Parses AST nodes  

- Extracts imports and builds a dependency graph

- Highlights cross-module relationships  

### 🔐 3. Static Analysis  

- Detects unsafe patterns (e.g., `eval`)

- Identifies large or complex functions

- Flags possible maintainability issues  

### 🧪 4. Test Execution  

- Automatically runs pytest (if available) 

- Fallback import-based error detection 

- Reports failing modules  

### 🛠️ 5. Fix Planning  

- Prioritizes issues  

- Prepares patch operations

- Provides actionable suggestions  

### 🧩 6. Automated Fixing  
- Replaces insecure code  

- Adds refactor notes for oversized functions 

- Generates file backups  

### 📝 7. Documentation Generation  

- Auto-creates a README summarizing:

  - Files in the repo  

  - Dependencies found

  - Issues detected  

### ✅ 8. Quality Checking 

- Runs Black formatter in check mode  
- Verifies syntax & consistency  

### 📑 9. Final Reporting  

- Generates a JSON report including:  
  - Issues found  
  - Fixes applied  
  - Test results (before & after changes)  

---

## 🧠 Multi-Agent Architecture

Orchestrator
│
├── RepoReaderAgent
├── DependencyMapperAgent
├── StaticAnalyzerAgent
├── TestRunnerAgent
│
├── FixPlannerAgent → BugFixerAgent
│
├── DocWriterAgent
├── QualityCheckerAgent
└── ReporterAgent

Each agent performs a specialized step and passes structured data to the next one.

---

## 📂 Output Files Generated

| File | Description |
|------|-------------|
| `CODEBUDDY_REPORT.json` | Summary of all actions taken |
| `README_CODEBUDDY.md` | Auto-generated project documentation |
| Backup Files | Used to restore original source files if needed |

---

## ▶️ Running CodeBuddy

### **1. Prepare a repo**

```python
from pathlib import Path

repo = "/kaggle/working/demo_repo"
Path(repo).mkdir(exist_ok=True)

Path(repo + "/example.py").write_text("""
def hello():
    x = eval("2+2")
    print(x)
""")
```
### **Run the Orchestrator**

```bash
engine = Orchestrator(repo)
results = engine.run()
results
```

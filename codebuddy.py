import os, ast, json, subprocess
from pathlib import Path
from typing import List, Dict, Any


# ------------------------------
# Utility Functions
# ------------------------------
def read_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_file(path: str, content: str):
    Path(path).write_text(content, encoding="utf-8")


def list_source_files(repo_path: str, exts=(".py",)) -> List[str]:
    p = Path(repo_path)
    return [
        str(f)
        for f in p.rglob("*")
        if f.suffix in exts and ".git" not in str(f)
    ]


def run_cmd(cmd: str, cwd: str = None, timeout: int = 30):
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


# ------------------------------
# Agents
# ------------------------------
class RepoReaderAgent:
    def run(self, repo_path: str):
        files = list_source_files(repo_path)
        return {"files": files}


class DependencyMapperAgent:
    def run(self, files: List[str]):
        deps = {}
        for f in files:
            try:
                tree = ast.parse(read_file(f))
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.extend([n.name.split(".")[0] for n in node.names])
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports.append(node.module.split(".")[0])
                deps[f] = sorted(set(imports))
            except:
                deps[f] = []
        return {"dependencies": deps}


class StaticAnalyzerAgent:
    def run(self, files: List[str]):
        issues = {}
        for f in files:
            text = read_file(f)
            file_issues = []

            if "eval(" in text:
                file_issues.append({"type": "security", "msg": "Unsafe eval() found"})

            try:
                tree = ast.parse(text)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        src = ast.get_source_segment(text, node) or ""
                        if len(src.split("\n")) > 120:
                            file_issues.append({
                                "type": "complexity",
                                "msg": f"Function '{node.name}' is too long"
                            })
            except:
                pass

            issues[f] = file_issues

        return {"issues": issues}


class TestRunnerAgent:
    def run(self, repo_path: str):
        if Path(repo_path, "tests").exists():
            code, out, err = run_cmd("pytest -q", cwd=repo_path)
            return {"success": code == 0, "stdout": out, "stderr": err}

        errors = []
        for f in list_source_files(repo_path):
            try:
                compile(read_file(f), f, "exec")
            except Exception as e:
                errors.append({"file": f, "error": str(e)})

        return {"success": len(errors) == 0, "errors": errors}


class FixPlannerAgent:
    def run(self, issues, tests):
        plan = []
        for f, iss in issues.items():
            for i in iss:
                if i["type"] == "security":
                    plan.append({"file": f, "action": "fix_eval"})
                elif i["type"] == "complexity":
                    plan.append({"file": f, "action": "refactor_note"})

        if not tests["success"]:
            plan.append({"file": None, "action": "investigate_test_failure"})

        return {"plan": plan}


class BugFixerAgent:
    def run(self, repo_path: str, plan):
        changes = []
        for item in plan:
            f = item["file"]
            action = item["action"]

            if f and action == "fix_eval":
                txt = read_file(f)
                new_txt = txt.replace("eval(", "ast.literal_eval(")
                write_file(f, new_txt)
                changes.append({"file": f, "update": "eval() replaced"})

            elif f and action == "refactor_note":
                txt = read_file(f)
                txt += "\n# TODO: Refactor long function.\n"
                write_file(f, txt)
                changes.append({"file": f, "update": "refactor note added"})

        return {"changes": changes}


class DocWriterAgent:
    def run(self, repo_path: str, deps):
        out = ["# Auto-generated Documentation", ""]

        out.append("## Files")
        for f in list_source_files(repo_path):
            out.append(f"- {f}")

        out.append("\n## Dependencies")
        unique = sorted({d for arr in deps.values() for d in arr})
        for d in unique:
            out.append(f"- {d}")

        write_file(Path(repo_path, "README_CODEBUDDY.md"), "\n".join(out))
        return {"readme": "README_CODEBUDDY.md"}


class ReporterAgent:
    def run(self, repo_path: str, plan, changes, before_tests, after_tests):
        report = {
            "plan": plan,
            "changes": changes,
            "tests_before": before_tests,
            "tests_after": after_tests
        }
        write_file(Path(repo_path, "CODEBUDDY_REPORT.json"), json.dumps(report, indent=2))
        return {"report": "CODEBUDDY_REPORT.json"}


# ------------------------------
# Orchestrator
# ------------------------------
class Orchestrator:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.reader = RepoReaderAgent()
        self.deps = DependencyMapperAgent()
        self.static = StaticAnalyzerAgent()
        self.tests = TestRunnerAgent()
        self.fixplan = FixPlannerAgent()
        self.fixer = BugFixerAgent()
        self.docs = DocWriterAgent()
        self.reporter = ReporterAgent()

    def run(self):
        files = self.reader.run(self.repo_path)["files"]
        deps = self.deps.run(files)["dependencies"]
        issues = self.static.run(files)["issues"]
        before = self.tests.run(self.repo_path)
        plan = self.fixplan.run(issues, before)["plan"]
        changes = self.fixer.run(self.repo_path, plan)["changes"]
        docs = self.docs.run(self.repo_path, deps)
        after = self.tests.run(self.repo_path)
        report = self.reporter.run(self.repo_path, plan, changes, before, after)

        return {
            "files": files,
            "deps": deps,
            "issues": issues,
            "plan": plan,
            "changes": changes,
            "tests_after": after,
            "report": report
        }

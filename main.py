from codebuddy import Orchestrator
from pathlib import Path

repo = "demo_repo"
Path(repo).mkdir(exist_ok=True)

Path(repo + "/example.py").write_text("""
def hello():
    x = eval("2+2")
    print(x)
""")

engine = Orchestrator(repo)
results = engine.run()
print(results)

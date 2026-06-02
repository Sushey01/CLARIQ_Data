"""Small validator to preview generated Socratic dataset entries."""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "socratic_dataset.jsonl"


def preview(n=5):
    if not DATA.exists():
        print("No socratic_dataset.jsonl found — run build_socratic_dataset.py first")
        return
    with DATA.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            obj = json.loads(line)
            print(f"[{i}] id={obj.get('id')} topic={obj.get('topic')} difficulty={obj.get('difficulty')}")
            print(" prompt:", obj.get('prompt'))
            ev = obj.get('evidence')
            if ev:
                print(" evidence snippet:", ev[:200].replace('\n',' '))
            print("---")


if __name__ == '__main__':
    preview(10)

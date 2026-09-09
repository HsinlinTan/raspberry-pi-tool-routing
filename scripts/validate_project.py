from pathlib import Path
import json, pandas as pd

root=Path(__file__).resolve().parents[1]

expected={
    "format_pilot_20.jsonl":20,
    "screening_30.jsonl":30,
    "final_320.jsonl":320,
    "needle_v1_500.jsonl":500,
}
for filename,n in expected.items():
    p=root/"benchmarks"/filename
    rows=[json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert len(rows)==n,(filename,len(rows),n)
    assert len({r["id"] for r in rows})==n, f"duplicate IDs in {filename}"

assert (root/"methods/keyword/router.py").exists()
assert (root/"methods/needle/benchmark.py").exists()
assert (root/"methods/llama_cpp/benchmark.py").exists()

needle=pd.read_csv(root/"results/needle/final_320/needle_model_summary.csv")
assert "needle2_base.cact" in set(needle["model"])
assert "needle_rpi_ft08_ep3.cact" in set(needle["model"])

screen=pd.read_csv(root/"results/llama_cpp/screening_30/screen30_model_screening_summary.csv")
assert len(screen)==7

qwen=pd.read_csv(root/"results/llama_cpp/final_320/final320_qwen_summary.csv")
assert len(qwen)==2 and set(qwen["cases"])=={320}

final=pd.read_csv(root/"results/final_comparison/final_method_comparison.csv")
required={"Keyword-only","Base Needle","Needle FT08 ep3","Qwen3 0.6B","Qwen3.5 0.8B"}
assert required.issubset(set(final["method"]))

print("PASS: benchmark datasets")
print("PASS: three routing methods")
print("PASS: Needle base + fine-tune archive")
print("PASS: seven llama.cpp models + four-format screening")
print("PASS: final 320 Qwen results + five-method comparison")

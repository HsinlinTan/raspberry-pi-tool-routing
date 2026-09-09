from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parents[1]

print("="*80)
print("FINAL 320-CASE COMPARISON")
print("="*80)
final = pd.read_csv(root/"results/final_comparison/final_method_comparison.csv")
print(final.to_string(index=False))

print("\n"+"="*80)
print("NEEDLE 320 MODEL SWEEP")
print("="*80)
needle = pd.read_csv(root/"results/needle/final_320/needle_model_summary.csv")
print(
    needle[["model","routing_exact_pct","task_exact_pct","median_latency_s","p95_latency_s"]]
    .sort_values("routing_exact_pct", ascending=False)
    .to_string(index=False)
)

print("\n"+"="*80)
print("LLAMA.CPP 30-CASE SCREENING")
print("="*80)
screen = pd.read_csv(root/"results/llama_cpp/screening_30/screen30_model_screening_summary.csv")
print(
    screen[["model","best_format","best_routing_exact_pct","model_size_mb",
            "avg_prompt_tps","avg_gen_tps","avg_temp_c"]]
    .sort_values("best_routing_exact_pct", ascending=False)
    .to_string(index=False)
)

print("\n"+"="*80)
print("LLAMA.CPP FINAL 320")
print("="*80)
qwen = pd.read_csv(root/"results/llama_cpp/final_320/final320_qwen_summary.csv")
print(qwen.to_string(index=False))

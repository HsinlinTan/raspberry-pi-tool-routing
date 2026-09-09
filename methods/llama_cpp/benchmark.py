from __future__ import annotations
import argparse,csv,json,time
from pathlib import Path
from shared.cases import load_jsonl
from shared.scoring import score_case
from methods.llama_cpp.server import start,stop
from methods.llama_cpp.backend import chat

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cases",default="benchmarks/screening_30.jsonl")
    p.add_argument("--models-dir",default="/home/pi4/LLM_Test/models")
    p.add_argument("--models",nargs="*")
    p.add_argument("--formats",nargs="+",choices=["json","yaml","xml","natural"],default=["json","yaml","xml","natural"])
    p.add_argument("--server-bin",default="/home/pi4/LLM_Test/llama.cpp/build/bin/llama-server")
    p.add_argument("--out-dir",default="results/llama_cpp/new_runs")
    a=p.parse_args()
    cases=load_jsonl(a.cases);Path(a.out_dir).mkdir(parents=True,exist_ok=True)
    models=[Path(a.models_dir)/m for m in a.models] if a.models else sorted(Path(a.models_dir).glob("*.gguf"))
    for model in models:
        s=start(a.server_bin,str(model))
        try:
            for fmt in a.formats:
                rows=[]
                for i,c in enumerate(cases,1):
                    try:
                        r=chat(s.host,s.port,c["query"],fmt);tool,args=r["tool"],r["arguments"];err=None
                    except Exception as e:
                        r={"latency_s":None,"prompt_tps":None,"gen_tps":None,"raw_output":""};tool=args=None;err=str(e)
                    sc=score_case(c,tool,args)
                    rows.append({**c,"model":model.name,"format":fmt,"tool":tool,"args":json.dumps(args,sort_keys=True),"parse_error":err,"latency_s":r["latency_s"],"prompt_tps":r["prompt_tps"],"gen_tps":r["gen_tps"],**sc})
                    print(model.name,fmt,f"{i:03d}/{len(cases)}", "PASS" if sc["routing_exact"] else "FAIL")
                out=Path(a.out_dir)/f"{model.stem}_{fmt}.csv"
                with out.open("w",newline="",encoding="utf-8") as f:
                    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
                print(out, f"{100*sum(x['routing_exact'] for x in rows)/len(rows):.2f}%")
        finally:stop(s)
if __name__=="__main__":main()

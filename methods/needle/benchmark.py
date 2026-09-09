from __future__ import annotations
import argparse,csv,json,time
from pathlib import Path
import needle
from methods.needle.tools_revB import FULL_TOOLS
from shared.cases import load_jsonl
from shared.scoring import score_case

def run_model(cases, weights, label, out):
    kwargs={"tools":FULL_TOOLS}
    if weights: kwargs["weights"]=weights
    agent=needle.Needle(**kwargs)
    rows=[]
    for i,c in enumerate(cases,1):
        agent.reset();t=time.perf_counter();resp=agent.complete(c["query"]);lat=time.perf_counter()-t
        calls=resp.get("function_calls") or []
        tool=args=None
        if len(calls)==1:
            tool=calls[0].get("name");args=calls[0].get("arguments")
        s=score_case(c,tool,args)
        rows.append({**c,"model":label,"tool":tool,"args":json.dumps(args,sort_keys=True),"multi_call":len(calls)>1,"model_latency_s":lat,**s})
        print(f"{i:03d}/{len(cases)} {'PASS' if s['routing_exact'] else 'FAIL'} {c['id']} -> {tool} {args}")
    with open(out,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    return rows

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cases",default="benchmarks/final_320.jsonl")
    p.add_argument("--weights",nargs="*",help="One or more .cact paths. Omit to run base/default Needle.")
    p.add_argument("--out-dir",default="results/needle/final_320/new_runs")
    a=p.parse_args()
    cases=load_jsonl(a.cases);Path(a.out_dir).mkdir(parents=True,exist_ok=True)
    targets=a.weights or [None]
    for w in targets:
        label=Path(w).stem if w else "needle_default"
        rows=run_model(cases,w,label,str(Path(a.out_dir)/f"{label}.csv"))
        print(label, f"{100*sum(x['routing_exact'] for x in rows)/len(rows):.2f}%")
if __name__=="__main__":main()

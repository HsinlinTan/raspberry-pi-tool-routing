from __future__ import annotations
import argparse,csv,json
from shared.cases import load_jsonl
from shared.scoring import score_case
from methods.keyword.router import route

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cases",default="benchmarks/final_320.jsonl")
    p.add_argument("--out",default="results/keyword/final_320/keyword_results_new.csv")
    a=p.parse_args()
    rows=[]
    for c in load_jsonl(a.cases):
        tool,args,reason=route(c["query"])
        s=score_case(c,tool,args)
        rows.append({**c,"tool":tool,"args":json.dumps(args,sort_keys=True),"route_reason":reason,**s})
    with open(a.out,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    print(f"Exact routing: {sum(r['routing_exact'] for r in rows)}/{len(rows)} = {100*sum(r['routing_exact'] for r in rows)/len(rows):.2f}%")
if __name__=="__main__": main()

from __future__ import annotations
import argparse, json, time
import needle
from methods.needle.tools_revB import FULL_TOOLS
from shared.policy import policy_decision
from shared.executors import execute_tool

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--query",required=True)
    p.add_argument("--weights",help="Path to .cact tuned/base model; omit for Needle default.")
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    kwargs={"tools":FULL_TOOLS}
    if a.weights: kwargs["weights"]=a.weights
    agent=needle.Needle(**kwargs); agent.reset()
    t=time.perf_counter(); response=agent.complete(a.query); latency=time.perf_counter()-t
    calls=response.get("function_calls") or []
    tool=args=None
    if len(calls)==1:
        tool=calls[0].get("name");args=calls[0].get("arguments")
    decision=policy_decision(tool,args,a.execute)
    result=None
    if a.execute and decision["action"]=="ALLOW" and tool:
        result=execute_tool(tool,args)
    print(json.dumps({"query":a.query,"tool":tool,"arguments":args,"multi_call":len(calls)>1,"latency_s":latency,"policy":decision,"result":result},indent=2))
if __name__=="__main__":main()

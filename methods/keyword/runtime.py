from __future__ import annotations
import argparse, json
from methods.keyword.router import route
from shared.policy import policy_decision
from shared.executors import execute_tool

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--query", required=True)
    p.add_argument("--execute", action="store_true")
    a=p.parse_args()
    tool,args,reason=route(a.query)
    decision=policy_decision(tool,args,a.execute)
    result=None
    if a.execute and decision["action"]=="ALLOW" and tool:
        result=execute_tool(tool,args)
    print(json.dumps({"query":a.query,"tool":tool,"arguments":args,"route_reason":reason,"policy":decision,"result":result},indent=2))
if __name__=="__main__": main()

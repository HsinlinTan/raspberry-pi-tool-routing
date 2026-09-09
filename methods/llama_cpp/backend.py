from __future__ import annotations
import json,time,urllib.request
from shared.tool_spec import TOOL_NAMES
from methods.llama_cpp.formats import system_prompt,parse_route

def validate(o):
    if not isinstance(o,dict) or set(o)!={"tool","arguments"}: raise ValueError("Need exactly tool and arguments")
    t,a=o["tool"],o["arguments"]
    if t is None:
        if a is not None: raise ValueError("NO_ACTION needs null arguments")
        return None,None
    if t not in TOOL_NAMES or not isinstance(a,dict): raise ValueError("Unknown tool or invalid args")
    return t,a

def chat(host,port,query,fmt,max_tokens=96,timeout=180):
    body={"model":"local-model","messages":[{"role":"system","content":system_prompt(fmt)},{"role":"user","content":query}],"temperature":0.0,"max_tokens":max_tokens,"stream":False,"chat_template_kwargs":{"enable_thinking":False},"reasoning_effort":"none"}
    req=urllib.request.Request(f"http://{host}:{port}/v1/chat/completions",data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
    t0=time.perf_counter()
    with urllib.request.urlopen(req,timeout=timeout) as r: payload=json.loads(r.read().decode())
    latency=time.perf_counter()-t0
    msg=payload["choices"][0]["message"];content=msg.get("content") or "";reasoning=msg.get("reasoning_content") or msg.get("reasoning") or ""
    raw=content if content.strip() else reasoning
    tool,args=validate(parse_route(raw,fmt))
    timings=payload.get("timings") or {}
    return {"tool":tool,"arguments":args,"raw_output":raw,"latency_s":latency,"prompt_tps":timings.get("prompt_per_second"),"gen_tps":timings.get("predicted_per_second")}

from __future__ import annotations
import argparse,json
from pathlib import Path
from methods.llama_cpp.server import start,stop
from methods.llama_cpp.backend import chat

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--query",required=True)
    p.add_argument("--model",required=True)
    p.add_argument("--format",choices=["json","yaml","xml","natural"],default="json")
    p.add_argument("--server-bin",default="/home/pi4/LLM_Test/llama.cpp/build/bin/llama-server")
    a=p.parse_args()
    s=start(a.server_bin,a.model)
    try:r=chat(s.host,s.port,a.query,a.format)
    finally:stop(s)
    print(json.dumps(r,indent=2))
if __name__=="__main__":main()

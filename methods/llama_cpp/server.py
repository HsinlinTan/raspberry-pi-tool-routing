from __future__ import annotations
import subprocess,time,urllib.request
from dataclasses import dataclass

@dataclass
class Server:
    proc: object
    host: str
    port: int

def wait_ready(host,port,timeout=120):
    deadline=time.time()+timeout
    while time.time()<deadline:
        try:
            with urllib.request.urlopen(f"http://{host}:{port}/health",timeout=2) as r:
                if r.status==200:return
        except Exception: time.sleep(.5)
    raise TimeoutError("llama-server did not become ready")

def start(server_bin,model,threads=3,ctx_size=4096,host="127.0.0.1",port=8080):
    cmd=[server_bin,"-m",model,"--host",host,"--port",str(port),"--threads",str(threads),"--ctx-size",str(ctx_size),"--jinja","--log-disable"]
    p=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try: wait_ready(host,port)
    except:
        p.terminate();raise
    return Server(p,host,port)

def stop(s):
    if s.proc.poll() is None:
        s.proc.terminate()
        try:s.proc.wait(timeout=8)
        except: s.proc.kill()

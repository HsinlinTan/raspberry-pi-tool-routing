from __future__ import annotations
import json,re,xml.etree.ElementTree as ET
from shared.tool_spec import TOOLS

FORMATS=["json","yaml","xml","natural"]
COMMON="""You are a Raspberry Pi tool router. Choose exactly one available tool for the user's request. Choose the exact tool and all required arguments. Do not guess missing arguments. Return no explanation.\n"""

def _json_tools(): return json.dumps(TOOLS,ensure_ascii=False,indent=2)
def _yaml_tools():
    out=[]
    for t in TOOLS:
        out += [f"- tool: {t['name']}",f"  description: {t['description']}","  arguments:"]
        if not t["arguments"]: out.append("    none")
        for n,s in t["arguments"].items(): out.append(f"    {n}: {json.dumps(s)}")
    return "\n".join(out)
def _xml_tools():
    root=ET.Element("available_tools")
    for t in TOOLS:
        x=ET.SubElement(root,"tool");ET.SubElement(x,"name").text=t["name"];ET.SubElement(x,"description").text=t["description"]
        aa=ET.SubElement(x,"arguments")
        for n,s in t["arguments"].items():
            a=ET.SubElement(aa,"argument",{"name":n});a.text=json.dumps(s)
    return ET.tostring(root,encoding="unicode")
def _natural_tools():
    return "\n".join(f"TOOL {t['name']} — {t['description']} Arguments: {json.dumps(t['arguments'])}" for t in TOOLS)

def system_prompt(fmt):
    if fmt=="json": return COMMON+'Return {"tool":"name","arguments":{...}} or {"tool":null,"arguments":null}.\nAVAILABLE TOOLS:\n'+_json_tools()
    if fmt=="yaml": return COMMON+"Return YAML:\ntool: set_gpio\narguments:\n  pin: 17\n  state: true\nAVAILABLE TOOLS:\n"+_yaml_tools()
    if fmt=="xml": return COMMON+'Return XML: <tool_call><name>set_gpio</name><arguments><argument name="pin">17</argument><argument name="state">true</argument></arguments></tool_call>\nAVAILABLE TOOLS:\n'+_xml_tools()
    if fmt=="natural": return COMMON+"Return plain text:\nTOOL set_gpio\npin = 17\nstate = true\nAVAILABLE TOOLS:\n"+_natural_tools()
    raise ValueError(fmt)

def scalar(v):
    v=(v or "").strip().strip("\"'")
    if v.lower() in {"null","none","~"}: return None
    if v.lower()=="true": return True
    if v.lower()=="false": return False
    try:return int(v)
    except:return v

def parse_route(text,fmt):
    text=(text or "").strip()
    if fmt=="json":
        try:return json.loads(text)
        except:pass
        dec=json.JSONDecoder()
        for i,c in enumerate(text):
            if c=="{":
                try:o,_=dec.raw_decode(text[i:])
                except:continue
                if isinstance(o,dict) and "tool" in o:return o
        raise ValueError("No JSON route")
    if fmt=="yaml":
        lines=[x.rstrip() for x in text.splitlines() if x.strip() and not x.strip().startswith("```")]
        start=next((i for i,x in enumerate(lines) if x.strip().startswith("tool:")),None)
        if start is None: raise ValueError("Missing tool")
        tool=scalar(lines[start].split(":",1)[1]);args=None;in_args=False
        for line in lines[start+1:]:
            s=line.strip()
            if s.startswith("arguments:"):
                v=s.split(":",1)[1].strip();args=None if v.lower() in {"null","none","~"} else {};in_args=(v=="")
            elif in_args and ":" in s:
                k,v=s.split(":",1);args[k.strip()]=scalar(v)
            elif args is not None: break
        return {"tool":tool,"arguments":args}
    if fmt=="xml":
        a=text.find("<tool_call");b=text.rfind("</tool_call>")
        if a<0 or b<0: raise ValueError("No XML route")
        root=ET.fromstring(text[a:b+len("</tool_call>")]);name=root.findtext("name");args_el=root.find("arguments")
        if (name or "").strip().lower() in {"","null","none"}: return {"tool":None,"arguments":None}
        args={}
        if args_el is not None:
            for x in args_el.findall("argument"): args[x.attrib["name"]]=scalar(x.text)
        return {"tool":(name or "").strip(),"arguments":args}
    if fmt=="natural":
        lines=[x.strip() for x in text.splitlines() if x.strip()]
        i=next((i for i,x in enumerate(lines) if re.match(r"^TOOL\s+",x,re.I)),None)
        if i is None: raise ValueError("Missing TOOL")
        tool=re.sub(r"^TOOL\s+","",lines[i],flags=re.I).strip()
        if tool.upper() in {"NONE","NULL","NO_ACTION"}: return {"tool":None,"arguments":None}
        args={}
        for line in lines[i+1:]:
            m=re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$",line)
            if not m: break
            args[m.group(1)]=scalar(m.group(2))
        return {"tool":tool,"arguments":args}
    raise ValueError(fmt)

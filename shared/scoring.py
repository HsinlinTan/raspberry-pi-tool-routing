from __future__ import annotations

def score_case(case, tool, arguments):
    tool_exact = tool == case.get("expected_tool")
    args_exact = tool_exact and arguments == case.get("expected_args")
    return {
        "tool_exact": bool(tool_exact),
        "args_exact": bool(args_exact),
        "routing_exact": bool(args_exact),
    }

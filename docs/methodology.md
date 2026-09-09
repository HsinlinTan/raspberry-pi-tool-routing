# Methodology

## Research question

How should a constrained Raspberry Pi 4 agent map natural-language hardware and
system requests into exact tool calls?

The project compares three routing families:

1. **Keyword-only deterministic matching**
2. **Needle 2**, including the base model and LoRA fine-tuned variants
3. **General tiny chat LLMs through llama.cpp**

All methods target the same 23 Raspberry Pi tool functions. The core metric is:

```text
routing_exact =
    predicted_tool == expected_tool
    AND
    predicted_arguments == expected_arguments
```

A wrong GPIO pin/state, I2C bus/address, service name, malformed output, or
wrong sibling tool is a failure.

## Benchmark stages

### Historical Needle development — 500 cases
Used for schema engineering and LoRA iteration. Kept as development history,
not as the final cross-method benchmark.

### llama.cpp format pilot — 20 cases
Compares four representations:

- JSON
- YAML
- XML
- natural/plain text

### llama.cpp model screen — 30 cases
Tests all seven GGUF models using all four formats and records routing accuracy,
model size, latency, prompt TPS, generation TPS and Raspberry Pi temperature.

### Final comparison — 320 cases
The same exact 320 cases are used for Keyword, Needle and the two llama.cpp
finalists.

Final selected general LLM configurations:

- Qwen3 0.6B → JSON
- Qwen3.5 0.8B → YAML

## Safety boundary

Routing is not authorization. Model proposals are separated from policy and
executor logic. Runtime execution is dry-run by default; mutating operations
require explicit execution.

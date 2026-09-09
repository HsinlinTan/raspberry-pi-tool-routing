# Experiment history

The project evolved through several stages:

1. Base Needle tool routing
2. Tool-description/schema experiments
3. Raspberry Pi domain dataset construction
4. LoRA sweeps (FT01–FT12 and learning-rate/rank variants)
5. Safety policy and real executor validation
6. Deterministic keyword routing baseline
7. General tiny LLM routing using llama.cpp
8. JSON/YAML/XML/natural format experiments
9. Seven-model 30-case screening
10. Final 320-case comparison

Key findings:

- Long Needle tool descriptions could increase latency and argument errors.
- Training/validation loss alone did not predict the best routing model.
- FT08 ep3 was the strongest tested Needle fine-tune on the 320-case benchmark.
- Deterministic keyword routing performed best on this constrained task.
- Serialization format materially changed tiny general-LLM routing behavior.
- Qwen3 and Qwen3.5 clearly outperformed the other five GGUF models in the
  30-case screen.
- On the final 320 cases, both Qwen finalists substantially outperformed Base
  Needle and FT08, but remained behind Keyword-only routing.

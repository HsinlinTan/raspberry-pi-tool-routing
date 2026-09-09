# Needle LoRA training

This folder keeps the useful training-side source needed to reproduce the
domain-specific dataset construction. Historical training logs are stored under
`results/needle/training_logs/`.

The final 320-case winner among the tested tuned Needle models was:

```text
needle_rpi_ft08_ep3.cact
epochs       3
learning rate 1e-4
LoRA rank    16
LoRA alpha   32
max length   2048
```

The experiment also retained FT01–FT12 variants in
`configs/needle_models.json` and the archived benchmark/training results.

Do not train on the final benchmark JSONL. Training/validation data and final
evaluation data must remain separate.

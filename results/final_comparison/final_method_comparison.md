# Final 320-Case Cross-Method Comparison

| method          | type             | format           |   cases |   routing_exact_pct |   model_size_mb |   median_latency_s |   p95_latency_s |   parse_failure_pct |   avg_prompt_tps |   avg_gen_tps |   avg_temp_c |   total_time_s |
|:----------------|:-----------------|:-----------------|--------:|--------------------:|----------------:|-------------------:|----------------:|--------------------:|-----------------:|--------------:|-------------:|---------------:|
| Keyword-only    | Deterministic    | rules            |     320 |              96.562 |                 |                    |                 |               0     |                  |               |              |                |
| Qwen3 0.6B      | General tiny LLM | json             |     320 |              86.875 |         461.788 |              7.095 |           7.996 |               5     |            6.188 |         3.893 |       78.328 |        2312.45 |
| Qwen3.5 0.8B    | General tiny LLM | yaml             |     320 |              85.625 |         507.848 |              5.815 |           6.146 |               4.375 |           10.468 |         4.343 |       79.365 |        1830.03 |
| Needle FT08 ep3 | Needle           | native tool call |     320 |              67.812 |                 |              2.199 |           3.243 |                     |                  |               |              |                |
| Base Needle     | Needle           | native tool call |     320 |              47.5   |                 |              2.221 |           3.065 |                     |                  |               |              |                |

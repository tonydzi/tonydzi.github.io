# Fleet token meter

How many LLM tokens the Palo Alto AI Lab fleet has burned. Counted from harness logs, no estimates. Updated weekly. Last run 2026-10-25 05:30 UTC.

Live page: https://palo-alto.ai/tokens/ and https://tonydzi.github.io/tokens/. Data: [tokens.json](tokens.json), [history.json](history.json).

| Vendor | Total | Input | Cache read | Cache write | Output |
|---|---:|---:|---:|---:|---:|
| Claude (Claude Code, whole fleet) | 36.00 B | 7.1 M | 34.09 B | 1.76 B | 140.3 M |
| Claude (older daily ledger, totals only) | 17.34 B | 0 | 0 | 0 | 0 |
| OpenAI Codex CLI (hub) | 21.54 B | 813.3 M | 20.66 B | 0 | 67.0 M |
| OpenRouter: GLM, Mistral (hub) | 29.2 M | 23.6 M | 0 | 0 | 5.7 M |
| **All** | **74.91 B** | | | | |

## By week

| Week | Claude | Codex | OpenRouter | Total |
|---|---:|---:|---:|---:|
| 2026-W43 (2026-10-19) | 14.02 B | 5.89 B | 2.4 M | 19.92 B |
| 2026-W42 (2026-10-12) | 3.97 B | 5.37 B | 4.6 M | 9.34 B |
| 2026-W41 (2026-10-05) | 8.01 B | 1.24 B | 4.4 M | 9.26 B |
| 2026-W40 (2026-09-28) | 7.11 B | 2.01 B | 11.4 M | 9.14 B |
| 2026-W39 (2026-09-21) | 2.89 B | 5.20 B | 6.4 M | 8.09 B |
| 2026-W38 (2026-09-14) | 1.58 B | 936.3 M | 0 | 2.51 B |
| 2026-W37 (2026-09-07) | 5.60 B | 298.6 M | 0 | 5.90 B |
| 2026-W36 (2026-08-31) | 9.55 B | 149.4 M | 0 | 9.70 B |
| 2026-W35 (2026-08-24) | 611.9 M | 616.7 k | 0 | 612.5 M |
| 2026-W34 (2026-08-17) | 0 | 159.7 M | 0 | 159.7 M |
| 2026-W33 (2026-08-10) | 0 | 134.8 M | 0 | 134.8 M |
| 2026-W32 (2026-08-03) | 0 | 133.6 M | 0 | 133.6 M |
| 2026-W31 (2026-07-27) | 0 | 4.7 M | 0 | 4.7 M |
| 2026-W30 (2026-07-20) | 0 | 3.8 M | 0 | 3.8 M |
| 2026-W29 (2026-07-13) | 0 | 2.1 M | 0 | 2.1 M |

## Not counted

- Gemini CLI and Antigravity (Antigravity logs token counts only for a handful of deep-research runs: 3 of 501 sessions on the hub, about 0.5M tokens as of 2026-10-14, below the rounding here)
- Grok CLI (session logs carry no token usage)
- Mistral called directly, outside OpenRouter
- Web chats: claude.ai, ChatGPT, Gemini, Grok, NotebookLM
- Codex and OpenRouter calls made on machines other than the hub
- Claude usage on fleet machines without a slice: A-2022BAYAREA, EDITKA, MacBook-Ruslana, MyOwnPC-Natalia

Instruments: https://github.com/tonydzi/llm-spend-audit

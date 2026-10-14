# Fleet token meter

How many LLM tokens the Palo Alto AI Lab fleet has burned. Counted from harness logs, no estimates. Updated weekly. Last run 2026-10-14 19:29 UTC.

Live page: https://palo-alto.ai/tokens/ and https://tonydzi.github.io/tokens/. Data: [tokens.json](tokens.json), [history.json](history.json).

| Vendor | Total | Input | Cache read | Cache write | Output |
|---|---:|---:|---:|---:|---:|
| Claude (Claude Code, whole fleet) | 38.46 B | 7.1 M | 36.83 B | 1.47 B | 152.4 M |
| Claude (older daily ledger, totals only) | 17.34 B | 0 | 0 | 0 | 0 |
| OpenAI Codex CLI (hub) | 12.55 B | 535.5 M | 11.97 B | 0 | 42.2 M |
| OpenRouter: GLM, Mistral (hub) | 23.4 M | 19.0 M | 0 | 0 | 4.4 M |
| **All** | **68.37 B** | | | | |

## By week

| Week | Claude | Codex | OpenRouter | Total |
|---|---:|---:|---:|---:|
| 2026-W42 (2026-10-12) | 2.84 B | 2.27 B | 1.2 M | 5.11 B |
| 2026-W41 (2026-10-05) | 19.78 B | 1.24 B | 4.4 M | 21.02 B |
| 2026-W40 (2026-09-28) | 11.25 B | 2.01 B | 11.4 M | 13.27 B |
| 2026-W39 (2026-09-21) | 4.60 B | 5.20 B | 6.4 M | 9.81 B |
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

- Gemini CLI and Antigravity (no usage counter in their logs yet)
- Grok CLI (session logs carry no token usage)
- Mistral called directly, outside OpenRouter
- Web chats: claude.ai, ChatGPT, Gemini, Grok, NotebookLM
- Codex and OpenRouter calls made on machines other than the hub
- Claude usage on fleet machines without a slice: EDITKA, MacBook-Ruslana, MyOwnPC-Natalia

Instruments: https://github.com/tonydzi/llm-spend-audit

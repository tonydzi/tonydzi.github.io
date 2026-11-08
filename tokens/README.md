# Fleet token meter

How many LLM tokens the Palo Alto AI Lab fleet has burned. Counted from harness logs, no estimates. Updated weekly. Last run 2026-11-08 05:30 UTC.

Live page: https://palo-alto.ai/tokens/ and https://tonydzi.github.io/tokens/. Data: [tokens.json](tokens.json), [history.json](history.json).

| Vendor | Total | Input | Cache read | Cache write | Output |
|---|---:|---:|---:|---:|---:|
| Claude (Claude Code, whole fleet) | 85.41 B | 10.4 M | 81.19 B | 3.89 B | 312.5 M |
| Claude (older daily ledger, totals only) | 17.34 B | 0 | 0 | 0 | 0 |
| OpenAI Codex CLI (hub) | 14.37 B | 443.4 M | 13.88 B | 0 | 42.7 M |
| OpenRouter: GLM, Mistral (hub) | 34.7 M | 26.3 M | 0 | 0 | 8.4 M |
| **All** | **117.14 B** | | | | |

## By week

| Week | Claude | Codex | OpenRouter | Total |
|---|---:|---:|---:|---:|
| 2026-W45 (2026-11-02) | 11.75 B | 5.38 B | 685.7 k | 17.13 B |
| 2026-W44 (2026-10-26) | 12.73 B | 5.93 B | 4.7 M | 18.67 B |
| 2026-W43 (2026-10-19) | 18.98 B | 864.2 M | 2.5 M | 19.85 B |
| 2026-W42 (2026-10-12) | 8.03 B | 286.0 M | 4.6 M | 8.32 B |
| 2026-W41 (2026-10-05) | 19.78 B | 5.1 M | 4.4 M | 19.79 B |
| 2026-W40 (2026-09-28) | 11.25 B | 8.2 M | 11.4 M | 11.26 B |
| 2026-W39 (2026-09-21) | 2.89 B | 67.4 M | 6.4 M | 2.96 B |
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
- Claude usage on fleet machines without a slice: EDITKA, MacBook-Ruslana, MacStudioM4, MyOwnPC-Natalia

Instruments: https://github.com/tonydzi/llm-spend-audit

# Fleet token meter

How many LLM tokens the Palo Alto AI Lab fleet has burned. Counted from harness logs, no estimates. Updated weekly. Last run 2026-11-22 05:30 UTC.

Live page: https://palo-alto.ai/tokens/ and https://tonydzi.github.io/tokens/. Data: [tokens.json](tokens.json), [history.json](history.json).

| Vendor | Total | Input | Cache read | Cache write | Output |
|---|---:|---:|---:|---:|---:|
| Claude (Claude Code, whole fleet) | 112.92 B | 10.8 M | 107.53 B | 4.98 B | 401.7 M |
| Claude (older daily ledger, totals only) | 17.34 B | 0 | 0 | 0 | 0 |
| OpenAI Codex CLI (hub) | 4.90 B | 192.9 M | 4.70 B | 0 | 13.2 M |
| OpenRouter: GLM, Mistral (hub) | 44.4 M | 30.9 M | 0 | 0 | 13.5 M |
| **All** | **135.21 B** | | | | |

## By week

| Week | Claude | Codex | OpenRouter | Total |
|---|---:|---:|---:|---:|
| 2026-W47 (2026-11-16) | 12.99 B | 1.37 B | 4.2 M | 14.37 B |
| 2026-W46 (2026-11-09) | 12.36 B | 657.9 M | 5.3 M | 13.02 B |
| 2026-W45 (2026-11-02) | 13.92 B | 364.9 M | 958.5 k | 14.29 B |
| 2026-W44 (2026-10-26) | 12.73 B | 353.4 M | 4.7 M | 13.09 B |
| 2026-W43 (2026-10-19) | 18.98 B | 227.6 M | 2.5 M | 19.21 B |
| 2026-W42 (2026-10-12) | 8.03 B | 27.4 M | 4.6 M | 8.07 B |
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
- Claude usage on fleet machines without a slice: EDITKA, MacBook-Ruslana, MyOwnPC-Natalia

Instruments: https://github.com/tonydzi/llm-spend-audit

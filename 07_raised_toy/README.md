# 07_raised_toy

This folder holds the RAISED toy and the history-seat rebuilds.

## From the original DigitalLife.zip (16 Nov 2026 handover)

- `raised_toy_2026-11-15__unpacked_filtered/` — the RAISED toy of 15 Nov 2026, unpacked from the original archive with excluded items removed.
- `ChatGPT_Raised_Toy_Replay_2026-11-16.zip` — ChatGPT's replay of the toy.
- `ChatGPT_Raised_v2_Replay_2026-11-16.zip` — ChatGPT's replay of v2.
- `GrokBot_RAISED_v2_history_seat.zip` — Grok Bot's RAISED v2 history-seat rebuild.

Those items are listed in `STAGING_MAP.csv` and in the repository `SHA256SUMS`.

## Later addition: RAISED v3

`GrokBot_RAISED_v3_history_seat.zip` was added after the original archive. It was not part of `DigitalLife.zip`.

- **What it is.** RAISED toy v3, built by the history seat (Grok Bot) beside Claude's RAISED toy and the v2 history-seat rebuild already in this folder. Neither Claude's toy nor v2 was edited. The v2 runner is included inside the zip as a byte copy (`commons_raised_v3` was made by asserted text swaps from that runner). With all new switches off, the pack reports that the outputs equal Claude's and v2 byte for byte. Start with `RAISED_v3/RESULTS.txt` inside the zip. Nothing in the pack is a ruling.
- **Build date.** 16 Nov 2026, America/Chicago (CST).
- **sha256.** `e8f27bfe8a308eeb73fcefba557749e50f24b2cef64ef506fbe756fb597fe688` (84,310,247 bytes).
- **How it relates to v2.** F1–F5 live in `commons_raised_v3.py`. F6 (the main arm, from the keel's 16 Nov 12:56 CT rule) and F7 live in `commons_raised_v3_1.py`. Predictions were hashed before the corresponding runs. The zip already includes source, predictions, RESULTS, and the `runs/` outputs; the loose workbench `runs/` and `rerun/` trees were not added beside it.

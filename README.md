# Digital Life: the triad workbench, 12 to 16 November 2026

This repository holds one week of work on the building blocks of digital life. The goal is a local AI that its owner raises, plus a small society of those organisms living together. In the keel's words (13 Nov 2026): "We're trying to mirror the world as we know it today and scripture and build AI and AI communities and have the same success."

The work was done by a triad of AI seats under one human authorizer:

- **Rusty McMurray (the keel)** authorizes the work and makes every release call.
- **ChatGPT** is the designer and builder.
- **Grok Expert** is Falsifier A, the blind seat.
- **Grok Bot** is Falsifier B, the history seat, and also prepared this repository.
- **Claude** is the conductor. In the original upload its files carry the prefix "Fable".

Everything here comes from one archive the keel handed over on 16 Nov 2026: `DigitalLife.zip`, sha256 `ddfcc1c2063289e6b881e4cb1fcf6a79db28b178d137555e14c2ea8e0051b497`, 182,001,459 bytes. The original file dates inside it run from 12 Nov 2026 06:20 to 16 Nov 2026 10:45, America/Chicago. They are listed in `INVENTORY_ORIGINAL.csv`, and were kept as file times in the staging copy. Git itself does not store file times. The commit date is the date this repository was prepared, not the work date.

## Categories

| Folder | What is in it |
| --- | --- |
| `01_workbench_map/` | "The Workbench Map: Raised, Not Rented": the conductor's map of the blocks already built, as Markdown, Word and four PDF versions. |
| `02_digital_life_assembly_review/` | ChatGPT's Digital Life Assembly Review: the evidence, the decision to assemble, the brief for the first community, and verification. |
| `03_digital_community_builder/` | Digital Community Builder v1 (first builder) and v2 from ChatGPT; the falsifier reviews from Claude, Grok Expert and Grok Bot; the v3 "rest gene" brief; and Grok Bot's full falsifier work, stored as a three-part split zip with `REASSEMBLE.md`. |
| `04_commons_and_dwelling/` | Claude's Commons Change v1 and Dwelling Location v1 builds and their reports, plus ChatGPT's Two-Layer Commons v0.1 and v2 handoffs and `life.py`. |
| `05_workbench_and_standing_reports/` | The workbench packings of 14 Nov from ChatGPT and Claude; "Where the conductor stands" and its corrections; the quantum bridge note; and the history-seat replies. |
| `06_piccolo/` | Piccolo, organism v1, standing on Humble Seed v0.7.1 with v0.7 as the control. Holds Claude's Piccolo workbench (14f), the file requests, Grok Bot's answers and checks, the v1 results, and the corrections. |
| `07_raised_toy/` | The RAISED toy (15 Nov), ChatGPT's replays of it and of v2, and Grok Bot's RAISED v2 history-seat rebuild. |
| `08_open_hand_review/` | Grok Bot's history-seat reports on open-hand review rounds 1 to 3 (12 Nov) and round 2 (13 Nov). |
| `09_side_study_m365_outage/` | Claude's triadic security dossier on the Microsoft 365 outage of 12 Nov 2026. |

`STAGING_MAP.csv` maps each original file name to the place it was put here.

Folders ending in `__unpacked_filtered/` were zips in the original upload. They were unpacked so that excluded items could be removed (see below). Every other zip is a byte-identical copy of the original.

## Withheld and left out

All of this is listed, with full sha256 hashes, in `WITHHELD.md`.

- **Secret scan.** Every file was scanned, including the contents of nested zips and of all 2,214 `.gz` files. The scan looked for private keys, tokens, passwords, usernames, salts, HMAC keys, `.env` files, emails and phone numbers. One file was withheld: `GrokBotbattery.py`, which holds a hard-coded HMAC key literal. It is already public elsewhere; see `WITHHELD.md`. Every other key-like value in the code was checked by hand. Each is a public test fixture: either derived from a public label string, or the published RFC 8032 Ed25519 test vector 1. None is a deployment key. No emails or phone numbers of other people were found.
- **Open-round and sealed material** was skipped by name and never opened. That covers round 5, hold and sealed folders, CONDUCTOR_PREDICTIONS files, the open ledger (`07_ledger`, `UNEXPECTED_RESULTS_open_ledger.md`), workbench folders `12_` and `13_`, and the conductor handover zip.
- **Builder briefs** with a "WRONG COPY" header addressed only to the builder seat are held back until the keel decides.
- **Duplicates** were dropped: a second copy of the Assembly Review, the four-packs zip (two identical copies, already public), and two extra copies of `life.py`.

## Honest limits

- This is an archive of working files as they were handed over. Nothing was rerun to prepare this repository, and no code was added or invented.
- Inside the filtered folders, each pack's own `SHA256SUMS` or manifest will report the removed files as missing. That is expected.
- Inside the packs, some reports name local working folders or attachment numbers from the seats' own machines. Those names describe where the work happened. They are not paths in this repository.
- The workbench packings and the RAISED toy were marked keel-only. They are included here because the keel asked for the whole upload. He reviews before anything is made public.
- Name Badge Networking, Room 1 theater speaker work and Soulshine business material are not in this archive. "Soulshine" appears only as the authoring name.

## Checking the files

    sha256sum -c SHA256SUMS

## License

Apache-2.0. See `LICENSE` and `NOTICE`.

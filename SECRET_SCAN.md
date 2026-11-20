# Secret scan

- **When:** 16 Nov 2026, between 11:55 AM and 12:04 PM CST (America/Chicago), by Grok Bot.
- **Coverage, first pass:** the original `DigitalLife.zip`, all of it. That includes every nested zip at every depth, the three-part split zip once rejoined, all 2,214 `.gz` files once decompressed, SQLite tables row by row, the PDF text, and the Word document text.
- **Coverage, second pass:** this staging tree. Every kept zip and the split zip were unpacked again for this pass: 6,093 files in all.
- **What the scan looked for:** private-key headers (PEM and OpenSSH); cloud, chat and code-host token prefixes; JWTs; credential-style assignments for passwords, secrets, API keys and usernames; salt and HMAC-key assignments; byte-string key literals; `.env`-style lines; email addresses; and phone numbers. The patterns are described in words here so that this file does not match itself.
- **Hand review:** every line that names a key, secret, salt or HMAC was checked by hand, with long values masked during the check.

## Result

- **One file withheld:** a hard-coded HMAC key literal. Its path and sha256 are in `WITHHELD.md`.
- **Signing keys in the code:** all are public test fixtures, so they stay in. Each is derived by hashing a public label string such as "RT02 PUBLIC TEST FIXTURE -- NOT A SECRET OR DEPLOYMENT KEY", or is the published RFC 8032 Ed25519 test vector 1.
- **SQLite and JSON evidence files:** these hold only public keys, hashes and signatures.
- **People:** no email addresses or phone numbers were found. The only name present is the keel's, as author.
- **Second pass on the staging tree:** zero secret hits. The only matches were mentions of withheld file names and "WRONG COPY" headers. Those headers are addressed to the history seat, or to files the keel handed over himself.

## Later addition (RAISED v3)

- **When:** 20 Nov 2026, America/Chicago (CST), by Grok Bot, before the file was added to this repository.
- **Coverage:** the contents of `07_raised_toy/GrokBot_RAISED_v3_history_seat.zip` (734 files after unzip; two were Python bytecode under `vendor/`). This zip was not part of the 16 Nov `DigitalLife.zip` handover.
- **Result:** no emails; no `.env` files; no private-key headers; no cloud or code-host token prefixes; no credential-style assignments. No Medicaid, Medicare, grift-investigator, LEIE, NPPES, or HCPCS content in names or text. Ten-digit sequences were sha256 fragments, a hash prefix in `PREDICTIONS.txt`, or decimal fractions in simulation `returned` fields. Nothing was withheld from this pack.

# Withheld, skipped and held-back items
Hashes and paths only. No contents of these items are in this repository. Paths are as they appear inside DigitalLife.zip (`a.zip::b` means file b inside zip a).
## 1. Withheld by the secret-scan rule
- `DigitalLife/GrokBotbattery.py`  sha256 `3eb3ab68f294303da3ac645859aaaa61f402cf6c736b6d281833eb451f0a72f0`. Reason: holds a hard-coded HMAC key literal. The file calls it public fixture material, not a production credential. The same bytes were already withheld from FOR_CLAUDE_four_packs (pack 3) and are public at `organism-whole-environment-batteries/topographic_memory_v0_4/battery.py` (commit 410ca8c6738c8ba83434e10f09ab3e7674605fd3). Adding it here is the keel's call.
## 2. Skipped by name, never opened or listed below this level
Open-round, sealed, hold, ledger, conductor-prediction and handover material, plus workbench folders 12_ and 13_. The skip happened on the name alone.
- `DigitalLife/Fableworkbench_2026-11-14c.zip::workbench_2026-11-14c/07_ledger`
- `DigitalLife/Fableworkbench_2026-11-14c.zip::workbench_2026-11-14c/08_october_archive_reruns/results_commons_sealed.json`
- `DigitalLife/Fableworkbench_2026-11-14c.zip::workbench_2026-11-14c/08_october_archive_reruns/gw_results_sealed.json`
- `DigitalLife/Fableworkbench_2026-11-14c.zip::workbench_2026-11-14c/02_forecasts/SEALED_v3_forecast_HASH_ONLY.txt`
- `DigitalLife/ChatGPTworkbench_2026-11-14.zip::workbench_2026-11-14/07_ledger`
- `DigitalLife/FablePiccoloworkbench_2026-11-14f.zip::workbench_2026-11-14f/11_v071_against_v07/CONDUCTOR_PREDICTIONS_v071_SCORED_2026-11-14.md`
- `DigitalLife/FablePiccoloworkbench_2026-11-14f.zip::workbench_2026-11-14f/11_v071_against_v07/CONDUCTOR_PREDICTIONS_v071_against_v07_2026-11-14_1928.md`
- `DigitalLife/FablePiccoloworkbench_2026-11-14f.zip::workbench_2026-11-14f/07_ledger`
- `DigitalLife/FablePiccoloworkbench_2026-11-14f.zip::workbench_2026-11-14f/15_piccolo_v1/PREDICTIONS_sealed.md`
- `DigitalLife/FablePiccoloworkbench_2026-11-14f.zip::workbench_2026-11-14f/13_grok_redteam_probes_25oct`
- `DigitalLife/FablePiccoloworkbench_2026-11-14f.zip::workbench_2026-11-14f/12_repair_v1_on_both_kernels`
- `DigitalLife/FablePiccoloworkbench_2026-11-14f.zip::workbench_2026-11-14f/08_october_archive_reruns/results_commons_sealed.json`
- `DigitalLife/FablePiccoloworkbench_2026-11-14f.zip::workbench_2026-11-14f/08_october_archive_reruns/gw_results_sealed.json`
- `DigitalLife/FablePiccoloworkbench_2026-11-14f.zip::workbench_2026-11-14f/02_forecasts/SEALED_v3_forecast_HASH_ONLY.txt`
- `DigitalLife/raised_toy_2026-11-15.zip::raised_toy_2026-11-15/ledger/UNEXPECTED_RESULTS_open_ledger.md`
- `DigitalLife/FableTRIAD_HANDOVER_after_Piccolo_v1_2026-11-15.zip` (conductor handover zip, not opened; sha256 `ab489b9221dddd2328e8933dffdb8c3824964c5e13865e9319bc6db08c6292f4`)

## 3. Held back: header says WRONG COPY for any reader but the named seat
These are briefs addressed to the builder seat (ChatGPT). Only their first lines were seen. They are held out until the keel says otherwise.
- `DigitalLife/Fableworkbench_2026-11-14c.zip::workbench_2026-11-14c/01_briefs/FOR_CHATGPT_two_layers_build.md`  sha256 `4a81e05fa61920a7b966eb55e288dfb6655bd63dab67b62525d668cf952eb967`
- `DigitalLife/Fableworkbench_2026-11-14c.zip::workbench_2026-11-14c/01_briefs/FOR_CHATGPT_two_layers_build_v2.md`  sha256 `534ce46ee78662c1afe65bcbf6260fd1d60fdbb8c577fb5eb59d12a6cffe404a`
- `DigitalLife/Fableworkbench_2026-11-14c.zip::workbench_2026-11-14c/01_briefs/WITHDRAWN_never_sent/FOR_CHATGPT_commons_build_v3.md`  sha256 `a8bcfe44bd0bf6bb307e9243b09c067fdfeace87e21c54c5258b20f2285d9245`
- `DigitalLife/ChatGPTworkbench_2026-11-14.zip::workbench_2026-11-14/01_briefs/FOR_CHATGPT_two_layers_build.md`  sha256 `4a81e05fa61920a7b966eb55e288dfb6655bd63dab67b62525d668cf952eb967`
- `DigitalLife/ChatGPTworkbench_2026-11-14.zip::workbench_2026-11-14/01_briefs/FOR_CHATGPT_two_layers_build_v2.md`  sha256 `534ce46ee78662c1afe65bcbf6260fd1d60fdbb8c577fb5eb59d12a6cffe404a`
- `DigitalLife/ChatGPTTwo_Layer_Commons_v0.1_Fable_Handoff.zip::Two_Layer_Commons_v0.1/BUILD_BRIEF.md`  sha256 `4a81e05fa61920a7b966eb55e288dfb6655bd63dab67b62525d668cf952eb967`
- `DigitalLife/ChatGPTTwo_Layer_Commons_v2_Fable_Handoff.zip::Two_Layer_Commons_v2/BUILD_BRIEF.md`  sha256 `534ce46ee78662c1afe65bcbf6260fd1d60fdbb8c577fb5eb59d12a6cffe404a`
- `DigitalLife/ChatGPTTwo_Layer_Commons_v2_Fable_Handoff.zip::Two_Layer_Commons_v2/antecedents/Two_Layer_Commons_v0.1_Fable_Handoff.zip::Two_Layer_Commons_v0.1/BUILD_BRIEF.md`  sha256 `4a81e05fa61920a7b966eb55e288dfb6655bd63dab67b62525d668cf952eb967`
- `DigitalLife/FablePiccoloworkbench_2026-11-14f.zip::workbench_2026-11-14f/01_briefs/FOR_CHATGPT_two_layers_build.md`  sha256 `4a81e05fa61920a7b966eb55e288dfb6655bd63dab67b62525d668cf952eb967`
- `DigitalLife/FablePiccoloworkbench_2026-11-14f.zip::workbench_2026-11-14f/01_briefs/FOR_CHATGPT_two_layers_build_v2.md`  sha256 `534ce46ee78662c1afe65bcbf6260fd1d60fdbb8c577fb5eb59d12a6cffe404a`
- `DigitalLife/FablePiccoloworkbench_2026-11-14f.zip::workbench_2026-11-14f/01_briefs/WITHDRAWN_never_sent/FOR_CHATGPT_commons_build_v3.md`  sha256 `a8bcfe44bd0bf6bb307e9243b09c067fdfeace87e21c54c5258b20f2285d9245`
- `DigitalLife/FableFOR CHATGPT two layers build v2.md`  sha256 `534ce46ee78662c1afe65bcbf6260fd1d60fdbb8c577fb5eb59d12a6cffe404a`
- `DigitalLife/FableFOR CHATGPT two layers build.md`  sha256 `4a81e05fa61920a7b966eb55e288dfb6655bd63dab67b62525d668cf952eb967`

## 4. Not included because they duplicate other copies or are already public
- `DigitalLife/Digital_Life_Assembly_Review/` (loose folder): it matches `ChatGPTDigital_Life_Assembly_Review.zip` file for file, 102 of 102 identical. The zip is kept.
- `DigitalLife/FOR_CLAUDE_four_packs.zip` and `DigitalLife/GrokBotFOR_CLAUDE_four_packs.zip`: the two are byte-identical (sha256 `7db973a71896…`, full hash in INVENTORY_ORIGINAL.csv). They are addressed to the conductor seat, and the four packs are already public in the-terrain-remembers, organism-whole-environment-batteries and related repos.
- `DigitalLife/CauGPTlife.py` and `DigitalLife/ChatGPTlife 2.py`: byte-identical to `ChatGPTlife.py` (sha256 `ec84f73c6844…`). One copy is kept.

## 5. Zips repacked as filtered folders
These zips held something from sections 1 to 3. Each is published here as a folder named `<name>__unpacked_filtered/`, with the excluded items removed. The original zip is not included, so its hash will not match. Manifests inside these folders will list the removed files as missing.
- `DigitalLife/Fableworkbench_2026-11-14c.zip`  original sha256 `48c815a434f7c76802aa52129674b07a07429c06dace9b0c175260721b7bab0d`
- `DigitalLife/ChatGPTworkbench_2026-11-14.zip`  original sha256 `f1d9fc24398bd0aa1f7f52febc6f0d814f80f7603e153bb15fb6145414d8c131`
- `DigitalLife/ChatGPTTwo_Layer_Commons_v0.1_Fable_Handoff.zip`  original sha256 `cec0fb723f600e4932532baa19dbe000c6449eda083cc129c7144f296c55e773`
- `DigitalLife/ChatGPTTwo_Layer_Commons_v2_Fable_Handoff.zip`  original sha256 `3ad4b9a26b8f57136e0ded4cd5ff55136f5084ddbc056860ac8e5f1a30db5124`
- `DigitalLife/ChatGPTTwo_Layer_Commons_v2_Fable_Handoff.zip::Two_Layer_Commons_v2/antecedents/Two_Layer_Commons_v0.1_Fable_Handoff.zip`  original sha256 `cec0fb723f600e4932532baa19dbe000c6449eda083cc129c7144f296c55e773`
- `DigitalLife/FablePiccoloworkbench_2026-11-14f.zip`  original sha256 `a08fdf3cd82244207b2ae57fa839fc80a70b36e5a9b381dc1723b6bc69ebe278`
- `DigitalLife/raised_toy_2026-11-15.zip`  original sha256 `087f065ea9bcd37db0725bcedcea1cfc36940fff1211876b2429fdc5771a0b29`

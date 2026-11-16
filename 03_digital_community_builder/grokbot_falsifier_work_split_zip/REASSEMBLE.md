# Reassembling the split zip

The three parts are one zip cut into pieces of 19,537,300 bytes.

    cat digital-community-builder-falsifier-work-2026-11-12.zip.part1of3 \
        digital-community-builder-falsifier-work-2026-11-12.zip.part2of3 \
        digital-community-builder-falsifier-work-2026-11-12.zip.part3of3 \
        > digital-community-builder-falsifier-work-2026-11-12.zip
    sha256sum digital-community-builder-falsifier-work-2026-11-12.zip

Expected sha256: a08f99b598abbd1e4f038922b7da45e1bef9005ca1133df06fc2937eeddff960
(checked 2026-11-16; 843 entries; zip test passed). The joined zip is 58,611,900 bytes,
above GitHub's 50 MB warning size, so only the parts are stored.

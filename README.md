# FLAPJAX — the 20 largest holders at the last block of 2026-10-23 (COT)

A single-block, from-the-chain holder audit of **FlapJax (FLAPJAX)** on BNB Smart Chain.

- **Token:** `0x90c8889f428F9Ebb77BB8f15CAD3a50a9aC680df` (18 decimals)
- **Snapshot block:** `129454096`
- **Snapshot time:** 2026-10-24 04:59:59 UTC = **2026-10-23 23:59:59 COT (UTC−5)** — the last block of 23 October 2026 in Colombia time. Block `129454097` is the first block of 24 October COT (2026-10-24 05:00:00 UTC).
- **totalSupply at that block:** `44444444444000000000000000000` = 44,444,444,444.000000 FLAPJAX

## Result

| | % of total supply | FLAPJAX |
|---|---|---|
| Top 5 | 69.9793% | 31,101,902,050.224703 |
| Top 10 | 77.4991% | 34,444,036,377.969864 |
| Top 20 | 88.6180% | 39,385,785,959.948406 |
| Outside the top 20 | 11.3820% | 5,058,658,484.051593 |

Amounts are exact truncations of the on-chain 18-decimal integer. The 20th holder holds 383,287,277.524234 FLAPJAX.

Of the 20 largest holders: **3 are contracts** (the two PancakeSwap v3 pools and the address BscScan labels "Pancakeswap: Infinity Vault"), **16 are ordinary wallets**, and **1 is the burn address** `0x000000000000000000000000000000000000dEaD` (no bytecode, but not an ordinary wallet — tokens there are not spendable by any known key).

The full ranked table with labels and the source of each label is in `index.html` and `data/top20.csv`.

## How it was produced

1. **The block.** A binary search over `eth_getBlockByNumber` timestamps returns the last block strictly before 2026-10-24 05:00:00 UTC. COT is UTC−5 year-round.
2. **The numbers.** `totalSupply()` and `balanceOf(address)` are read with `eth_call` at exactly block `129454096` on an archive node. Nothing is read at head.
3. **Candidate coverage.** Candidate addresses come from BscScan's public holder table (used only to enumerate; every number is re-read from a node). To prove no holder was missed at the snapshot, every FLAPJAX `Transfer` from block `129454097` to head was pulled with `eth_getLogs` (47 events, 33 distinct addresses) and the snapshot balance of each of those addresses was read too. The largest snapshot balance among addresses outside today's top 25 is 8,220,000.000000 FLAPJAX; every other address outside today's top 25 that did not move since the snapshot holds at most today's rank-25 balance of 253,650,856.719947. Both are far below the rank-20 balance of 383,287,277.524234 FLAPJAX, so the top-20 set at that block is exact.
4. **Contract vs wallet.** `eth_getCode` for each of the 20 addresses at the snapshot block.

## Reproduce

```bash
python3 verify.py https://bsc-mainnet.public.blastapi.io
```

`verify.py` re-reads `totalSupply` and all 20 balances from a node at block `129454096` and compares them to `data/top20.json`, printing a per-row `ok`/`MISMATCH` and exiting non-zero on any difference. The node must serve archive state at that block.

Equivalent raw call for one address:

```bash
curl -s -X POST https://bsc-mainnet.public.blastapi.io -H 'Content-Type: application/json' --data '{
  "jsonrpc":"2.0","id":1,"method":"eth_call",
  "params":[{"to":"0x90c8889f428F9Ebb77BB8f15CAD3a50a9aC680df",
             "data":"0x70a08231000000000000000000000000ca93ec685b8623688e6b236f9068034b298c2150"},
            "0x7b75010"]}'
```

## Files

- `index.html` — the audit page (self-contained, no external assets)
- `data/top20.csv` — rank, address, exact balance in wei (18 dp), token amount, share, type, label
- `data/top20.json` — same data as JSON plus snapshot metadata
- `verify.py` — independent re-check of every published number against a live node

## Limits

- One block, not a history. Holdings changed after the snapshot (the treasury address and the Infinity Vault both moved tokens), so this is not today's distribution.
- "Contract" means "had bytecode at that block"; it does not distinguish pool, vault, multisig or bridge.
- Shares are of `totalSupply`, not of a circulating supply, which is not defined on-chain.
- Fourteen of the twenty addresses carry no public label and are left unlabelled rather than guessed.

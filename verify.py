#!/usr/bin/env python3
"""Re-check the FLAPJAX top-20 snapshot table against a BNB Smart Chain node.

Usage:
    python3 verify.py [RPC_URL]

The node must serve archive state at the snapshot block (129454096).
Exits 0 when every balance and the total supply match the published data,
1 on any mismatch, 2 if the node cannot answer at that block.
"""
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "data", "top20.json")))

TOKEN = DATA["token"]
SNAP = DATA["snapshot_block"]
SUPPLY_RAW = int(DATA["total_supply_raw"])
DEFAULT_RPC = "https://bsc-mainnet.public.blastapi.io"


def rpc(url, method, params, timeout=60):
    req = urllib.request.Request(
        url,
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "flapjax-audit-verify/1.0"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        out = json.load(r)
    if "error" in out:
        raise RuntimeError(json.dumps(out["error"])[:200])
    return out["result"]


def balance_of(url, address):
    data = "0x70a08231" + "0" * 24 + address[2:].lower()
    result = rpc(url, "eth_call", [{"to": TOKEN, "data": data}, hex(SNAP)])
    return int(result, 16)


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("BSC_RPC_URL", DEFAULT_RPC)
    print(f"node          : {url}")
    print(f"token         : {TOKEN}")
    print(f"snapshot block: {SNAP}")

    try:
        supply = int(rpc(url, "eth_call", [{"to": TOKEN, "data": "0x18160ddd"}, hex(SNAP)]), 16)
    except (RuntimeError, urllib.error.HTTPError, urllib.error.URLError) as exc:
        print(f"FAIL: node cannot serve state at block {SNAP} ({exc})")
        return 2

    print(f"totalSupply   : {supply}  (published {SUPPLY_RAW})")
    ok = supply == SUPPLY_RAW
    if not ok:
        print("MISMATCH: total supply differs from the published value")

    scale = 10 ** 18
    print(f"\n{'#':>2}  {'address':42}  {'balance (FLAPJAX)':>22}  {'share':>9}  status")
    running = 0
    for holder in DATA["holders"]:
        got = balance_of(url, holder["addr"])
        want_exact = int(holder["balance_raw"])
        running += got
        same = got == want_exact
        ok = ok and same
        share = got / supply * 100 if supply else 0
        print(f"{holder['rank']:>2}  {holder['addr']:42}  {got / scale:>22,.6f}  {share:>8.4f}%  {'ok' if same else 'MISMATCH'}")

    top20 = running / scale
    print(f"\ntop-20 sum    : {top20:,.6f} FLAPJAX  ({running / supply * 100:.4f}% of supply)" if supply else "")
    print(f"published     : {DATA['top20_percent']:.4f}%")

    if ok:
        print("\nPASS: all 20 balances and the total supply match the published snapshot.")
        return 0
    print("\nFAIL: at least one value differs from the published snapshot.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

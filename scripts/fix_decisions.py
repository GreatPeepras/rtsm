#!/usr/bin/env python3
import json
from collections import Counter
RAW = "rtsm_decisions.json"
COLA_PRIMARY = "44f349f5ca194fbb"
COLA_OTHERS  = ["3c42c95ec4394030", "b73d6f118b92436c", "e6a5652f488f40ad"]
KALLAX_NAME_OID = "f0aba9d1aae14eb2"
ORDIS_LIVE_OID = "01b1dfab1bce485c"
ORDIS_LOSERS = ["327abb823a9341bc","c476382e29004e2c","744846b7e7644efe",
                "c56fe332e34e411c","bbded67ea1024f47","51b4ec1c16bb4756"]
d = json.load(open(RAW)); dec = d["decisions"]
def show(o):
    v=dec.get(o,{}); return f"{o[:8]}={v.get('action')}({v.get('merge_into') or v.get('name')})"
print("BEFORE:")
for o in [COLA_PRIMARY]+COLA_OTHERS+[KALLAX_NAME_OID]+ORDIS_LOSERS: print("  ",show(o))
dec[COLA_PRIMARY] = {"action":"name","name":"cola desk"}
for o in COLA_OTHERS:
    dec[o] = {"action":"merge","merge_into":COLA_PRIMARY,"merge_into_raw":"cola desk"}
dec[KALLAX_NAME_OID] = {"action":"name","name":"Kallax shelf"}
for o in ORDIS_LOSERS:
    dec[o] = {"action":"merge","merge_into":ORDIS_LIVE_OID,"merge_into_raw":"ordis work bag"}
json.dump(d, open(RAW,"w"), indent=1)
print("\nAFTER:")
for o in [COLA_PRIMARY]+COLA_OTHERS+[KALLAX_NAME_OID]+ORDIS_LOSERS: print("  ",show(o))
print("\ncounts:", dict(Counter(v['action'] for v in dec.values())))

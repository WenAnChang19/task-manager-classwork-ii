"""Independently verify saved W3Schools results against ungrouped detail rows."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
import json
ROOT=Path(__file__).resolve().parents[1]
raw=json.loads((ROOT/'evidence/sql-detail.json').read_text())
results=json.loads((ROOT/'evidence/sql-results.json').read_text())
rows=[dict(zip(raw[0],row)) for row in raw[1:]]
totals=defaultdict(Decimal)
quantities=defaultdict(int)
for r in rows:
    if r['Country']=='France':
        totals[int(r['CustomerID'])]+=Decimal(r['Price'])*int(r['Quantity'])
    if '1996-07-01'<=r['OrderDate']<'1996-08-01':
        quantities[int(r['ProductID'])]+=int(r['Quantity'])
b1=sorted(totals.items(),key=lambda r:(-r[1],r[0]))
assert b1==[(int(r[0]),Decimal(r[2])) for r in results[0]['rows'][1:]]
b2=sorted(quantities.items(),key=lambda r:(-r[1],r[0]))[:5]
assert b2==[(int(r[0]),int(r[2])) for r in results[1]['rows'][1:]]
tofu=sorted((r for r in rows if r['ProductName']=='Tofu'),key=lambda r:(int(r['CustomerID']),r['OrderDate'],int(r['OrderID'])))
b3=[[r[k] for k in ['CustomerID','CustomerName','OrderDate','Quantity']] for r in tofu]
assert b3==results[2]['rows'][1:]
print(f'B1 / B2 / B3 PASS; independently checked {len(rows)} detail rows.')

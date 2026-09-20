#!/usr/bin/env python3
"""Wrapper: download MEF CSV, strip BOM, save."""
import sys, os
from urllib.request import urlopen, Request

url = sys.argv[1]
outfile = sys.argv[2]

req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (DataCivicLab/1.0)'})
with urlopen(req, timeout=120) as r:
    content = r.read()

# Strip BOM
if content[:3] == b'\xef\xbb\xbf':
    content = content[3:]

os.makedirs(os.path.dirname(outfile), exist_ok=True)
with open(outfile, 'wb') as f:
    f.write(content)

print(f'Downloaded {len(content)} bytes to {outfile}')

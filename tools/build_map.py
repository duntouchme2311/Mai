#!/usr/bin/env python3
"""Convert an OpenStreetMap XML extract into game/map-data.js.

Usage: python3 tools/build_map.py data/osm-raw.osm game/map-data.js

The world is rotated so the cathedral facade faces +z and its front-centre is the origin.
Units are metres. Data (c) OpenStreetMap contributors, ODbL.
"""
import sys, json, math, xml.etree.ElementTree as ET

CATHEDRAL_WAY = '801950766'
BEHIND_NAME = 'Diamond Plaza'   # a building known to be behind the cathedral, to orient the axis
src, out = sys.argv[1], sys.argv[2]
root = ET.parse(src).getroot()

tags = lambda e: {t.get('k'): t.get('v') for t in e.findall('tag')}
nodes = {n.get('id'): (float(n.get('lat')), float(n.get('lon'))) for n in root.iter('node')}
ways = {w.get('id'): w for w in root.iter('way')}
way_nodes = lambda w: [nd.get('ref') for nd in w.findall('nd') if nd.get('ref') in nodes]

b = root.find('bounds')
lat0 = (float(b.get('minlat')) + float(b.get('maxlat'))) / 2
lon0 = (float(b.get('minlon')) + float(b.get('maxlon'))) / 2
KX, KY = 111320 * math.cos(math.radians(lat0)), 110540
def en(ref):  # east/north metres -> pre-rotation game plane (X = east, Z = -north)
    la, lo = nodes[ref]
    return ((lo - lon0) * KX, -(la - lat0) * KY)

# --- orientation from the cathedral footprint (principal axis) ---
cat = [en(r) for r in way_nodes(ways[CATHEDRAL_WAY])]
cx = sum(p[0] for p in cat) / len(cat); cz = sum(p[1] for p in cat) / len(cat)
sxx = sum((p[0] - cx) ** 2 for p in cat); szz = sum((p[1] - cz) ** 2 for p in cat)
sxz = sum((p[0] - cx) * (p[1] - cz) for p in cat)
ang = 0.5 * math.atan2(2 * sxz, sxx - szz)
f = (math.cos(ang), math.sin(ang))
behind = None
for w in ways.values():
    t = tags(w)
    if BEHIND_NAME in t.get('name', ''):
        ps = [en(r) for r in way_nodes(w)]
        behind = (sum(p[0] for p in ps) / len(ps), sum(p[1] for p in ps) / len(ps)); break
if behind and (behind[0] - cx) * f[0] + (behind[1] - cz) * f[1] > 0:
    f = (-f[0], -f[1])
rot = lambda p: (p[0] * f[1] - p[1] * f[0], p[0] * f[0] + p[1] * f[1])
catr = [rot(p) for p in cat]
ox = (min(p[0] for p in catr) + max(p[0] for p in catr)) / 2
oz = max(p[1] for p in catr)
def P(ref):
    x, z = rot(en(ref)); return (round(x - ox, 1), round(z - oz, 1))
flat = lambda refs: [c for r in refs for c in P(r)]
catg = [(p[0] - ox, p[1] - oz) for p in catr]
print('cathedral footprint: width %.1f m, length %.1f m' % (max(p[0] for p in catg) - min(p[0] for p in catg), -min(p[1] for p in catg)))

# Sensitive places (government, diplomatic, judicial, military, political) are kept as anonymous
# blocks only: no name, no type, no points of interest. Extend this list when adding new areas.
SENSITIVE = ('lãnh sự', 'đại sứ', 'ủy ban', 'uỷ ban', 'viện kiểm sát', 'tòa án', 'toà án', 'sở ', 'cục ', 'chi cục',
             'thành đoàn', 'liên đoàn', 'dinh ', 'công an', 'quân ', 'quân đội', 'bộ ', 'thống kê', 'viện ', 'đảng',
             'nhà khách', 'tank', 'bia ', 'tượng đài', 'trận đánh', 'công chứng', 'kho bạc', 'ngân hàng nhà nước')
SENSITIVE_TYPES = ('civic', 'government', 'military', 'palace', 'public')
def is_sensitive(t):
    name = (t.get('name', '') + ' ').lower()
    return (any(k in name for k in SENSITIVE) or t.get('building') in SENSITIVE_TYPES
            or any(k in t for k in ('military', 'diplomatic', 'government')) or t.get('office') in ('government', 'diplomatic')
            or t.get('amenity') in ('embassy', 'police', 'courthouse', 'townhall', 'prison'))
hidden = []

def seeded(i, a, b_):  # deterministic pseudo-random per OSM id
    return a + (int(i) * 2654435761 % 1000) / 1000 * (b_ - a)

buildings, roads, parks, trees, barriers = [], [], [], [], []
def add_building(wid, refs, t):
    if len(refs) < 4 or refs[0] != refs[-1]: return
    h, est = None, 1
    try:
        if 'height' in t: h, est = float(t['height'].split()[0]), 0
        elif 'building:levels' in t: h, est = float(t['building:levels']) * 3.6 + 1, 0
    except ValueError: pass
    if h is None: h = 3.5 if t.get('building') == 'roof' else seeded(wid, 7, 20)
    d = {'id': wid, 'p': flat(refs[:-1]), 'h': round(h, 1), 'e': est}
    if is_sensitive(t): hidden.append(t.get('name', '(no name)'))
    else:
        if 'name' in t: d['n'] = t['name']
        if t.get('building') not in (None, 'yes'): d['t'] = t['building']
    buildings.append(d)

for wid, w in ways.items():
    t, refs = tags(w), way_nodes(w)
    if len(refs) < 2: continue
    if 'building' in t: add_building(wid, refs, t)
    elif 'highway' in t and t.get('area') != 'yes':
        roads.append({'p': flat(refs), 'k': t['highway'], **({'n': t['name']} if 'name' in t else {})})
    elif (t.get('leisure') in ('park', 'garden') or t.get('landuse') in ('grass', 'recreation_ground', 'village_green')) and refs[0] == refs[-1]:
        parks.append({'p': flat(refs[:-1])})
    elif t.get('barrier') in ('fence', 'wall') :
        barriers.append({'p': flat(refs)})
for r in root.iter('relation'):
    t = tags(r)
    if 'building' not in t: continue
    for m in r.findall('member'):
        if m.get('type') == 'way' and m.get('role') == 'outer' and m.get('ref') in ways:
            add_building(m.get('ref'), way_nodes(ways[m.get('ref')]), t)
pois = []
for n in root.iter('node'):
    t = tags(n)
    if t.get('natural') == 'tree': trees += list(P(n.get('id')))
    elif any(k in t for k in ('historic', 'tourism')) and 'name' in t and not is_sensitive(t) and t.get('tourism') != 'hotel':
        pois.append({'n': t['name'], 'k': t.get('historic') or t.get('tourism'), 'p': list(P(n.get('id')))})

nx, nz = rot((0.0, -1.0))  # north = -Z before rotation
cxr, czr = rot((0.0, 0.0))
data = {'north': [round(nx, 4), round(nz, 4)], 'center': [round(cxr - ox, 1), round(czr - oz, 1)], 'cathedral': CATHEDRAL_WAY, 'buildings': buildings, 'roads': roads,
        'parks': parks, 'trees': trees, 'barriers': barriers, 'pois': pois,
        'attribution': '© OpenStreetMap contributors (ODbL)'}
with open(out, 'w', encoding='utf-8') as fh:
    fh.write('// Generated by tools/build_map.py. Map data © OpenStreetMap contributors, ODbL.\n')
    fh.write('window.MAP = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
print(len(buildings), 'buildings,', len(roads), 'roads,', len(parks), 'parks,', len(trees) // 2, 'trees,', len(barriers), 'barriers')
print('north vector (x,z):', data['north'])
print('names hidden as sensitive:', len(hidden)); [print('  -', h) for h in sorted(set(hidden))]
for p in pois: print('poi', p)
for d in buildings:
    if d.get('n') and any(s in d['n'] for s in ('Bưu điện', 'Diamond', 'Nhà thờ', 'Vincom', 'Metropolitan')):
        xs, zs = d['p'][0::2], d['p'][1::2]; print(d['n'], 'x %.0f..%.0f z %.0f..%.0f h %s' % (min(xs), max(xs), min(zs), max(zs), d['h']))

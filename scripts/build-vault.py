"""Build an Obsidian vault (architecture map) from output/full-crawl.

Usage: python scripts/build-vault.py [crawl_dir] [vault_dir]
"""
import csv, json, re, sys, shutil, collections
from pathlib import Path
from urllib.parse import urlparse, unquote, parse_qs

crawl = Path(sys.argv[1] if len(sys.argv) > 1 else 'output/full-crawl')
vault = Path(sys.argv[2] if len(sys.argv) > 2 else 'obsidian-vault')

TEMPLATES = [
    (r'^/products/p-[^/]+/([^/]+)$', r'/products/:product/\1'),
    (r'^/products/p-[^/]+$', '/products/:product'),
    (r'^/decision/[^/]+$', '/decision/:finding'),
    (r'^/supply-chain/suppliers/[^/]+$', '/supply-chain/suppliers/:supplier'),
    (r'^/compliance/enisa/[^/]+$', '/compliance/enisa/:product'),
]
GLOBAL_SHARE = 0.85
CVE_RE = re.compile(r'CVE-\d{4}-\d{4,}')
SEV_RE = re.compile(r'(CVE-\d{4}-\d{4,}) (Critical|High|Medium|Low)( Exploited)?')
PKG_RE = re.compile(r'(?<![\w@])([a-z][\w.+-]*)@(\d[\w.+-]*)')
PRODUCT_RE = re.compile(r'\b([A-Z]{2,5}-\d{3}) (.+?)(?= [A-Z]{2,5}-\d{3} |$)')


def path_of(url):
    return unquote(urlparse(url).path).rstrip('/') or '/'

def template(url):
    p = path_of(url)
    for pat, rep in TEMPLATES:
        if re.match(pat, p):
            return re.sub(pat, rep, p)
    return p

def section(tpl):
    return tpl.strip('/').split('/')[0] or 'home'

def main_text(p):
    return (p.get('visibleText') or '').split('© 20')[0]

def clean(s):
    return re.sub(r'\s+', ' ', s or '').strip()

def norm(s):
    s = clean(s).lower()
    s = re.sub(r'cve-\d{4}-\d+', 'cve-#', s)
    s = re.sub(r'[\w.-]+@[\w.+-]+', '<pkg>@<ver>', s)
    s = re.sub(r'\bv?\d+(\.\d+)+\b', '<ver>', s)
    return re.sub(r'\d+', '#', s)

def safe(name):
    name = re.sub(r'[\\/:*?"<>|#^\[\]]', ' ', name)
    return re.sub(r'\s+', ' ', name).strip()[:90]

def page_note(tpl):
    return 'Page ' + (safe(tpl.strip('/').replace('/', ' › ').replace(':', '')) or 'home')

def link(name, alias=None):
    return f'[[{name}|{alias}]]' if alias else f'[[{name}]]'

# ---------------------------------------------------------------- load
rows = list(csv.DictReader(open(crawl / 'features.csv', encoding='utf-8-sig')))
pages = json.load(open(crawl / 'pages.json', encoding='utf-8'))
by_url = {p['url']: p for p in pages}

def fkey(r):
    ft = r['featureType']
    if ft == 'navigation' and not r['targetUrl']:
        ft = 'control'
    if ft == 'navigation':
        return (ft, template(r['targetUrl']))
    return (ft, norm(r['label']) or '(unlabelled ' + r['element'] + ')')

tpl_urls = collections.defaultdict(set)
for p in pages:
    tpl_urls[template(p['url'])].add(p['url'])

feat_urls = collections.defaultdict(set)
feat_tpls = collections.defaultdict(set)
feat_labels = collections.defaultdict(collections.Counter)
tpl_feats = collections.defaultdict(set)
for r in rows:
    k, t = fkey(r), template(r['url'])
    feat_urls[k].add(r['url'])
    feat_tpls[k].add(t)
    tpl_feats[t].add(k)
    lbl = clean(r['label'])
    feat_labels[k][lbl if len(lbl) <= 80 else lbl[:79] + '…'] += 1

table_headers = {}
for p in pages:
    for tb in p.get('tables') or []:
        hdr = [clean(h) for h in tb.get('headers') or [] if clean(h)]
        if hdr:
            table_headers.setdefault(norm(' | '.join(hdr)), hdr)

n_pages = len(by_url)
if n_pages < 20 or len(rows) < 500:
    sys.exit(f'Refusing to build: crawl at {crawl} has only {n_pages} pages / {len(rows)} features '
             '(looks like a failed crawl). Existing vault left untouched.')
global_keys = {k for k, u in feat_urls.items() if len(u) >= GLOBAL_SHARE * n_pages}
shared_keys = {k for k, ts in feat_tpls.items()
               if len(ts) >= 2 and k not in global_keys and k[0] != 'navigation' and k[0] != 'heading'}

def label(k):
    ex = [e for e, _ in feat_labels[k].most_common() if e]
    return ex[0] if ex else k[1]

TYPE_NAME = {'tab': 'Tab', 'tab view': 'Tab', 'control': 'Control', 'form field': 'Field', 'table': 'Table'}

def feature_note(k):
    if k[0] == 'table':
        hdr = table_headers.get(norm(label(k)).replace(' | ', ' | '), None) or [h.strip() for h in label(k).split('|')]
        return safe('Table - ' + ', '.join(h for h in hdr if h)[:70])
    return safe(f'{TYPE_NAME.get(k[0], k[0].title())} - {re.sub(r" \d+$", "", label(k))}')

# merge "tab" and "tab view" with same label into one note
note_of = {}
for k in shared_keys:
    note_of[k] = feature_note(k)

# ---------------------------------------------------------------- entities
products = {}           # short id (TCU-200) -> name
product_slug = {}       # p-tcu-200 -> TCU-200
for r in rows:
    if r['featureType'] == 'form field' and r['label'].startswith('All products'):
        for m in PRODUCT_RE.finditer(clean(r['label'])[len('All products '):]):
            products[m.group(1)] = m.group(2)
for p in pages:
    m = re.match(r'^/products/(p-[^/]+)', path_of(p['url'])) or re.match(r'^/compliance/enisa/(p-[^/]+)', path_of(p['url']))
    if m:
        slug = m.group(1)
        short = slug[2:].upper()
        product_slug[slug] = short if short in products else product_slug.get(slug, short)
for slug, short in product_slug.items():
    products.setdefault(short, short)

cve_comp = collections.defaultdict(set)
cve_sev = collections.defaultdict(collections.Counter)
cve_kev = set()
cve_products = collections.defaultdict(set)
cve_pages = collections.defaultdict(set)
comp_versions = collections.defaultdict(set)
comp_products = collections.defaultdict(set)

def product_of(url):
    m = re.match(r'^/(?:products|compliance/enisa)/(p-[^/]+)', path_of(url))
    return product_slug.get(m.group(1)) if m else None

for r in rows:
    lbl = clean(r['label'])
    m = re.match(r'Select (CVE-\d{4}-\d+) in (\S+)', lbl)
    prod = product_of(r['url'])
    if m:
        cve_comp[m.group(1)].add(m.group(2))
        if prod:
            cve_products[m.group(1)].add(prod)
            comp_products[m.group(2)].add(prod)
    for name, ver in PKG_RE.findall(lbl):
        comp_versions[name].add(ver)
        if prod:
            comp_products[name].add(prod)

for p in pages:
    text = main_text(p)
    t = template(p['url'])
    for m in SEV_RE.finditer(text):
        cve_sev[m.group(1)][m.group(2)] += 1
        if m.group(3):
            cve_kev.add(m.group(1))
    for c in set(CVE_RE.findall(text)) | set(CVE_RE.findall(p['url'])):
        cve_pages[c].add(t)
    # decision ids embed the CVE: f-c-ivi-log4j-2021-44228-714
    m = re.match(r'^/decision/f-c-(\w+)-[\w]+-(\d{4})-(\d+)-\d+$', path_of(p['url']))
    if m:
        cve = f'CVE-{m.group(2)}-{m.group(3)}'
        cve_pages[cve].add(t)
        short = next((s for s in products if s.lower().startswith(m.group(1))), None)
        if short:
            cve_products[cve].add(short)

# visibleText is truncated by the crawler, so feature labels are a second source of CVE mentions
for r in rows:
    for c in CVE_RE.findall(r['label'] + ' ' + r['targetUrl']):
        cve_pages[c].add(template(r['url']))

suppliers = {}  # slug -> dict
for p in pages:
    m = re.match(r'^/supply-chain/suppliers/(.+)$', path_of(p['url']))
    if not m:
        continue
    text = main_text(p)
    head = re.search(r'Supply chain [A-Z]{1,3} (.+?) (Not registered|Registered)', text)
    name = head.group(1) if head else m.group(1).title()
    known = {x for s in cve_comp.values() for x in s} | set(comp_versions)
    comps = {c for c in known if re.search(r'(?<![\w-])' + re.escape(c) + r'(?![\w-])', text)}
    prods = {s for s in products if s in text.split('Products and components')[-1]}
    suppliers[m.group(1)] = {'name': name, 'components': comps, 'products': prods,
                             'cves': set(CVE_RE.findall(text)), 'registered': bool(head and head.group(2) == 'Registered')}

all_comps = set(comp_versions) | {c for s in cve_comp.values() for c in s}

# shared features that are really data rows (mention a product/component/supplier) are covered by entity notes
data_words = set(products) | all_comps | {s['name'] for s in suppliers.values()}
data_re = re.compile(r'(?<![\w-])(' + '|'.join(re.escape(w) for w in sorted(data_words, key=len, reverse=True)) + r')(?![\w-])', re.I)
for k in list(note_of):
    lb = label(k)
    if k[0] != 'table' and (data_re.search(lb) or CVE_RE.search(lb) or re.fullmatch(r'[A-Z][a-z]+ [A-Z][a-z]+', lb)
                            or re.fullmatch(r'v?\d+(\.\d+)+', lb) or re.search(r'\(supplier\)| team$|^Supplier .+ open CVE', lb)):
        del note_of[k]
    elif k[0] == 'control' and label(k).startswith('About '):
        note_of[k] = 'Control - About (info tooltips)'
comp_supplier = collections.defaultdict(set)
for slug, s in suppliers.items():
    for c in s['components']:
        comp_supplier[c].add(s['name'])


# ---------------------------------------------------------------- tree
# Every note has exactly one parent (⬆ Back) and a numbered list of children (➡ Next junctions).
# Everything else is plain text, so the graph view is a clean tree starting at START HERE.

START = 'START HERE'
SIDEBAR = [
    ('Main menu', 'Home, products and the Friday assistant', ['home', 'products', 'friday']),
    ('Security', 'Vulnerability, threat, PSIRT, supply-chain and compliance work',
     ['vulnerabilities', 'threat-intel', 'psirt', 'supply-chain', 'compliance']),
    ('Workspace', 'Reports, integrations and settings', ['reports', 'integrations', 'settings']),
]
in_sidebar = {s for _, _, secs in SIDEBAR for s in secs}
other_secs = sorted({section(t) for t in tpl_urls} - in_sidebar)
SIDEBAR.append(('Other pages', 'Pages reached from inside the app, not from the sidebar', other_secs))

nodes = {}  # name -> dict(folder, tags, title, parent, children[], desc, body[])

def node(name, folder, tag, title=None, desc=''):
    nodes.setdefault(name, {'folder': folder, 'tag': tag, 'title': title or name, 'parent': None,
                            'children': [], 'desc': desc, 'body': []})
    return nodes[name]

def attach(parent, child):
    if nodes[child]['parent'] is None:
        nodes[child]['parent'] = parent
    if child not in nodes[parent]['children']:
        nodes[parent]['children'].append(child)

def page_name(t):
    return 'home' if t == '/' else safe(t.strip('/').replace('/', ' › ').replace(':', ''))

def headline(t):
    hs = [label(k) for k in tpl_feats.get(t, set()) - global_keys if k[0] == 'heading']
    return hs[0] if hs else ''

def nfeat(t):
    return len(tpl_feats.get(t, set()) - global_keys)

node(START, '', 'start', 'START HERE — DestroSolutions PSOC')

# app branch: sidebar group -> section -> pages nested by URL path
for group, gdesc, secs in SIDEBAR:
    node(group, '1 Junctions', 'junction', desc=gdesc)
    attach(START, group)
    for sec in secs:
        root = '/' if sec == 'home' else '/' + sec
        if root in tpl_urls:
            sname = page_name(root)
            node(sname, '2 Pages', 'page', title=root)
        else:
            sname = f'{sec} (section)'
            node(sname, '1 Junctions', 'junction', desc='section with no landing page of its own')
        attach(group, sname)

for t in sorted(tpl_urls, key=lambda t: (t.count('/'), t)):
    name = page_name(t)
    n = node(name, '2 Pages', 'page', title=t)
    n['desc'] = (f'{nfeat(t)} features' + (f' · "{headline(t)}"' if headline(t) else '')) if nfeat(t) else '⚠ not captured'
    if t == '/' or t == '/' + section(t):
        continue  # already attached under its sidebar group
    parts = t.strip('/').split('/')
    parent = None
    for i in range(len(parts) - 1, 0, -1):
        cand = '/' + '/'.join(parts[:i])
        if cand in tpl_urls:
            parent = page_name(cand)
            break
    attach(parent or (page_name('/' + section(t)) if '/' + section(t) in tpl_urls else f'{section(t)} (section)'), name)

# data branch
node('Data', '1 Junctions', 'junction', desc='Products, suppliers, components and CVEs found in the crawl')
attach(START, 'Data')
node('Global shell', '1 Junctions', 'junction', desc='What every page has: sidebar, top bar, search, Friday panel')
attach(START, 'Global shell')

all_cves = set(cve_pages) | set(cve_comp)
sev_of = lambda c: cve_sev[c].most_common(1)[0][0] if cve_sev[c] else 'Unknown'
prod_note = lambda s: safe(f'{s} {products[s]}') if products.get(s, s) != s else s
sup_note = lambda n: safe(n + ' (supplier)')

for lst, desc in [('Products list', f'{len(products)} products'), ('Suppliers list', f'{len(suppliers)} suppliers'),
                  ('Components list', f'{len(all_comps)} software components'), ('CVEs list', f'{len(all_cves)} vulnerabilities')]:
    node(lst, '3 Data', 'data-list', desc=desc)
    attach('Data', lst)

for s in sorted(products):
    comps = sorted(c for c, ps in comp_products.items() if s in ps)
    cves = [c for c, ps in cve_products.items() if s in ps]
    node(prod_note(s), '3 Data/Products', 'product', desc=f'{len(comps)} components · {len(cves)} CVEs')
    attach('Products list', prod_note(s))
for slug, sp in sorted(suppliers.items()):
    node(sup_note(sp['name']), '3 Data/Suppliers', 'supplier', desc=f'{len(sp["components"])} components')
    attach('Suppliers list', sup_note(sp['name']))
for c in sorted(all_comps):
    cves = sorted(x for x, cs in cve_comp.items() if c in cs)
    node(c, '3 Data/Components', 'component', desc=f'{len(cves)} CVEs')
    attach('Components list', c)
for c in sorted(all_cves):
    node(c, '3 Data/CVEs', 'cve', desc=sev_of(c) + (' · KEV' if c in cve_kev else ''))
    attach('CVEs list', c)
# second-level data junctions: product -> its components -> their CVEs; supplier -> its components
for s in sorted(products):
    for c in sorted(c for c, ps in comp_products.items() if s in ps):
        attach(prod_note(s), c)
for sp in suppliers.values():
    for c in sorted(sp['components']):
        attach(sup_note(sp['name']), c)
for c in sorted(all_comps):
    for x in sorted(x for x, cs in cve_comp.items() if c in cs):
        attach(c, x)

# ---------------------------------------------------------------- note bodies
def plain_list(title, items):
    return [f'**{title}:** ' + ' · '.join(items), ''] if items else []

for t in tpl_urls:
    keys = tpl_feats.get(t, set()) - global_keys
    b = nodes[page_name(t)]['body']
    b += [f'Crawled URLs: {len(tpl_urls[t])} · e.g. {sorted(tpl_urls[t])[0]}', '']
    if not keys:
        b += ['> [!warning] Nothing captured on this page', '> Only the global shell was recorded. Re-crawl with a longer render wait.', '']
        continue
    b += ['## What\'s on this page', '']
    for ft, title in [('tab', 'Tabs'), ('control', 'Buttons & controls'), ('form field', 'Inputs & filters'), ('heading', 'Headings')]:
        items = sorted({label(k) for k in keys if k[0] == ft or (ft == 'tab' and k[0] == 'tab view')}, key=str.lower)
        b += plain_list(f'{title} ({len(items)})', items)
    tables = sorted({label(k) for k in keys if k[0] == 'table'})
    if tables:
        b += [f'**Tables ({len(tables)}):**', ''] + [f'- `{x}`' for x in tables] + ['']
    outs = sorted({k[1] for k in keys if k[0] == 'navigation' and k[1] in tpl_urls and k[1] != t})
    kids = {nodes[c]['title'] for c in nodes[page_name(t)]['children']}
    outs = [o for o in outs if o not in kids and o != (nodes[nodes[page_name(t)]['parent']]['title'] if nodes[page_name(t)]['parent'] else '')]
    if outs:
        b += ['## Also links out to (elsewhere in the tree)', ''] + [f'- `{o}`' for o in outs] + ['']
    cves = sorted(c for c, ts in cve_pages.items() if t in ts)
    prods = sorted({product_of(u) for u in tpl_urls[t]} - {None})
    if cves or prods:
        b += ['## Data shown here', ''] + plain_list('Products', prods) + plain_list('CVEs', cves)

shell = nodes['Global shell']['body']
for ft, title in [('control', 'Buttons & controls'), ('form field', 'Inputs'), ('navigation', 'Sidebar links')]:
    shell += plain_list(title, sorted({label(k) for k in global_keys if k[0] == ft or (ft == 'control' and k[0] == 'heading')}, key=str.lower))

for c in all_cves:
    nodes[c]['body'] += [f'Severity: **{sev_of(c)}**' + (' · **Known exploited (KEV)**' if c in cve_kev else ''), '']
    nodes[c]['body'] += plain_list('Component', sorted(cve_comp[c])) + plain_list('Affects products', sorted(cve_products[c]))
    nodes[c]['body'] += plain_list('Shown on pages', sorted(cve_pages[c]))
for c in all_comps:
    nodes[c]['body'] += plain_list('Versions seen', sorted(comp_versions[c])) + plain_list('Supplier', sorted(comp_supplier[c]))
    nodes[c]['body'] += plain_list('Used in products', sorted(comp_products[c]))
for sp in suppliers.values():
    nodes[sup_note(sp['name'])]['body'] += plain_list('Registered', ['yes' if sp['registered'] else 'no'])
    nodes[sup_note(sp['name'])]['body'] += plain_list('Products', sorted(sp['products'])) + plain_list('Open CVEs', sorted(sp['cves']))
for s in products:
    nodes[prod_note(s)]['body'] += [f'**Name:** {products[s]}', '']
    nodes[prod_note(s)]['body'] += plain_list('Open CVEs', sorted(c for c, ps in cve_products.items() if s in ps))
    nodes[prod_note(s)]['body'] += ['App pages for this product live under `products › product` in the tree.', '']

nodes[START]['body'] = [
    f'Map of **app.destrosolutions.com** built from the crawl: {len(by_url)} URLs → {len(tpl_urls)} page types, '
    f'{len(products)} products, {len(suppliers)} suppliers, {len(all_comps)} components, {len(all_cves)} CVEs.', '',
    '> **New here? Read [[PLANNING OVERVIEW]] first.** It is the whole app on one page.',
    '> **Rebuilding?** The module-by-module plan is in [[REBUILD PLAN]].', '',
    '**How to use:** pick a junction below, then keep following ➡ *Next junctions*. Every note has ⬆ *Back* to return one step.', '',
]

# ---------------------------------------------------------------- write
for old in ['Sections', 'Pages', 'Features', 'Entities', 'Map', '1 Junctions', '2 Pages', '3 Data']:
    shutil.rmtree(vault / old, ignore_errors=True)
for old in ['00 App Map.md', START + '.md']:
    (vault / old).unlink(missing_ok=True)

def crumbs(name):
    chain = []
    while name:
        chain.append(nodes[name]['title'] if nodes[name]['tag'] == 'page' else name)
        name = nodes[name]['parent']
    return ' › '.join(reversed(chain))

for name, n in nodes.items():
    folder = vault / n['folder'] if n['folder'] else vault
    folder.mkdir(parents=True, exist_ok=True)
    out = ['---', 'tags:', f'  - {n["tag"]}', '---', '', f'# {n["title"]}', '']
    if n['parent']:
        out += [f'📍 {crumbs(name)}', '', f'⬆ **Back:** [[{n["parent"]}]]', '']
    if n['desc'] and n['tag'] != 'page':
        out += [f'*{n["desc"]}*', '']
    out += n['body'] if name == START else []
    out += [f'## ➡ Next junctions ({len(n["children"])})', '']
    if n['children']:
        for i, c in enumerate(n['children'], 1):
            alias = nodes[c]['title'] if nodes[c]['tag'] == 'page' else c
            out.append(f'{i}. [[{c}|{alias}]] — {nodes[c]["desc"]}' if alias != c else f'{i}. [[{c}]] — {nodes[c]["desc"]}')
        out.append('')
    else:
        out += ['🏁 End of this branch.', '']
    if name != START:
        out += n['body']
    (folder / f'{name}.md').write_text('\n'.join(out), encoding='utf-8')

# graph colours: keep the user's other graph settings, replace only the colour groups
gpath = vault / '.obsidian' / 'graph.json'
gpath.parent.mkdir(parents=True, exist_ok=True)
graph = json.loads(gpath.read_text(encoding='utf-8')) if gpath.exists() else {}
graph['colorGroups'] = [{'query': q, 'color': {'a': 1, 'rgb': int(c, 16)}} for q, c in [
    ('tag:#start OR tag:#overview', 'FFFFFF'), ('tag:#plan', '30A46C'), ('tag:#junction', 'E5484D'), ('tag:#page', '3E8EF7'), ('tag:#data-list', 'F76B15'),
    ('tag:#product', 'F76B15'), ('tag:#supplier', '12A594'), ('tag:#component', 'FFC53D'), ('tag:#cve', '8E4EC6')]]
graph.update({'showArrow': True, 'hideUnresolved': True, 'showTags': False})
gpath.write_text(json.dumps(graph, indent=2), encoding='utf-8')

orphans = [n for n, v in nodes.items() if n != START and not v['parent']]
print('vault:', vault.resolve(), '| notes:', len(nodes), '| orphans:', orphans)

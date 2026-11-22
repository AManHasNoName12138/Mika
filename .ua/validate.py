#!/usr/bin/env python3
"""Check graph coverage, references and source fingerprints (stdlib only)."""
import collections
import hashlib
import json
from pathlib import Path
import sys

UA = Path(__file__).resolve().parent
ROOT = UA.parent
FILE_TYPES = {'file', 'config', 'document', 'service', 'pipeline', 'table', 'schema', 'resource', 'endpoint'}
NODE_TYPES = FILE_TYPES | {'function', 'class', 'module', 'concept'}
EDGE_TYPES = {'imports','exports','contains','inherits','implements','calls','subscribes','publishes','middleware','reads_from','writes_to','transforms','validates','depends_on','tested_by','configures','related','similar_to','deploys','serves','provisions','triggers','migrates','documents','routes','defines_schema'}

def main():
    read = lambda p: json.loads((UA / p).read_text())
    graph, scan, meta, fp = map(read, ['knowledge-graph.json', 'intermediate/scan-result.json', 'meta.json', 'fingerprints.json'])
    issues=[]
    def check(ok, message):
        if not ok: issues.append(message)
    inventory={f['path']:f for f in scan['files']}
    nodes={n['id']:n for n in graph['nodes']}
    file_nodes={n['id']:n for n in nodes.values() if n['type'] in FILE_TYPES}
    check(len(nodes)==len(graph['nodes']), 'Duplicate node IDs')
    check(set(inventory)=={n['filePath'] for n in file_nodes.values()}, 'File node coverage differs from inventory')
    check(not any(p.startswith('.ua/') for p in inventory), 'Graph artifacts were scanned recursively')
    for n in nodes.values():
        check(n['type'] in NODE_TYPES, f"Invalid node type: {n['id']}")
        check(all(n.get(k) for k in ['name','summary','tags']), f"Missing node metadata: {n['id']}")
        check(n['complexity'] in ['simple','moderate','complex'], f"Invalid complexity: {n['id']}")
        p=n.get('filePath')
        if p:
            check(p in inventory and (ROOT/p).is_file(), f'Missing source: {p}')
            if 'lineRange' in n:
                a,b=n['lineRange'];check(p in inventory and 1<=a<=b<=inventory[p]['sizeLines'], f"Invalid line range: {n['id']} {n['lineRange']}")
    keys=set();actual=set();connected=set()
    for e in graph['edges']:
        a,b,t=e['source'],e['target'],e['type'];key=(a,b,t)
        check(key not in keys, f'Duplicate edge: {key}');keys.add(key)
        check(a in nodes and b in nodes and a!=b, f'Invalid edge endpoints: {key}')
        check(t in EDGE_TYPES, f'Invalid edge type: {t}')
        check(e.get('direction') in ['forward','backward','bidirectional'], f'Invalid direction: {key}')
        check(isinstance(e.get('weight'),(int,float)) and 0<=e['weight']<=1, f'Invalid weight: {key}')
        connected.update((a,b))
        if t=='imports' and a in nodes and b in nodes:actual.add((nodes[a].get('filePath'),nodes[b].get('filePath')))
    expected={(p,q) for p,targets in scan['importMap'].items() for q in targets if p!=q}
    for pair in sorted(expected-actual):issues.append(f'Missing import: {pair}')
    assigned=collections.Counter()
    for layer in graph['layers']:
        check(all(layer.get(k) for k in ['id','name','description','nodeIds']), f"Invalid layer: {layer.get('id')}")
        for i in layer['nodeIds']:assigned[i]+=1;check(i in nodes,f'Dangling layer node: {i}')
    check(all(assigned[i]==1 for i in file_nodes), 'Every file-level node must belong to exactly one layer')
    tour=graph['tour']
    check(5<=len(tour)<=15,'Tour must have 5–15 steps')
    check([s['order'] for s in tour]==list(range(1,len(tour)+1)), 'Non-consecutive tour order')
    for s in tour:
        check(all(s.get(k) for k in ['title','description','nodeIds']), f"Incomplete tour step {s['order']}")
        check(all(i in nodes for i in s['nodeIds']), f"Dangling tour node in step {s['order']}")
    check(graph['project']['gitCommitHash']==meta['gitCommitHash']==fp['gitCommitHash'], 'Source commit metadata mismatch')
    check(meta['analyzedFiles']==scan['totalFiles']==len(inventory),'Inventory count mismatch')
    check(set(fp['files'])==set(inventory),'Fingerprint coverage mismatch')
    for p,f in fp['files'].items():
        if (ROOT/p).is_file():check(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==f['contentHash'],f'Source changed after analysis: {p}')
    report={'passed':not issues,'sourceCommit':meta['gitCommitHash'],'analyzedFiles':len(inventory),'nodes':len(nodes),'edges':len(graph['edges']),'layers':len(graph['layers']),'tourSteps':len(tour),'resolvedImports':len(expected),'fingerprintedFiles':len(fp['files']),'isolatedNodes':len(set(nodes)-connected),'fileCategories':dict(collections.Counter(f['fileCategory'] for f in inventory.values())),'nodeTypes':dict(collections.Counter(n['type'] for n in nodes.values())),'edgeTypes':dict(collections.Counter(e['type'] for e in graph['edges'])),'issues':issues}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return int(bool(issues))

if __name__=='__main__':sys.exit(main())

import json
import pickle
import numpy

data = json.load(open("idiom.json", "r"))
idioms = {}
for d in data:
  d['first'] = d['pinyin'].split()[0]
  d['last'] = d['pinyin'].split()[-1]
  idioms[d['word']] = d

pinyins = []
for i in idioms.values():
  pinyins.append(i['first'])
  pinyins.append(i['last'])

pinyins = set(pinyins)

index = {}
for pinyin in pinyins:
  index[pinyin] = []
  for i in idioms.values():
    if i['first'] == pinyin:
      index[pinyin].append(i)

def find(idex, key):
  results = index[key]
  for r in results:
    print(r['word'])

### initialize
for d in data:
  d['winrate'] = 0.5
  d['visits'] = 0

def choose(key, excludes):
  candidates = index[key]
  canditates = set(candidates) - set(excludes)
  if candidates == []:
    return 0
  winrates = np.array([c['winrate'] for c in candidates])
  visits = np.array([c['visits'] for c in candidates])
  weights = winrates / (1 + visits); weights = weights / weights.sum()
  decision = np.random.choice(candidates, 1, p = weights)[0]
  return decision

def play():
  start = np.random.choice(data, 1)[0]['last']
  sequence = []
  p = start
  while True:
    idiom = choose(p, sequence)
    if idiom == 0:
      break
    sequence.append(idiom)
    print(idiom['word'])
    p = idiom['last']
  return sequence
  

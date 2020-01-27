import json
import pickle
import numpy as np

data = json.load(open("idiom.json", "r"))
N = len(data)
words = [d['word'] for d in data]
pinyins = [d['pinyin'] for d in data]
firsts = [p.split()[0] for p in pinyins]
lasts = [p.split()[-1] for p in pinyins]

pinyins = set(firsts + lasts)
index = {}
for pinyin in pinyins:
  index[pinyin] = []
  for i in range(N):
    if firsts[i] == pinyin:
      index[pinyin].append(i)

def choose(key, player, excludes):
  candidates = index[key]
  canditates = set(candidates) - set(excludes)
  if candidates == []:
    return -1
  winrates = np.array(player['winrate'])[candidates]
  visits = np.array(player['visits'])[candidates]
  weights = winrates / (1 + visits); weights = weights / weights.sum()
  decision = np.random.choice(candidates, 1, p = weights)[0]
  return decision

### initialize a player
player = {'winrate': [0.5] * N, 'visits': [0] * N}

### play
def self_play(player):
  start = np.random.choice(lasts, 1)[0]
  sequence = []
  p = start
  while True:
    i = choose(p, player, sequence)
    if i == -1:
      break
    sequence.append(i)
    print(words[i])
    p = lasts[i]
  return sequence

def learn(player, sequence):
  evens, odds = sequence[::2], sequence[1::2]
  if len(sequence)%2 == 0:
    wins, loses = odds, evens
  else:
    wins, loses = evens, odds
  return(wins)






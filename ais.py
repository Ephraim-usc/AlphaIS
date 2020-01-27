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
M = len(pinyins)

index = {}
for pinyin in pinyins:
  index[pinyin] = []
  for i in range(N):
    if firsts[i] == pinyin:
      index[pinyin].append(i)

back_index = {}
for pinyin in pinyins:
  back_index[pinyin] = []
  for i in range(N):
    if lasts[i] == pinyin:
      back_index[pinyin].append(i)

def choose(key, player, excludes = []):
  candidates = index[key]
  canditates = set(candidates) - set(excludes)
  if candidates == []:
    return -1
  winrates = np.array([player['winrate'][lasts[i]] for i in canditates])
  visits = np.array([player['visits'][lasts[i]] for i in canditates])
  weights = winrates / (1 + visits); weights = weights / weights.sum()
  decision = np.random.choice(candidates, 1, p = weights)[0]
  return decision

### initialize a player
def new_player():
  buffer = {'winrate': {p:0.5 for p in pinyins}, 'visits': {p:2 for p in pinyins}}
  return buffer

### play
def self_play(player):
  start = np.random.choice(lasts, 1)[0]
  sequence = []
  p = start
  while True:
    i = choose(p, player)
    if i == -1:
      break
    sequence.append(i)
    #print(words[i])
    p = lasts[i]
  return sequence

def learn(player, sequence):
  evens, odds = sequence[::2], sequence[1::2]
  if len(sequence)%2 == 0:
    wins, loses = odds, evens
  else:
    wins, loses = evens, odds
  
  for i in wins:
    p = lasts[i]
    player['winrate'][p] = (player['winrate'][p] * player['visits'][p] + 1) / (player['visits'][p] + 1)
    player['visits'][p] += 1
  
  for i in loses:
    p = lasts[i]
    player['winrate'][p] = (player['winrate'][p] * player['visits'][p]) / (player['visits'][p] + 1)
    player['visits'][p] += 1

def train(player, n):
  for i in range(n):
    s = self_play(player)
    learn(player, s)
    print(i)

### play
def play(player1, player2):
  start = np.random.choice(lasts, 1)[0]
  sequence = []
  p = start
  print("start pinyin: " + str(p))
  while True:
    i = choose(p, player1)
    if i == -1:
      break
    sequence.append(i)
    p = lasts[i]
    print("player 1 gives: " + str(words[i]))
    print("player 1 current win rate: " + str(player1['winrate'][p]))
    i = choose(p, player2)
    if i == -1:
      break
    sequence.append(i)
    p = lasts[i]
    print("player 2 gives: " + str(words[i]))
    print("player 2 current win rate: " + str(player2['winrate'][p]))
  return sequence


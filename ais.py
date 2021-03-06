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

def choose_train(key, player, excludes = []):
  candidates = index[key]
  canditates = set(candidates) - set(excludes)
  if candidates == []:
    return -1
  winrates = np.array([player['winrate'][lasts[i]] for i in canditates])
  visits = np.array([player['visits'][lasts[i]] for i in canditates])
  weights = np.power(winrates, 2) / (1 + visits)
  weights = weights / weights.sum()
  decision = np.random.choice(candidates, 1, p = weights)[0]
  return decision

def choose_match(key, player, excludes = []):
  candidates = index[key]
  canditates = set(candidates) - set(excludes)
  if candidates == []:
    return -1
  winrates = np.array([player['winrate'][lasts[i]] for i in canditates])
  weights = np.power(winrates, 3)
  weights = weights / weights.sum()
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
    i = choose_train(p, player)
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

def refresh(player):
  player['visits'] = {p:2 for p in pinyins}

### play
def play(player1, player2):
  start = np.random.choice(lasts, 1)[0]
  p = start
  print("start pinyin: " + str(p))
  while True:
    i = choose_match(p, player1)
    if i == -1:
      return 0
    p = lasts[i]
    print("Black gives: " + str(words[i]) + " current win rate: " + str(player1['winrate'][p]))
    i = choose_match(p, player2)
    if i == -1:
      return 1
    p = lasts[i]
    print("White gives: " + str(words[i]) + " current win rate: " + str(player2['winrate'][p]))
  return -1

def play_(player1, player2):
  start = np.random.choice(lasts, 1)[0]
  p = start
  while True:
    i = choose_match(p, player1)
    if i == -1:
      return 0
    p = lasts[i]
    i = choose_match(p, player2)
    if i == -1:
      return 1
    p = lasts[i]
  return -1

def compare(player1, player2, n):
  score = 0
  for i in range(n):
    score += play_(player1, player2)
  return score/n

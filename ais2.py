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
  candidates = set(candidates) - set(excludes)
  if candidates == set():
    return -1
  winrates = np.array([player['winrate'][lasts[i]] for i in candidates])
  weights = np.power(winrates, 2) + 0.001
  weights = weights / weights.sum()
  decision = np.random.choice(list(candidates), 1, p = weights)[0]
  return decision

def choose_match(key, player, excludes = []):
  candidates = index[key]
  candidates = set(candidates) - set(excludes)
  if candidates == set():
    return -1
  winrates = np.array([player['winrate'][lasts[i]] for i in candidates])
  weights = winrates == winrates.max()
  weights = weights / weights.sum()
  decision = np.random.choice(list(candidates), 1, p = weights)[0]
  return decision

### initialize a player
def new_player():
  buffer = {'winrate': {p:0.5 for p in pinyins}}
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
    player['winrate'][p] = (player['winrate'][p] * 9 + 1) / 10
  
  for i in loses:
    p = lasts[i]
    player['winrate'][p] = (player['winrate'][p] * 9) / 10

def train(player, n):
  for i in range(n):
    s = self_play(player)
    learn(player, s)
    print(i)

### play
def play(player1, player2, verbose = True):
  while True:
    start = np.random.choice(lasts, 1)[0]
    if index[start] != []:
      break
  p = start
  history = set()
  if verbose: print("start pinyin: " + str(p))
  while True:
    i = choose_match(p, player1, history)
    if i == -1:
      return 0
    p = lasts[i]
    history.add(i)
    if verbose: print("Black gives: " + str(words[i]) + " last: " + str(p) +
                      " Win rate: " + str(player1['winrate'][p]))
    i = choose_match(p, player2, history)
    if i == -1:
      return 1
    p = lasts[i]
    history.add(i)
    if verbose: print("White gives: " + str(words[i]) + " last: " + str(p) +
                      " Win rate: " + str(player2['winrate'][p]))
  return -1


def compare(player1, player2, n = 100):
  score = 0
  for i in range(n):
    score += play(player1, player2, verbose = False)
  return score/n

### human 

def new_strong_player():
  player = {'winrate': {p:0.5 for p in pinyins}}
  wins = set()
  loses = set()
  index_ = index.copy()
  back_index_ = back_index.copy()
  
  for i in range(3):
    for p in pinyins:
      if index_[p] == []:
        wins.add(p)
    
    for q in range(20):
      buffer = [back_index_[p] for p in wins]
      buffer = [i for sublist in buffer for i in sublist]
      buffer = set([firsts[i] for i in buffer])
      buffer = buffer - wins - loses
      loses = loses.union(buffer)
      
    for p in pinyins:
      for i in index_[p]:
        if lasts[i] in loses:
          index_[p].remove(i)
  
  for p in wins:
    player['winrate'][p] = 1
  for p in loses:
    player['winrate'][p] = 0
  return player

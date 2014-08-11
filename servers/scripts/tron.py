#!/usr/bin/python -u
# coding: utf8
import random
import time
import sys
import threading
import big
import re

rows = 17
cols = 17

idP1 = sys.argv[1]
idP2 = sys.argv[2]

nameP1 = "Player " + idP1
nameP2 = "Player " + idP2

lastinputP1 = "right"
lastinputP2 = "left"

def opposite(x,y):
  if (x.startswith("left") and y.startswith("right")) or (x.startswith("right") and y.startswith("left")) or (x.startswith("down") and y.startswith("up")) or (x.startswith("up") and y.startswith("down")):
    return True
  return False

def escape(x):
 return re.sub(r'([\"])', r'\\\1', x)

running = True

def input():
  global lastinputP1, lastinputP2, nameP1, nameP2, running
  while running:
    inp = sys.stdin.readline().strip().split("\t")
    if len(inp) == 3:
      if inp[1] == idP1:
        nameP1 = escape(inp[2])
      elif inp[1] == idP2:
        nameP2 = escape(inp[2])
    else:
      if inp[0] == idP1:
        if not opposite(inp[1], lastinputP1):
          lastinputP1 = inp[1]
      elif inp[0] == idP2:
        if not opposite(inp[1], lastinputP2):
          lastinputP2 = inp[1]

def broadcast(s):
  print("broadcast \"" + s + "\"")
  sys.stdout.flush()

threading.Thread(target=input).start()

air = "▢"
snakeP1 = "▩"
snakeP2 = "▦"
food = "■"
br = "\\n"

try:
  broadcast(big.big("Tron"))
  time.sleep(2)
  print("status")
  broadcast(big.big("by DoNe"))
  time.sleep(2)
  broadcast(nameP2 + " (▩) vs " + nameP1 + " (▦)!")
  time.sleep(4)
  while running:
    board = [[0 for x in range(cols)] for x in range(rows)]

    headxP1 = cols/2+4
    headyP1 = rows/2
    board[headyP1][headxP1] = 3
    board[headyP1][headxP1-1] = 2
    board[headyP1][headxP1-2] = 1
    scoreP1 = 0

    headxP2 = cols/2-4
    headyP2 = rows/2
    board[headyP2][headxP2] = -3
    board[headyP2][headxP2+1] = -2
    board[headyP2][headxP2+2] = -1
    scoreP2 = 0

    board[cols/2][rows/2] = 500
    gameover = False
    sleeptime = 0.2

    lastinputP1 = "right"
    lastinputP2 = "left"

    while not gameover:
      display = ""
      for row in range(rows):
        for col in range(cols):
          if board[row][col] == 0:
            display += air
          elif board[row][col] > 0 and board[row][col] < 500:
            display += snakeP1
          elif board[row][col] < 0:
            display += snakeP2
          elif board[row][col] == 500:
            display += food
        display += br
      display = display[:-2]
      broadcast(display)

      time.sleep(sleeptime)

      newHeadxP1 = headxP1
      newHeadyP1 = headyP1
      newHeadxP2 = headxP2
      newHeadyP2 = headyP2

      if lastinputP1.startswith("up"):
        newHeadyP1 -= 1
      elif lastinputP1.startswith("down"):
        newHeadyP1 += 1
      elif lastinputP1.startswith("left"):
        newHeadxP1 -= 1
      else:
        newHeadxP1 += 1

      if lastinputP2.startswith("up"):
        newHeadyP2 -= 1
      elif lastinputP2.startswith("down"):
        newHeadyP2 += 1
      elif lastinputP2.startswith("left"):
        newHeadxP2 -= 1
      else:
        newHeadxP2 += 1

      failP1 = False
      failP2 = False

      if newHeadyP1 < 0 or newHeadyP1 >= rows or newHeadxP1 < 0 or newHeadxP1 >= cols or (board[newHeadyP1][newHeadxP1] > 0 and board[newHeadyP1][newHeadxP1] < 500) or board[newHeadyP1][newHeadxP1] < 0:
        failP1 = True

      if newHeadyP2 < 0 or newHeadyP2 >= rows or newHeadxP2 < 0 or newHeadxP2 >= cols or (board[newHeadyP2][newHeadxP2] > 0 and board[newHeadyP2][newHeadxP2] < 500) or board[newHeadyP2][newHeadxP2] < 0:
        failP2 = True
      if newHeadxP1 == newHeadxP2 and newHeadyP1 == newHeadyP2:
        failP1 = True
        failP2 = True

      if failP1 or failP2:
        gameover = True
        break

      if board[newHeadyP1][newHeadxP1] == 500 and board[newHeadyP2][newHeadxP2] != 500:
        board[newHeadyP1][newHeadxP1] = 1 + board[headyP1][headxP1]
        found = False
        while not found:
          y = random.randint(0, rows-1)
          x = random.randint(0, cols-1)
          if board[y][x] == 0:
            board[y][x] = 500
            found = True
            headxP1 = newHeadxP1
            headyP1 = newHeadyP1
      else:
        board[newHeadyP1][newHeadxP1] = 1 + board[headyP1][headxP1]
        for x in range(rows):
          for y in range(cols):
            if board[x][y] > 0 and  board[x][y] < 500:
              board[x][y] -= 1
      headxP1 = newHeadxP1
      headyP1 = newHeadyP1

      if board[newHeadyP2][newHeadxP2] == 500 and board[newHeadyP1][newHeadxP1] != 500:
        board[newHeadyP2][newHeadxP2] = -1 + board[headyP2][headxP2]
        found = False
        while not found:
          y = random.randint(0, rows-1)
          x = random.randint(0, cols-1)
          if board[y][x] == 0:
            board[y][x] = 500
            found = True
            headxP2 = newHeadxP2
            headyP2 = newHeadyP2
      else:
        board[newHeadyP2][newHeadxP2] = -1 + board[headyP2][headxP2]
        for x in range(rows):
          for y in range(cols):
            if board[x][y] < 0:
              board[x][y] += 1
      headxP2 = newHeadxP2
      headyP2 = newHeadyP2

      if failP1 or failP2:
        gameover = True
        break

    if failP1 and failP2:
      broadcast("Draw!")
    elif failP1:
      broadcast(nameP2 + " (▦)  wins!")
    elif failP2:
      broadcast(nameP1 + " (▩) wins!")
    time.sleep(2)
except KeyboardInterrupt:
  running = False

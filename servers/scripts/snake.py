#!/usr/bin/python2 -u
# coding: utf8
import random
import time
import sys
import threading
import big
import re

rows = 16
cols = 16

lastinput = "left"
running = True

idP1 = sys.argv[1]
nameP1 = "Player " + idP1

def opposite(x,y):
  if (x.startswith("left") and y.startswith("right")) or (x.startswith("right") and y.startswith("left")) or (x.startswith("down") and y.startswith("up")) or (x.startswith("up") and y.startswith("down")):
    return True
  return False

def escape(x):
 return re.sub(r'([\"])', r'\\\1', x)

def input():
  global lastinput, idP1, nameP1, running
  while running:
    inp = sys.stdin.readline().strip().split("\t")
    if len(inp) == 3:
      if inp[1] == idP1:
        nameP1 = escape(inp[2])
    else:
      if inp[0] == idP1:
        if not opposite(inp[1], lastinput):
          lastinput = inp[1]

def broadcast(s):
  print("broadcast \"" + s + "\"")
  sys.stdout.flush()

threading.Thread(target=input).start()

air = "▢"
snake = "▩"
food = "■"
br = "\\n"

try:
  broadcast(big.big("Snake"))
  time.sleep(2)
  print("status")
  broadcast(big.big("by done"))
  time.sleep(2)
  broadcast(nameP1 + " is playing!")
  time.sleep(4)
  while running:
    board = [[0 for x in range(cols)] for x in range(rows)]
    headx = cols/2
    heady = rows/2
    board[heady][headx] = 1
    board[cols/2][rows/4] = -1
    score = 0
    gameover = False
    sleeptime = 0.2

    while not gameover:
      display = ""
      for row in range(rows):
        for col in range(cols):
          if board[row][col] == 0:
            display += air
          elif board[row][col] > 0:
            display += snake
          elif board[row][col] < 0:
            display += food
        display += br
      display = display[:-2]
      broadcast(display)

      time.sleep(sleeptime)

      newHeadx = headx
      newHeady = heady

      if lastinput.startswith("up"):
        newHeady -= 1
      elif lastinput.startswith("down"):
        newHeady += 1
      elif lastinput.startswith("left"):
        newHeadx -= 1
      else:
        newHeadx += 1

      if newHeady < 0 or newHeady >= rows or newHeadx < 0 or newHeadx >= cols or board[newHeady][newHeadx] > 0:
        gameover = True
        break

      if board[newHeady][newHeadx] < 0:
        score += 1
        sleeptime *= 0.98
        board[newHeady][newHeadx] = 1 + board[heady][headx]
        found = False
        while not found:
          y = random.randint(0, rows-1)
          x = random.randint(0, cols-1)
          if board[y][x] == 0:
            board[y][x] = -1
            found = True
            headx = newHeadx
            heady = newHeady
      else:
        board[newHeady][newHeadx] = 1 + board[heady][headx]
        for x in range(rows):
          for y in range(cols):
            if board[x][y] > 0:
              board[x][y] -= 1

      headx = newHeadx
      heady = newHeady

    broadcast(big.big("Score: " + str(score)))
    time.sleep(2)
except KeyboardInterrupt:
  running = False

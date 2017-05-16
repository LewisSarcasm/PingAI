import random
import time
import socket
import json

WIDTH = 640
HEIGHT = 480

TCP_IP = "0.0.0.0"
TCP_PORT = 1337

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

ball = {
	"x": WIDTH/2,
	"y": HEIGHT/2,
	"xvel": 10 * (random.randrange(0, 2)-0.5),
	"yvel": 10 * (random.randrange(0, 2)-0.5),
	"r": 10, #radius of ball
	"color": (random.randrange(0, 0xFF), random.randrange(0, 0xFF), random.randrange(0, 0xFF))
}

bat_l = {
	"x": 5,
	"y": HEIGHT/2,
	"width": 5, # actually, half the width and height
	"height": 20,
	"speed": 8,
	"score": 0
}

bat_r = bat_l.copy()
bat_r["x"] = WIDTH - bat_r["x"]

bat_l["conn"], bat_l["addr"] = s.accept()
print("Left player connected from {}".format(bat_l["addr"]))

bat_r["conn"], bat_r["addr"] = s.accept()
print("Right player connected from {}".format(bat_r["addr"]))

def update():
	
	#if keys[K_s] and bat_l["y"] < HEIGHT - bat_l["height"]:
	#	bat_l["y"] += bat_l["speed"]
	#if keys[K_w] and bat_l["y"] > bat_l["height"]:
	#	bat_l["y"] -= bat_l["speed"]

	#if keys[K_DOWN] and bat_r["y"] < HEIGHT - bat_r["height"]:
	#	bat_r["y"] += bat_r["speed"]
	#if keys[K_UP] and bat_r["y"] > bat_r["height"]:
	#	bat_r["y"] -= bat_r["speed"]

	# wall collision
	x2 = ball["x"] + ball["xvel"]
	y2 = ball["y"] + ball["yvel"]
	
	score = False
	
	if x2 < 0:
		yint = -(ball["yvel"]/ball["xvel"]) * ball["x"] + ball["y"]
		if bat_l["y"] - bat_l["height"] < yint < bat_l["y"] + bat_l["height"]: # bounce
			x2 = -x2
			ball["xvel"] *= -1
		else: # don't bounce
			score = True
			bat_r["score"] += 1
	elif x2 > WIDTH:
		yint = (ball["yvel"]/-ball["xvel"]) * (WIDTH - ball["x"]) + ball["y"]
		if bat_r["y"] - bat_r["height"] < yint < bat_r["y"] + bat_r["height"]: # bounce
			x2 = WIDTH - (x2-WIDTH)
			ball["xvel"] *= -1
		else: # don't bounce
			score = True
			bat_l["score"] += 1
	if y2 < 0 or y2 > HEIGHT:
		ball["yvel"] *= -1
	
	ball["x"] = x2
	ball["y"] = y2

	if score:
		print("SCORE: {}/{}".format(bat_l["score"], bat_r["score"]))
		ball["x"] = WIDTH/2
		ball["y"] = HEIGHT/2
		ball["xvel"] = 10 * (random.randrange(0, 2)-0.5)
		ball["yvel"] = 10 * (random.randrange(0, 2)-0.5)

last_time = time.time()

while True:
	update()
	
	state = [bat_l.copy(), bat_r.copy(), ball]
	del state[0]["conn"]
	del state[1]["conn"]
	state = json.dumps(state).encode()
	print(state)
	bat_l["conn"].send(state)
	bat_r["conn"].send(state)
	
	current_time = time.time()
	delay = (1 / 60) - (current_time - last_time)
	last_time = current_time
	if delay > 0:
		time.sleep(delay)
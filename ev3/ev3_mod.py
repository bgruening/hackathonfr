import time
import ev3
from ev3.ev3dev import Motor


import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--turn_left', nargs=1,  help='Turn left)')
parser.add_argument('-r', '--turn_right', nargs=1,  help='Turn right)')
parser.add_argument('-w', '--wiggle', nargs=1,  help='Turn left then right by this amount')
parser.add_argument('-m','--move', nargs=1, help='Move forward')
parser.add_argument('-b','--back_move', nargs=1, help='Move backward')
args=parser.parse_args()

d=Motor(port=Motor.PORT.A)
e=Motor(port=Motor.PORT.B)

def move(milliseconds):
	setUp()
	milliseconds=int(milliseconds)
        d.run_time_limited(time_sp=milliseconds, speed_sp=40, regulation_mode=False, stop_mode=Motor.STOP_MODE.COAST, ramp_up_sp=100, ramp_down_sp=100)
        e.run_time_limited(time_sp=milliseconds, speed_sp=40, regulation_mode=False, stop_mode=Motor.STOP_MODE.COAST, ramp_up_sp=100, ramp_down_sp=100)
        time.sleep(milliseconds/1000+1)

def back_move(milliseconds):
	setUp()
	milliseconds=int(milliseconds)
        d.run_time_limited(time_sp=milliseconds, speed_sp=-40, regulation_mode=False, stop_mode=Motor.STOP_MODE.COAST, ramp_up_sp=100, ramp_down_sp=100)
        e.run_time_limited(time_sp=milliseconds, speed_sp=-40, regulation_mode=False, stop_mode=Motor.STOP_MODE.COAST, ramp_up_sp=100, ramp_down_sp=100)
        time.sleep(milliseconds/1000+1)

def turn_left(milliseconds):
	setUp()
	milliseconds=int(milliseconds)
        d.run_time_limited(time_sp=milliseconds, speed_sp=40, regulation_mode=False, stop_mode=Motor.STOP_MODE.COAST, ramp_up_sp=100, ramp_down_sp=100)
        e.run_time_limited(time_sp=milliseconds, speed_sp=-40, regulation_mode=False, stop_mode=Motor.STOP_MODE.COAST, ramp_up_sp=100, ramp_down_sp=100)
        time.sleep(milliseconds/1000+1)

def turn_right(milliseconds):
	setUp()
	milliseconds=int(milliseconds)
        d.run_time_limited(time_sp=milliseconds, speed_sp=-40, regulation_mode=False, stop_mode=Motor.STOP_MODE.COAST, ramp_up_sp=100, ramp_down_sp=100)
        e.run_time_limited(time_sp=milliseconds, speed_sp=40, regulation_mode=False, stop_mode=Motor.STOP_MODE.COAST, ramp_up_sp=100, ramp_down_sp=100)
        time.sleep(milliseconds/1000+1)

def setUp():
        d.reset()
	e.reset()

def test_run():
        d.run_mode = 'forever'
        d.regulation_mode = True
        d.pulses_per_second_sp = 200
        d.start()
        time.sleep(5)
        d.stop()

def test_run_forever():
        d.run_forever(50, regulation_mode=False)
        time.sleep(5)
        d.stop()
        d.run_forever(200, regulation_mode=True)
        time.sleep(5)
        d.stop()


if args.move:
	move(args.move[0])
elif args.back_move:
	back_move(args.back_move[0])
elif args.turn_left:
	turn_left(args.turn_left[0])
elif args.turn_right:
	turn_right(args.turn_right[0])

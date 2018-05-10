#!/usr/bin/env python
from evdev import InputDevice
from select import select
import time
import numpy as np
from common.realtime import Ratekeeper

import zmq
from cereal import car
import selfdrive.messaging as messaging
from selfdrive.services import service_list
from selfdrive.car import get_car

# ***** connect to joystick *****
dev = InputDevice("/dev/input/event8")
button_values = [0]*7
axis_values = [0.0, 0.0, 0.0]


# ***** connect to car *****
context = zmq.Context()
logcan = messaging.sub_sock(context, service_list['can'].port)
sendcan = messaging.pub_sock(context, service_list['sendcan'].port)
CI, CP = get_car(logcan, sendcan)

def read_joystick():
  # **** handle joystick ****
  r, w, x = select([dev], [], [], 0.0)

  if dev in r:
    for event in dev.read():
      # button event
      if event.type == 1:
        if event.code == 304:
          button_values[0] = int(event.value)
        elif event.code == 305: # waze?
          button_values[1] = int(event.value)
        elif event.code == 307:
          button_values[2] = int(event.value)
        elif event.code == 308:
          button_values[3] = int(event.value)
        elif event.code == 314:
          button_values[4] = int(event.value)
        elif event.code == 315:
          button_values[5] = int(event.value)

      # axis move event
      if event.type == 3:
        if event.code < 2:
          if event.code == 2:
            axis_values[event.code] = np.clip((255-int(event.value))/250.0, 0.0, 1.0)
          else:
            DEADZONE = 5
            if event.value-DEADZONE < 128 and event.value+DEADZONE > 128:
              event.value = 128
            axis_values[event.code] = np.clip((int(event.value)-128)/120.0, -1.0, 1.0)

def control_car():
  CC = car.CarControl.new_message()
  CS = CI.update(CC)
  # print CS.cruiseState
  # ['actuators', 'brakeDEPRECATED', 'cruiseControl', 'enabled', 'gasDEPRECATED', 'hudControl', 'steeringTorqueDEPRECATED']

  CC.enabled = True

  # CC.actuators.gas = float(np.clip(-axis_values[1], 0, 1.0))
  # CC.actuators.brake = float(np.clip(axis_values[1], 0, 1.0))
  CC.actuators.steerAngle = float(axis_values[1])

  CC.hudControl.speedVisible = bool(button_values[5])
  CC.hudControl.lanesVisible = bool(button_values[4])
  CC.hudControl.leadVisible = bool(button_values[3])

  CC.cruiseControl.override = bool(button_values[2])
  CC.cruiseControl.cancel = bool(button_values[0])

  CC.hudControl.setSpeed = float(axis_values[2] * 100.0)

  # TODO: test alerts
  CC.hudControl.visualAlert = "none"
  CC.hudControl.audibleAlert = "none"

  #print CC
  CI.apply(CC)


rk = Ratekeeper(100)
while 1:
  read_joystick()
  # print axis_values, button_values
  control_car()
  rk.keep_time()



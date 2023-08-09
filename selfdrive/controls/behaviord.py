#!/usr/bin/env python3

""" gets behavior input from UI and saves it to params"""
from common.params import Params
import cereal.messaging as messaging
import time

A_CRUISE_MIN = -1.2


# Update this dict and run slider_gen.py to generate the code for the sliders, params, and log.capnp
PARAMS = {
    "AccelCruiseMin": {"default": -1.2, "range": (-3.0, 0.0), "label": "Minimum Cruise Accel:", "units": "m/s<sup>2</sup>"},
    "AccelCruiseMaxFactor": {"default": 1.0, "range": (0.0, 3.0), "label": "Cruise Accel Factor:", "units": "Coef."},
    "LatAngleFactor": {"default": 0.14, "range": (0.0, 0.3), "label": "Steering Angle Factor:", "units": "Coef."},
    "LatAccelFactor": {"default": 1.0, "range": (0.0, 4.0), "label": "Lateral Accel Factor:", "units": "Coef."},
    "LatAccelOffset": {"default": 0.0, "range": (-0.2, 0.2), "label": "Lateral Accel Offset:", "units": "Coef."},
    "Friction": {"default": 0.2, "range": (0.0, .5), "label": "Friction:", "units": "Coef."},
    "SteerDelay": {"default": 0.1, "range": (0.0, 5.0), "label": "Steer Delay:", "units": "Sec."},
}

class LiveBehavior:
  def __init__(self, log=False):
    self.log = log
    self.sm = messaging.SubMaster(['behavior'])
    self.params = {param: info["default"] for param, info in PARAMS.items()}

  def update(self) -> None:
    self.sm.update(0)
    if self.sm.updated['behavior']:
      for param in PARAMS.keys():
        self.params[param] = self.get_param(param)

  def get_param(self, param: str) -> float:
    # make the first letter lowercase to match the cereal message
    lowercase_param = param[0].lower() + param[1:]
    value = getattr(self.sm['behavior'], lowercase_param)
    min_val, max_val = PARAMS[param]["range"]
    return value if min_val <= value <= max_val else PARAMS[param]["default"]

  def get_live_param(self, param: str) -> float:
    self.update()
    if self.log:
      print(f"{param}: ", self.params[param])
    return self.params[param]
  

''' Example:
lb = LiveBehavior()
x = lb.get_live_param("AccelCruiseMin")
print(x)
'''

class Behaviord:
  def __init__(self):
    self.sm = messaging.SubMaster(['behavior'])
    self.p = Params()
    self.init_params()
        
  def init_params(self):
    if any(self.p.get(param) is None for param in PARAMS):
      for param, info in PARAMS.items():
        self.p.put(param, str(info["default"]))

  def get_param(self, param: str) -> float:
    # make the first letter lowercase to match the cereal message
    lowercase_param = param[0].lower() + param[1:]
    value = getattr(self.sm['behavior'], lowercase_param)
    min_val, max_val = PARAMS[param]["range"]
    return value if min_val <= value <= max_val else PARAMS[param]["default"]

  def save(self):
    if self.sm.updated['behavior']:
      print("behavior updated")
      for param in PARAMS.keys():
        self.p.put(param, str(self.get_param(param)))

  def behaviord_thread(self):
    while True:
      self.sm.update(0)
      self.save()
      time.sleep(1)

def main():
  behaviord = Behaviord()
  behaviord.behaviord_thread()
            
if __name__ == "__main__":
  main()

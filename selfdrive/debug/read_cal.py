#!/usr/bin/env python
import json
from common.params import Params

params = Params()
calibration_params_json = params.get("CalibrationParams")
print calibration_params_json
calibration_params = json.loads(calibration_params_json)
angle_offset = calibration_params["angle_offset"]
print calibration_params

#!/bin/python3
"""
    Model for the table tb_hardware
    Created by Eric Gibert on 31 Aug 2016

    Define the IC (probes, sensors, other...) that are present on the control board.
    Each hardware will have a driver to interact with defined in the 'drivers' module
"""
from model.model import Ponicwatch_Table
from drivers.hardware_dht import Hardware_DHT
from drivers.hardware_DS18B20 import Hardware_DS18B20

class Hardware(Ponicwatch_Table):
    """
    - 'hardware_id' and 'name' identify uniquely a hardware IC within a Controller database.
    - 'mode': indicates if the switch should be 'READ' or 'WRITE' or 'R/W'
    - 'value': current state of the switch ( 0 = OFF, 1 = OFF )
    - 'hardware': serial number of the chip or other relevant identification
    - 'init': free string passed to the __init__ function to perform hardware initialization
    """
    MODE = {
        0: "READ",    # IC can only be access for reading data
        1: "WRITE",   # IC can only accessed for writing data
        2: "R/W",     # IC supports for 'read' and 'write' modes
    }

    META = {"table": "tb_hardware",
            "id": "hardware_id",
            "columns": (
                         "hardwareid", # INTEGER NOT NULL,
                         "name", #  TEXT NOT NULL,
                         "mode", #  INTEGER NOT NULL DEFAULT (0),
                         "hardware", #  TEXT NOT NULL,
                         "init", #  TEXT NOT NULL,
                         "updated_on", #  TIMESTAMP,
                         "synchro_on", #  TIMESTAMP
                        )
            }

    def __init__(self, controller, *args, **kwargs):
        super().__init__(controller.db, Hardware.META, *args, **kwargs)
        # based on the "hardware" name, associate the proper driver object
        if self["hardware"] in ["DHT11", "DHT22", "AM2302"]:
            self._IC = Hardware_DHT(pigpio=controller.pig, model=self["hardware"], pin=self["init"])
        elif self["hardware"] in ["DS18B20"]:
            self._IC = Hardware_DS18B20(pigpio=controller.pig, device_folder=self["init"])
        else:
            raise ValueError("Unknown hardware declared: {0} {1}".format(self["id"], self["hardware"]))

    def read(self, param):
        return self._IC.read(param)

    def write(self, param):
        return self._IC.write(param)

    @classmethod
    def all_keys(cls, db):
        return super().all_keys(db, Hardware.META)

    def __str__(self):
        return "{} ({})".format(self["name"], Hardware.MODE[self["mode"]])
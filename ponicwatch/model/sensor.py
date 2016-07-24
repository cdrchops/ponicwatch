#!/bin/python3
"""
    Model for the table tb_sensor.
    Created by Eric Gibert on 29 Apr 2016

    Sensors are objects linked to a hardware pin (on/off digital input) or an analog input to capture a sensor's state.
    They belong to one Controller.

    - 'sensor_id' and 'name' identify uniquely a sensor within a Controller database.
    - 'mode': analog or digital
    - 'hardware': identification of the hardware undelying the sensor. Usually a pin number within an IC.
    - 'read_value': last reading, always as float even for digital input. Float between 0.0 and 1.0 to be converted.
    - 'calculated_value': conversion of the 'read_value' to reflect the expected metric
    Note: if the peripheric already provides a converted value then 'read_value' = 'calculated_value'
"""
from datetime import datetime, timezone
class Sensor(dict):
    """

    """
    MODE = {
        0: "DIGITIAL",    # sensor mode is digital 0/1 i.e. pin input reflecting a ON/OFF or True/False i.e. contactor
        1: "ANALOG",      # sensor is connected to an ADC reading the current of a probe. Float between 0.0 and 1.0 to be converted.
        2: "DIRECT",      # sensor provides a direct reading of the true value i.e. usually specific IC connected by i2c or 1-wire protocols
    }

    _tb_sensor = (
        "sensor_id", # INTEGER NOT NULL,
        "name", # TEXT NOT NULL,
        "mode", # INTEGER NOT NULL DEFAULT (0),
        "hardware", # TEXT NOT NULL,
        "timer", # TEXT,
        "read_value", # FLOAT NOT NULL DEFAULT (0.0),
        "calculated_value", # REAL NOT NULL DEFAULT (0.0)
        "timestamp_value", #             TIMESTAMP,
        "updated_on",  #    TIMESTAMP,
        "synchro_on",  #    TIMESTAMP
    )

    def __init__(self, db, name=None, id=None):
        # dict.__init__(self, *args,**kwargs)
        self.db = db
        for col in Sensor._tb_sensor:
            self[col] = None
        if name or id:
            self.get_sensor(name=name, id=id)

    def get_sensor(self, name=None, id=None):
        """
        Fetch one record from tb_sensor matching either of the given parameters
        :param name: tb_sensor.name (string)
        :param id: tb_sensor.sensor_id (int)
        """
        with self.db.get_connection() as conn:
            curs = conn.cursor()
            try:
                if name and type(name) is str:
                    curs.execute("SELECT * from tb_sensor where name=?", (name,))
                elif id and type(id) is int:
                    curs.execute("SELECT * from tb_sensor where sensor_id=?", (id,))
                else:
                    print("No name nor id porvided:", name, id)
                    raise ValueError
                sensor_row = curs.fetchall()
                if len(sensor_row) == 1:
                    for idx, col in enumerate(Sensor._tb_sensor):
                        self[col] = sensor_row[0][idx]
                    self.hw_components = self["hardware"].split('.')  # example:"AM2302.4.T" --> ['AM2302', '4', 'T']
                    self.IC, self.pins = self.hw_components[0], self.hw_components[1]
                    self.hw_id = self.IC + '.' + self.pins #  like "AM2302.4"  pin 4 on chip AM2302
            finally:
                curs.close()

    def update_values(self, read_value, calculated_value):
        self["read_value"] = read_value
        self["calculated_value"] = calculated_value
        with self.db.get_connection() as conn:
            curs = conn.cursor()
            try:
                curs.execute("update tb_sensor set read_value=?, calculated_value=?, updated_on=? where sensor_id=?",
                             (read_value, calculated_value, datetime.now(timezone.utc), self["sensor_id"]))

            finally:
                curs.close()


    def __str__(self):
        return "{} ({})".format(self["name"], Sensor.MODE[self["mode"]])

    @classmethod
    def list_sensors(cls, db):
        sensors = []
        with db.get_connection() as conn:
            curs = conn.cursor()
            curs.execute("select sensor_id from tb_sensor")
            for id in curs.fetchall():
                sensors.append(Sensor(db, id=id[0]))
        return sensors

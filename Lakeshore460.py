#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fr, Jan 28 2022

Device server to configure and read a Lakehosre Model 460 gaussmeter.
Reads all three probe inputs and returns individual readings as well as magnitude.

@author: Michael Schneider <mschneid@mbi-berlin.de>, Max Born Institut Berlin
"""


import pyvisa as visa
import tango
from tango import DevState
from tango.server import Device, attribute, command
from tango.server import device_property
from tango import READ
import sys


class Lakeshore460(Device):

    mx = attribute(
        name='mx',
        access=READ,
        unit='mT',
        dtype=tango.DevFloat,
        format='%10.4f',
        )

    my = attribute(
        name='my',
        access=READ,
        unit='mT',
        dtype=tango.DevFloat,
        format='%10.4f',
        )

    mz = attribute(
        name='mz',
        access=READ,
        unit='mT',
        dtype=tango.DevFloat,
        format='%10.4f',
        )

    gpib_addr = device_property(
        dtype=str,
        mandatory=True,
        update_db=True,
        )

    UNIT_MULT = {'u': 1e-6, 'm': 1e-3, '': 1, 'k': 1e3}

    def init_device(self):
        Device.init_device(self)
        self.rm = visa.ResourceManager('@py')
        self.inst = self.rm.open_resource(f'GPIB::{self.gpib_addr}::INSTR')
        self.inst.clear()
        self.inst.read_termination = '\r\n'
        try:
            ans = self.inst.query('*IDN?')
            print(ans, file=self.log_info)
            if 'MODEL460' in ans:
                self.configure_device()
                self.set_state(DevState.ON)
            else:
                self.set_state(DevState.FAULT)
                sys.exit(255)
        except Exception as e:
            print(e, file=self.error_stream)
            self.inst.close()
            self.set_state(DevState.FAULT)
            sys.exit(255)
        self._fieldvalues = [0, 0, 0, 0]

    def always_executed_hook(self):
        pass

    def measure(self, ax: str) -> float:
        """Set active channel (X/Y/Z) and request single measurement"""
        print(f"In measure({ax})", file=self.log_debug)
        self.inst.write(f"CHNL {ax}")
        mag = self.UNIT_MULT[self.inst.query("FIELDM?")]
        val = float(self.inst.query("FIELD?"))
        print(f"measure {ax}: {mag} * {val}", file=self.log_debug)
        return mag * val

    def read_mx(self):
        return 1e3 * self.measure('X')

    def read_my(self):
        return 1e3 * self.measure('Y')

    def read_mz(self):
        return 1e3 * self.measure('Z')

    def configure_device(self):
        """Set all channels to Tesla"""
        for ax in "XYZ":
            self.inst.write(f"CHNL {ax}")
            self.inst.write("UNIT T")

    @command
    def reset_device(self):
        self.inst.clear()
        self.inst.write('*RST')
        self.configure_device()


if __name__ == "__main__":
    Lakeshore460.run_server()



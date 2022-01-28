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
from tango import READ, READ_WRITE
import sys
import time
import numpy as np


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

    m = attribute(
        name='m',
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

    def init_device(self):
        Device.init_device(self)
        self.rm = visa.ResourceManager('@py')
        self.inst = self.rm.open_resource(f'GPIB::{self.gpib_addr}::INSTR')
        self.inst.clear()
        try:
            ans = self.inst.query('*IDN?')
            print(ans)
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
        ans = self.inst.query('ALLF?')
        print(f'always_executed_hook -> {ans}', file=self.log_debug)
        try:
            self._fieldvalues = [float(s) for s in ans.split(',')]
        except Exception as e:
            # likely a timeout ocurred - flush buffer
            print(f'unexpected {e}: {msg} -> {ans}. Clearing buffer.',
                  file=self.log_warn)
            self.inst.clear()
        return

    def read_mx(self):
        return self._fieldvalues[0]

    def read_my(self):
        return self._fieldvalues[1]

    def read_mz(self):
        return self._fieldvalues[2]

    def read_m(self):
        return self._fieldvalues[3]

    def configure_device(self):
        pass

    @command
    def reset_device(self):
        self.inst.write('*RST')
        self.configure_device()


if __name__ == "__main__":
    Lakeshore460.run_server()



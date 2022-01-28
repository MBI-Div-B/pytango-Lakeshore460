# Lakeshore Model 460
Minimal device server for Model 460 Gaussmeter. Only provides readings for all
three probe channels, no additional settings.

## Installation
requires pyvisa and a working GPIB installation

## Configuration
Only device property is the GPIB address. It's inserted in the following pyvisa
device string:

`f'GPIB::{gpib_address}::INSTR'`

## Authors
M. Schneider, MBI Berlin

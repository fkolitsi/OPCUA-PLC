## Set the virtual environment Python3.7
```
conda activate condaenv
```

## Digital Inputs (DI):
- DI0: START BUTTON
- DI1: RUN BUTTON
- DI2: STOP BUTTON
- DI3: EMERGENCY BUTTON
- DI4: RESET BUTTON
- DI5: LOWER LEVEL FLOATER
- DI6: LOW LEVEL FLOATER
- DI7: HIGH LEVEL FLOATER
- DI8: HIGHER LEVEL FLOATER
- DI9: DISCHARGING GATE SENSOR

## Digital Outputs (DQ):
- DQ0: INPUT VALVE
- DQ1: OUTPUT VALVE
- DQ2: HEATING SYSTEM VALVE
- DQ3: MOTOR-CONTROLLED DISCHARGING GATE

## Analog Inputs (AI):
- AI0: SENSOR TEMPERATURE

## Alarms:
- A0: Tank high level
- A1: Tank low level
- A2: High temperature (>80)
- A3: Low temperature (<10)
- A4: Discharging door open
- A5: Emergency activated



### Main Procedures Logic Table

#### STARTING
| Condition                          | Action/Procedure                             | Logic (0, 1) |
|------------------------------------|----------------------------------------------|--------------|
| Start button pressed (DI0 is True) | If DI9 is True, Close motor-controlled discharging door (DQ3 = False) | 0, 1         |
| Start button pressed (DI0 is True) | Open In Valve (DQ0 = True) until DI6 is True; | 1            |
| Tank level reached (DI6 is True)   | Close In Valve (DQ0 = False)                 | 0            |

#### RUNNING
| Condition                       | Action/Procedure                          | Logic (0, 1) |
|---------------------------------|-------------------------------------------|--------------|
| DI1 is True                      | Open In Valve ; RUN button pressed                           | 1            |
| High level not reached (DI7 is False)| Continue tank filling process           | 1            |
| High level reached (DI7 is True) | Close In Valve; Start Heating System        | 0, 1         |


#### HEATING
| Condition                                   | Action/Procedure                             | Logic (0, 1) |
|---------------------------------------------|----------------------------------------------|--------------|
| Tank is full (DI7 is True)                   | Start heating process                        | 1            |
| Temperature below setpoint (AI0 < Setpoint) | Continue heating                            | 1            |
| Temperature at or above setpoint (AI0 >= Setpoint)| Stop Heating System                      | 0            |



#### DISCHARGING
| Condition                          | Action/Procedure                          | Logic (0, 1) |
|------------------------------------|-------------------------------------------|--------------|
| Start discharging process           | Open Out Valve (DQ1 = True)               | 1            |
| Low level not reached (DI6 is False)| Continue waiting for low level            | 1            |
| Low level reached (DI6 is True)     | Close Out Valve (DQ1 = False)             | 0            |


### Alarms Logic Table

| Alarm | Condition | Action | Logic (0, 1) |
| --- | --- | --- | --- |
| A0 (Tank High) | DI7 is True | Set Active | 1 |
| A1 (Tank Low) | DI5 is True | Set Active | 1 |
| A2 (Temp High) | AI0 > 80 | Set Active | 1 |
| A3 (Temp Low) | AI0 < 10 | Set Active | 1 |
| A4 (Door Open) | DI9 is True | Set Active | 1 |
| A5 (Emergency) | DI3 is True | Set Active | 1 |



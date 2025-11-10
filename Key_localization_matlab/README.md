\# Key Localization and Trajectory Mapping (MATLAB)



This MATLAB project processes CAN log data to determine the position and movement of a key fob relative to a vehicle, designed for keyless entry and localization systems.



\## Overview

\- The project reads CAN log files containing distance data from four fixed anchor points.

\- It filters and extracts relevant data fields for analysis.

\- Data is grouped into synchronized measurement sets.

\- Kalman and spike suppression filters are applied to minimize noise and stabilize readings.

\- The code then calculates:

&nbsp; - Distance of the key device from the vehicle

&nbsp; - Angles relative to each anchor point

&nbsp; - The overall trajectory of movement



\## Features

\- CAN log parsing and filtering

\- Noise suppression using Kalman and spike filters

\- Real-time distance and angle computation

\- Visualization of the movement trajectory

\- Customizable filter parameters



\## Applications

\- Automotive keyless entry and localization

\- Sensor fusion and indoor positioning studies

\- Testing and validation of distance-based localization algorithms



\## Files (example)

\- main.m

\- src/parse\_can\_log.m

\- src/kalman\_localize.m

\- src/spike\_suppress.m

\- config/anchors.mat

\- datasets/

\- outputs/



\## Author

Raviramanan V




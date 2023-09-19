# Installation
To be able to plot chart
`pip install matplotlib`

## Create and activate virtual environment
virtual environment is needed to be able to plot charts

`python -m venv .venv`
`source .venv/bin/activate`

## Deactivate venv
`deactivate`

# Usage
`python get-progress.py example.log`

## Interesting options
`-o` save result to csv file
`-p` plot range chart (work only in debug, will be fixed)

# outcome
## csv table
time,route,offset,remaining length,soc,consumption,range
01.01.1970 02:31:33.134,(01e15238),382,19729779,49.825,44.7564,19730712
01.01.1970 02:31:34.137,(01e15238),431,19729730,49.825,44.7559,19730663
01.01.1970 02:31:35.121,(01e15238),431,19729730,49.825,44.7559,19730663
01.01.1970 02:31:36.130,(01e15238),445,19729716,49.825,44.7558,19730649
## plot
tbd
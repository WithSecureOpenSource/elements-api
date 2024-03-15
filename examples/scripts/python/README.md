# Elements Integration: Python scripts

This directory contains Python scripts that implements more complex scenarios. All scripts 
are ready to go which means in most examples all you need to run them is to install 
dependencies and provide client credentials. Check source of every script to get more
detailed instruction.

All programs are distributed under Apache 2.0 license. 

## Preparing environment

To run Python programs you need to install required dependencies and provide client 
credentials. To run programs in isolation from host consider using Python virtualenv.

1. Run `pip install -r requirements.txt` to install required dependencies.
2. Add environment variable `WS_CLIENT_ID` with Elements API client id.
3. Add environment variable `WS_SECRET` with Elements API client secret.

## Running script

Each provided script contains instruction how to run it standalone including required
parameters. After setting them you can execute script, for example `python get_devices.py`.

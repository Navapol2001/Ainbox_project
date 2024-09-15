REM This script sets up the environment and runs the main.py script for the FB_ChatAI project.

REM Create the conda environment using the environment.yml file.
call conda env create -f ainbox.yml

REM Activate the 'ainbox' conda environment.
call conda activate ainbox

REM Run the main.py script.
fastapi dev main.py
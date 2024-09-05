import logging
import os
import sys
import azure.functions as func
import alcoholFinder as alcolholFinder

app = func.FunctionApp()
run_on_startup = 'pydevd' in sys.modules # Check if the debugger is attached

@app.function_name(name="findAlcoholScheduled")
@app.timer_trigger(schedule="0 30 9 * * *", arg_name="myTimer", run_on_startup=run_on_startup, use_monitor=False) 
def timer_trigger(myTimer: func.TimerRequest) -> None:
    itemCode = os.environ['ITEM_CODE']
    origin = os.environ['ORIGIN_ADDRESS']


    alcolholFinder.establishSession()
    locations = alcolholFinder.queryProduct(itemCode)
    distances = alcolholFinder.getDistanceMatrix(origin, locations)
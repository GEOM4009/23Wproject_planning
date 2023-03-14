import subprocess
import time
import threading

# Import modules
from tkinter import *
import argparse
import os
import app as server

import webbrowser

os.environ["USE_PYGEOS"] = "0"
import geopandas as gpd


# Global Variables
run_tests = False
verbose = True

default_crs = 0
planning_unit = 0  # gpd.GeoDataFrame()
planning_layers = []  # list(gpd.GeoDataFrame())


def runner():
   print("in runner")
   input("Get some input from the user now that needs a map")
   # navigate to the local Flask app
   webbrowser.open_new("http://127.0.0.1:5000/")

   job_data = server.job_queue.get()
   print("Got some data!!!!!")
   print(job_data)
   server.job_queue.task_done()


def main():

   t2 = threading.Thread(target=runner)
   t2.start()

   server.app.run(host='127.0.0.1', port=5000)



   t2.join()
   # start the Flask app as a separate process
   # p = subprocess.Popen(cmd, shell=True)
   # set up the webdriver for Chrome
   # browser  = webdriver.Chrome()


   print("All done!")
# wait for some actions to be completed
# time.sleep(5) # wait for 5 seconds

# perform some actions on the page
# title = driver.title
# print(f"The title of the page is '{title}'")

# wait for some more actions to be completed
# time.sleep(5) # wait for 5 seconds





# stop the Flask app process
# p.terminate()


if __name__ =="__main__":
   main()
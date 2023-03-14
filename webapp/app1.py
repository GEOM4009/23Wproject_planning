from flask import Flask, request
import threading
import queue

import subprocess
import time
from selenium import webdriver






app = Flask(__name__)
job_queue = queue.Queue()

@app.route('/', methods=['POST'])
def handle_request():
    job_data = request.json
    job_queue.put(job_data)
    return 'Job received'

def worker():
    while True:
        job_data = job_queue.get()

        # Do work on job_data here


        job_queue.task_done()

if __name__ == '__main__':
    num_workers = 4
    for i in range(num_workers):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    app.run(host='0.0.0.0', port=8080)

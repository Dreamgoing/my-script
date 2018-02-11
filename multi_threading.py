# coding=utf-8
import pprint
import csv
import json
import threading
import time
import Queue
from multiprocessing.dummy import Pool
import grequests
from threading import Thread
import requests


result_queue = Queue.Queue()
product_queue = Queue.Queue()




def fetch_server(args):
    res = requests.post(url, headers=header, json=data)
    result = res.json()
    result_queue.put(result)


def writer_worker():
    num = 0
    start = time.time()
    with open('./fmp_result_1.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, FIELDS)
        writer.writeheader()
        while True:
            if not result_queue.empty():
                produce =  result_queue.get()
                result_queue.task_done()
                # write process
                print num, image_id, round(time.time() - start, 2), 's'


def run_all_process():
    with open('./image_env.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for it in reader:
            product_queue.put(meterial)


def read_worker():
    while True:
        if not product_queue.empty():
            arg = product_queue.get()
            product_queue.task_done()
            fetch_server(arg[0], arg[1])


if __name__ == '__main__':
    threading_pool = Pool(7)
    threading_pool.apply_async(run_all_process, args=())
    threading_pool.apply_async(read_worker, args=())
    threading_pool.apply_async(read_worker, args=())
    threading_pool.apply_async(read_worker, args=())
    threading_pool.apply_async(read_worker, args=())
    threading_pool.apply_async(read_worker, args=())
    threading_pool.apply_async(writer_worker, args=())

    threading_pool.close()
    threading_pool.join()


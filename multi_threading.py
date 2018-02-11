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

PROD_FMP_URL = 'http://11.30.94.179:8000/faceid/v1/liveness'
TEST_FMP_URL = "http://10.104.4.50:8000/faceid/v1/liveness"
header = {
    'algo_ver': '_v3-1-16',
}

FMP_RESULT_FIELDS = ['biz_no', 'image_env', 'fmp_passed', 'detail']

result_queue = Queue.Queue()
product_queue = Queue.Queue()


def round_to_3(num):
    return round(num, 3)


def round_to_5(num):
    return round(num, 5)


def run_prod_fmp(biz_no, image_id):
    data = {
        'image_id': image_id,
        'rect': None,
        'watermark': 0
    }

    facegen = {}
    time.sleep(0.01)
    res = requests.post(PROD_FMP_URL, headers=header, json=data)
    result = res.json()

    if res.status_code != 200:
        return False, result['error']

    facegen['synthetic_face_confidence'] = round_to_3(result['graphics'])
    facegen['synthetic_face_threshold'] = round_to_3(result['graphics_threshold'])
    facegen['mask_confidence'], facegen['mask_threshold'] = \
        reduce(
            lambda x, y: (round_to_3(x[0]), round_to_3(x[1])) if x[0] > y[0] else(round_to_3(y[0]), round_to_3(y[1])),
            [
                (result['mouth_mask'], result['mouth_mask_threshold']),
                (result['righteye_mask'], result['righteye_mask_threshold']),
                (result['lefteye_mask'], result['lefteye_mask_threshold'])])
    facegen['screen_replay_confidence'] = round_to_3(result['replay'])
    facegen['screen_replay_threshold'] = round_to_3(result['replay_threshold'])

    fmp_passed = all([facegen['synthetic_face_confidence'] < facegen['synthetic_face_threshold'],
                      facegen['mask_confidence'] < facegen['mask_threshold'],
                      facegen['screen_replay_confidence'] < facegen['screen_replay_threshold']])

    result_queue.put((biz_no, image_id, fmp_passed, json.dumps(facegen)))


def writer_worker():
    num = 0
    start = time.time()
    with open('./fmp_result_1.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, FMP_RESULT_FIELDS)
        writer.writeheader()
        while True:
            if not result_queue.empty():
                biz_no, image_id, fmp_passed, detail = result_queue.get()
                result_queue.task_done()
                num += 1
                writer.writerow({'biz_no': biz_no,
                                 'image_env': image_id,
                                 'fmp_passed': fmp_passed,
                                 'detail': detail})
                print num, image_id, round(time.time() - start, 2), 's'


def run_all_fmp():
    with open('./image_env.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for it in reader:
            product_queue.put((it['biz_no'], it['image_env']))


def read_worker():
    while True:
        if not product_queue.empty():
            arg = product_queue.get()
            product_queue.task_done()
            run_prod_fmp(arg[0], arg[1])


if __name__ == '__main__':
    threading_pool = Pool(7)
    threading_pool.apply_async(run_all_fmp, args=())
    threading_pool.apply_async(read_worker, args=())
    threading_pool.apply_async(read_worker, args=())
    threading_pool.apply_async(read_worker, args=())
    threading_pool.apply_async(read_worker, args=())
    threading_pool.apply_async(read_worker, args=())
    threading_pool.apply_async(writer_worker, args=())

    threading_pool.close()
    threading_pool.join()


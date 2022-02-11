from pebble import ProcessPool
from concurrent.futures import TimeoutError
import json
import os
from sympy.ntheory import factorint
from pprint import pprint,pformat
import multiprocessing
import datetime
import humanfriendly
import time

LOCK = multiprocessing.Lock()

class cacheObj(object):
    def __init__(self, fname = "cache.json"):
        self.fname = fname
        if fname in os.listdir():
            with open(fname) as f:
                self.json = json.load(f)
        else:
            self.json = dict()

        for jkey in list(self.json.keys()):
            if type(jkey)!=int:
                self.json[int(jkey)] = self.json[jkey]
                del self.json[jkey]
                
    def save(self):
        with open(self.fname, "w") as f:
            json.dump(self.json, f)
            
def repunit(n):
    return (10**n-1)//9

def repunit_range(*args, **kwargs):
    for n in range(*args, **kwargs):
        yield repunit(n)

def repunit_factorint(n):
    return factorint(repunit(n))
def custom_callback(cache_obj, inp):
    def task_done(future):
        LOCK.acquire()
        try:
            result = future.result()  # bLOCKs until results are ready
            cache_obj.json[inp] = {
                "status" : "success",
                "value" : result
                }
        except TimeoutError as error:
            cache_obj.json[inp] = {
                "status" : "timeout",
                "value" : error.args[1]
                }
        except Exception as error:
            cache_obj.json[inp] = {
                "status" : "error",
                "value" : error.with_traceback(None)
                }
        LOCK.release()
    return task_done

class factorize_obj(object):
    def __init__(self, cap = 5000):
        self.cache = cacheObj()
        self.cap = cap
        self.pool = ProcessPool(max_workers=multiprocessing.cpu_count(), max_tasks=10)
        self.futures = dict()
    def status_dict(self):
        status_dict = {"unseen" : 0,
                       "processing": 0,
                       "timeout": 0,
                       "error": 0,
                       "success": 0}
        for i in range(0, self.cap):
            if i in self.futures and not self.futures[i].done():
                status_dict["processing"] += 1
            elif i not in self.cache.json:
                status_dict["unseen"] += 1
            else:
                status_dict[self.cache.json[i]["status"]] += 1

        return status_dict
    def best_success(self):
        return max([0] + [int(inp) for inp in f_obj.cache.json if f_obj.cache.json[inp]["status"] == "success"])
    def status(self):
        pprint(self.status_dict())
        print("Largest success:", max([0] + list(self.cache.json)))
    def process(self, timeout):
        self.trim_futures()
        for i in range(self.cap):
            if i in self.futures:
                continue
            if i not in self.cache.json or self.cache.json[i]["status"] != "success":
                future = self.pool.schedule(repunit_factorint, args=[i], timeout=timeout)
                future.add_done_callback(custom_callback(self.cache, i))
                self.futures[i] = future
    def trim_futures(self):
        self.futures = {i:f for i,f in self.futures.items() if not f.done()}
    def save(self):
        LOCK.acquire()
        self.cache.save()
        LOCK.release()
            
if __name__ == "__main__":
    CAP = 6000
    f_obj = factorize_obj(cap = CAP)
    
    for i in range(3, 28):
        timeout_secs = 2**i
        timeout_msg = humanfriendly.format_timespan(datetime.timedelta(seconds = timeout_secs))
        print("Starting run with timeout:", timeout_msg)
        
        fs = f_obj.process(timeout_secs)

        inc = 10
        sd = dict()
        for i in range(inc, -1, -1):
            while True:                
                last_sd = sd
                sd = f_obj.status_dict()
                if sd["processing"]*inc <= CAP*i and sd["processing"] < CAP:
                    if sd != last_sd:
                        perc = round(100*(CAP - sd["processing"])/CAP,1)
                        print(f"\t{perc}% complete")
                        print("\t\t" + pformat(f_obj.status_dict()))
                        print("\t\tLargest success:", max([int(inp) for inp in f_obj.cache.json if f_obj.cache.json[inp]["status"] == "success"]))
                    break
                
                time.sleep(5)
            
            f_obj.save()
                


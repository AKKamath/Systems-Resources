#!/usr/bin/python
import sys, time, random, string
from multiprocessing import Process, Manager
import time, pylibmc

NR_KEYS = int(sys.argv[1])
KEY_SIZE = int(sys.argv[2])
BLOAT = int(sys.argv[3])
NR_SECONDS = int(sys.argv[4])

print 'NR_KEYS', NR_KEYS
print 'KEY_SIZE',KEY_SIZE
print 'BLOAT',BLOAT
print 'NR_SECONDS',NR_SECONDS

BLOAT = (NR_KEYS * BLOAT) / 100
keys = [x for x in range(NR_KEYS)]
random.shuffle(keys)

db_keys = []

def populate_keys(thread_idx, nr_threads):
	val = ''
	for i in range(KEY_SIZE - 10):
		val = val + '.'

	#r = redis.StrictRedis(host='localhost', port=6379, db=0)
	mc = pylibmc.Client(["127.0.0.1"], binary=True,
                                behaviors={"tcp_nodelay": True,
                                "ketama": True})

	keys_per_thread = NR_KEYS/nr_threads;
	start_idx = thread_idx * keys_per_thread;
	end_idx = start_idx + keys_per_thread;

	for idx in range(start_idx, end_idx):
		s = str(keys[idx]).zfill(10)
		#mc[s]= val;
		mc.set(s, val);

def remove_keys(thread_idx, nr_threads):
	#r = redis.StrictRedis(host='localhost', port=6379, db=0)
	mc = pylibmc.Client(["127.0.0.1"], binary=True,
                                behaviors={"tcp_nodelay": True,
                                "ketama": True})
	keys_per_thread = BLOAT / nr_threads
	start_idx = thread_idx * keys_per_thread
	end_idx = start_idx + keys_per_thread
	for key in range(start_idx, end_idx):
		s = str(keys[min(NR_KEYS - key, NR_KEYS -1)]).zfill(10)
		#del mc[s]
		mc.delete(s)

def init_keys_db():
	for key in range(NR_KEYS):
		if key % 100 != 99:
			db_keys.append(key)
		else:
			pass
	random.shuffle(db_keys)

def del_small_keys():
	nr_deletions = len(db_keys) / 4
	nr_total = len(db_keys)
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	for idx in range (nr_deletions):
		key = str(db_keys[nr_total-idx]).zfill(10)
		r.delete(key)

def read_memcached(thread_idx, ns):
	#r = redis.StrictRedis(host='localhost', port=6379, db=0)
	mc = pylibmc.Client(["127.0.0.1"], binary=True,
                                behaviors={"tcp_nodelay": True,
                                "ketama": True})
	t_end = time.time() + NR_SECONDS
	ops = 0
	skip = 0
	VALID_KEYS = NR_KEYS - BLOAT
	idx = random.randint(0, VALID_KEYS)
	#idx = 102430
	#print 'VALID_KEYS', VALID_KEYS
	while time.time() < t_end:
		key = str(keys[idx]).zfill(10)
		idx = (idx+1) % VALID_KEYS
		mc.get(key)
		ops += 1

	ns.ops += ops
	ns.skip += skip

if __name__ == '__main__':
        ns = Manager().Namespace()
        ns.ops = 0
        ns.skip = 0
        nr_threads = 2 # change this param if it keeps crashing
        procs = []
        procs = []
	
	print 'starting'
        #---populate the database first
        for i in range(nr_threads):
                p = Process(target = populate_keys, args=(i, nr_threads))
                procs.append(p)
                p.start()
        for p in procs:
                p.join()
        procs = []

	print 'populated'

        time.sleep(5)
        #---delete the specified fraction
        for i in range(nr_threads):
                p = Process(target = remove_keys, args=(i, nr_threads))
                procs.append(p)
                p.start()
        for p in procs:
                p.join()
        procs = []
	
	print 'deleted'

	#time.sleep(20)

	print 'operations start'
	
	for i in range(0, nr_threads):
		p = Process(target=read_memcached, args=(i, ns))
		procs.append(p)
		p.start()

	for p in procs:
		p.join()

	print('Ops: %d Throughput: %d Skip: %d' %(ns.ops, ns.ops/NR_SECONDS, ns.skip/NR_SECONDS))
	#Flush the database before exiting.
	#r = redis.StrictRedis(host='localhost', port=6379, db=0)
	mc = pylibmc.Client(["127.0.0.1"], binary=True,
                                behaviors={"tcp_nodelay": True,
                                "ketama": True})	
	mc.flush_all()

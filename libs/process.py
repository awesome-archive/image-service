# coding: utf-8

from multiprocessing import Process
from signal import signal, SIGTERM
from setproctitle import setproctitle

import os, sys, time

try:
    base_proc_title = 'python %s' % sys.argv[0]
except:
    base_proc_title = ''

def set_current_proc_title(title, name = ''):
    """ 设置当前进程标题 """

    title = '%s %s %s' % (base_proc_title, name, title) if name != '' \
        else '%s %s' % (base_proc_title, title)

    setproctitle(title)


class ProcessPool(object):
    """ 进程池 """

    def __init__(self):

        self._master_pid = os.getpid()

        self._workers = {}
        self._exiting_workers = []

    def signal_handler(self, signum, frame):
        pid = os.getpid()

        if pid == self._master_pid:

            for worker_pid, process_tuple in self._workers.items():

                process, proc, arg = process_tuple

                self._exiting_workers.append(worker_pid)

                os.kill(worker_pid, 9)

                del self._workers[worker_pid]

        os.kill(pid, 9)

    def map(self, proc, iterable):

        signal(SIGTERM, self.signal_handler)

        for arg in iterable:
            self._create_process(proc, arg)

        self._wait_workers()

    def _create_process(self, proc, arg):

        process = Process(target = proc, args = (arg,))
        process.start()

        self._workers[process.pid] = (process, proc, arg)

    def _wait_workers(self):

        while len(self._workers) > 0:

            pid, status = os.wait()

            process, proc, arg = self._workers[pid]

            del self._workers[pid]

            if pid not in self._exiting_workers:

                self._create_process(proc, arg)

            time.sleep(0.1)

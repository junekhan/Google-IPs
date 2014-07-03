# -*- coding: utf-8 -*-
#!/usr/bin/env python
__author__ = 'jacky'

import urllib2
import re
import threading
import httplib
import urlparse

avlist = []
unlist = []


class Dispatcher(object):
    def __init__(self):
        self.thread_pool = []
        self.sem = threading.BoundedSemaphore(16)

        fd = open("./README.md", "r")
        content = fd.read()
        fd.close()
        self.urllist = re.findall(r'http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', content)
        list_len = len(self.urllist)
        print list_len
        for i in range(0, list_len):
            self.thread_pool.append(Fetcher(urlparse.urlparse(self.urllist[list_len - i - 1]).hostname, self.sem))

    def go(self):
        i = 0
        for each in self.thread_pool:
            self.sem.acquire(blocking=1)
            i += 1
            each.start()
            if i % 100 == 0:
                print 'process %d' % i
        print 'over'
        i = 0
        for each in self.thread_pool:
            i += 1
            if each.isAlive(): each.join()
            print 'process %d' % i


class Fetcher(threading.Thread):
    def __init__(self, url, sem):
        threading.Thread.__init__(self)
        self.url = url
        self.sem = sem
        self.conn = httplib.HTTPSConnection(url, timeout=3)

    def run(self):
        try:
            # retval = urllib2.urlopen(self.url, timeout=3)
            self.conn.request("GET", "/")
            avlist.append(self.url)
        except IOError:
            pass
        except BaseException as e:
            print 'Unexpected error occure'
        finally:
            self.sem.release()


if __name__ == '__main__':
    dpt = Dispatcher()
    dpt.go()
    for each in avlist:
        print "https://" + each



#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: tan
# @Date:   2015-08-17 19:00:47
# @Last Modified by:   tan
# @Last Modified time: 2015-08-21 18:19:19

import csv
import requests
import Queue
import threading
import time
from router_crawler import RouterCrawler
from router_crawler import Error_addr

class WorkManager(object):
    """线程池管理类，用于管理路由器抓取线程"""

    self.FUNC_NAME = ['crawl', 'dns']

    @staticmethod 
    def valid_ip(address):
        """验证IP是否合法"""
        try: 
            socket.inet_aton(address)
            return True
        except:
            return False

    def __init__(self, data_in_path, data_out_path, thread_num, func, *dns):
        """初始化任务队列和线程队列"""
        self.file_lock = threading.Lock()
        self.work_queue = Queue.Queue()
        self.threads = []
        self.target_list = []
        target_num = self.data_in(data_in_path)
        #print target_num
        self.data_out_path = data_out_path
        self.__init_work_queue(func, target_num, self.target_list, *dns)
        self.__init_thread_pool(thread_num)

    def __init_work_queue(self, func, target_num, target_list, *dns):
        if func == 'crawl':
            for x in xrange(target_num):
                self.add_works(self.crawler, target_list[x])
        else:
            for x in xrange(target_num):
                self.add_works(self.dns, [target_list[x], dns[0], dns[1]])

    def __init_thread_pool(self, thread_num):
        for x in xrange(thread_num):
            self.threads.append(Work(self.work_queue))
            #print len(self.threads)

    def crawler(self, target):
    #target sample: ['ip', port, 'username', 'passwd']
        #try:
        #print target
        try:
            crawler_thread = RouterCrawler(addr = target[0], port = target[1], name = target[2], passwd = target[3])
            router_info = crawler_thread.crawl()
            self.data_out(self.data_out_path, router_info)
        except Error_addr, e:
            print e
        # for (k,v) in  router_info.items():
        #     print k, ' ', v

    def dns(self, target):
    #target sample: [['ip', port, 'username', 'passwd'], '8.8.4.4', '8.8.8.8']
        pass

    def data_out(self, file_path, router_info):
        self.file_lock.acquire()
        csvfile = file(file_path, 'ab')
        writer = csv.writer(csvfile)
        router_row = []
        #由于Python字典是无序的，这里手动遍历，获得全部内容，格式如下
        # router_info = {
        #         'url': url,
        #         'status': '',
        #         'router_server': '',
        #         'router_realm': '',
        #         'username': '',
        #         'passwd': '',
        #         'fm_version': '',
        #         'hm_version': '',
        #         'dns': ''
        #         }
        columns = ['url', 'status', 'router_server', 'router_realm', 'username', 'passwd', 'fm_version', 'hm_version', 'dns']
        try:
            for column in columns:
                if column in router_info:
                    router_row.append(router_info[column])
                else:
                    router_info.append('')
            writer.writerow(router_row)
        except Exception, e:
            pass
        csvfile.close()
        self.file_lock.release()

    def data_in(self, file_path):
        self.tartget_list = []
        csvfile = file(file_path, 'rb')
        reader = csv.reader(csvfile)
        row_len = 0
        for line in reader:
            target = []
            if (self.valid_ip(line[0])):
                target.append(line[0])
            else:
                break
            if (0 < port and port < 65432):
                target.append(80)
            else:
                break
            target.append('admin')
            target.append('admin')
            self.target_list.append(target)
            row_len += 1
        return row_len

    def add_works(self, func, args):
        self.work_queue.put((func, args))

    def check_queue(self):
        return self.work_queue.qsize()

    def wait_all(self):
        for x in self.threads:
            while x.isAlive():
                #x.join()
                print self.check_queue(), 'threads reaming'
                time.sleep(5)

class Work(threading.Thread):
    """路由器信息抓取线程"""

    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.start()

    def run(self):
        while True:
            try:
                crawl_func, target = self.work_queue.get(block=False)
                crawl_func(target)
                self.work_queue.task_done()
            except Exception, e:
                #raise e
                #抛出异常，说明任务队列已经被清空
                break

if __name__ == '__main__':

    data_in_path = './ip.csv'
    data_out_path = './out.csv'
    work_manager =  WorkManager(data_in_path, data_out_path, thread_num = 3)
    work_manager.wait_all()

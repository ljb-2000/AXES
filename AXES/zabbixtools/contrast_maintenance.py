#!/usr/bin/env python
# encoding: utf-8

import time
import models_mongodb as db


def contrast():
    url = "http://123.59.6.164/api_jsonrpc.php"
    for i in db.getMaintenance(url):
        hour = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())).split(' ')[1].split(':')
        hour_sec = int(hour[0]) * 3600 + int(hour[1]) * 60 + int(hour[2])
        start_time = i['timeperiods'][0]['start_time']
        status = i['status']
        time_now = int(time.time())
        last = i['timeperiods'][0]['period']
        till_time = start_time + last
        if time_now <= i['active_till']:
            if i['timeperiods'][0]['timeperiod_type'] == '2':
                if hour_sec >= start_time and hour_sec <= till_time:
                    flag = 0
                    if status == 0:
                        print 'error %s' %i['name']
                    else:
                        pass
            elif i['timeperiods'][0]['timeperiod_type'] == '3':
                dayofweek = i['timeperiods'][0]['dayofweek']
                dayofweek = binToDec(dayofweek)
                dayofweek_list = []
                dayofweek_list.append(str(len(dayofweek)))
                flag = len(dayofweek)
                for j in dayofweek[1:]:
                    flag -= 1
                    if j == '1':
                        dayofweek_list.append(str(flag))
                week_now = time.strftime('%w', time.localtime(time.time()))
                if week_now in dayofweek_list:
                    if hour_sec >= start_time and hour_sec <= till_time:
                        flag = 0
                        if status == 0:
                            print 'error %s' %i['name']
                        else:
                            pass
            elif i['timeperiods'][0]['timeperiod_type'] == '4':
                month_now = time.strftime('%m', time.localtime(time.time()))
                month_now = int(month_now)
                if month_now == i['timeperiods'][0]['month']:
                    day_now = int(time.strftime('%d', time.localtime(time.time())))
                    if hour_sec >= start_time and hour_sec <= till_time:
                        if day_now == int(i['timeperiods'][0]['day']):
                            if status == 0:
                                print 'error %s' %i['name']
                            else:
                                pass


def binToDec(num):
    return bin(num).split('0b')[1]

if __name__ == '__main__':
    while True:
        contrast()
        time.sleep(60)

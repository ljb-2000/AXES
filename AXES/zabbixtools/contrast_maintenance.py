#!/usr/bin/env python
# encoding: utf-8

import time
import models_mongodb as db
import smtplib
from email.mime.text import MIMEText
import MySQLdb
import ConfigParser
import os
pathdir = os.getcwd()

mail_host = "AXES.com"
mail_postfix = "AXES.cyou"
mail_user = "AXESMail"
mail_passwd = "AXESMail"
mail_to_who = ['15145880789@163.com', 'lixiang_dev@cyou-inc.com', 'zhaolei@cyou-inc.com']


def getIPList():
    url = []
    try:
        conn = MySQLdb.connect(host='127.0.0.1', user="root", passwd="root", db="AXESDatabases", port=3306)
        cur = conn.cursor()
        sql_str = "select url from systemmanage_zabbixurl;"
        cur.execute(sql_str)
        for result in cur.fetchall():
            url.append("http://:" + result[0] + "/api_jsonrpc.php")
        cur.close()
        conn.close()
    except MySQLdb.Error, e:
        print 'Erro %s' %e
    return url


def contrast(config):
    #  url = "http://123.59.6.164/api_jsonrpc.php"
    urls = getIPList()
    config.read(os.path.join(pathdir, 'config.conf'))
    options = config.options('contrast')
    for url in urls:
        for i in db.getMaintenance(url):
            hour = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())).split(' ')[1].split(':')
            hour_sec = int(hour[0]) * 3600 + int(hour[1]) * 60 + int(hour[2])
            start_time = i['timeperiods'][0]['start_time']
            status = i['status']
            time_now = int(time.time())
            last = i['timeperiods'][0]['period']
            till_time = start_time + last
            if i['name'] not in options or int(config.get('contrast', i['name'])) <= 2:
                if time_now <= i['active_till']:
                    if i['timeperiods'][0]['timeperiod_type'] == '2':
                        if hour_sec >= start_time and hour_sec <= till_time:
                            if status == 0:
                                sub = u"%s维护期间已到" %i['name']
                                content = u"您未开始维护,请确认无更新维护"
                                #  sent_email(sub, content)
                                if i['name'] not in options:
                                    config.set(i['name'], '0')
                                    config.write(open(os.path.join(pathdir, 'config.conf')))
                                else:
                                    value = int(config.get('contrast', i['name']), 'w+')
                                    value += 1
                                    config.set(i['name'], str(value))
                                    config.write(open(os.path.join(pathdir, 'config.conf'), 'w+'))
                            else:
                                continue
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
                                if status == 0:
                                    sub = u"%s维护期间已到" %i['name']
                                    content = u"您未开始维护,请确认无更新维护"
                                    #  sent_email(sub, content)
                                    if i['name'] not in options:
                                        config.set('contrast', i['name'], '0')
                                        config.write(open(os.path.join(pathdir, 'config.conf'), 'w+'))
                                    else:
                                        value = int(config.get('contrast', i['name']))
                                        value += 1
                                        config.set('contrast', i['name'], str(value))
                                        config.write(open(os.path.join(pathdir, 'config.conf'), 'w+'))
                                else:
                                    continue
                    elif i['timeperiods'][0]['timeperiod_type'] == '4':
                        month_now = time.strftime('%m', time.localtime(time.time()))
                        month_now = int(month_now)
                        if month_now == i['timeperiods'][0]['month']:
                            day_now = int(time.strftime('%d', time.localtime(time.time())))
                            if hour_sec >= start_time and hour_sec <= till_time:
                                if day_now == int(i['timeperiods'][0]['day']):
                                    if status == 0:
                                        sub = u"%s维护期间已到" %i['name']
                                        content = u"您未开始维护,请确认无更新维护"
                                        #  sent_email(sub, content)
                                        if i['name'] not in options:
                                            config.set('contrast', i['name'], '0')
                                            config.write(open(os.path.join(pathdir, 'config.conf'), 'w+'))
                                        else:
                                            value = int(config.get('contrast', i['name']))
                                            value += 1
                                            config.set('contrast', i['name'], str(value))
                                            config.write(open(os.path.join(pathdir, 'config.conf'), 'w+'))
                                    else:
                                        continue


def binToDec(num):
    return bin(num).split('0b')[1]


def sent_email(sub, content):
    me = "<" + mail_user + "@" + mail_postfix + ">"
    msg = MIMEText(content, _subtype="plain", _charset="utf-8")
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ';'.join(mail_to_who)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user, mail_passwd)
        server.sendmail(me, mail_to_who, msg.as_string())
        server.close()
        return True
    except Exception, e:
        print str(e)
        return False

if __name__ == '__main__':
    config = ConfigParser.ConfigParser()
    while True:
        contrast(config)
        time.sleep(2)

#!/usr/bin/env python
# encoding: utf-8

import pymongo
import scriptzabbixapi as zabbixapi
import MySQLdb


def getIPList():
    ip = []
    try:
        conn = MySQLdb.connect(host='localhost', user="root", passwd="root", db="AXESDatabases", port=3306)
        cur = conn.cursor()
        sql_str = "select url from systemmanage_zabbixurl;"
        cur.execute(sql_str)
        for result in cur.fetchall():
            ip.append(result[0])
        cur.close()
        conn.close()
    except MySQLdb.Error, e:
        print 'Erro %s' %e
    return ip


def connDB():
    conn = pymongo.MongoClient('127.0.0.1', 27017)
    db = conn.AXES
    return db


def saveHostData(ip, url):
    db = connDB()
    collections = 'zabbix' + ip.split('.')[3].split(':')[0]
    result = zabbixapi.getHostInfo(url)['result']
    hosts = db[collections].host
    hosts.insert(result)


def saveTemplateData(ip, url):
    db = connDB()
    collections = 'zabbix' + ip.split('.')[3].split(':')[0]
    result = zabbixapi.getTemplateInfo(url)['result']
    templates = db[collections].template
    templates.insert(result)


def saveGroupData(ip, url):
    db = connDB()
    collections = 'zabbix' + ip.split('.')[3].split(':')[0]
    result = zabbixapi.getGroupInfo(url)['result']
    groups = db[collections].host_group
    groups.insert(result)


def saveProxyData(ip, url):
    db = connDB()
    collections = 'zabbix' + ip.split('.')[3].split(':')[0]
    result = zabbixapi.getProxyInfo(url)['result']
    proxys = db[collections].proxy
    proxys.insert(result)


if __name__ == '__main__':
    ip_list = getIPList()
    for ip in ip_list:
        url = "http://" + ip + "/api_jsonrpc.php"
        saveHostData(ip, url)
        saveTemplateData(ip, url)
        saveGroupData(ip, url)
        saveProxyData(ip, url)

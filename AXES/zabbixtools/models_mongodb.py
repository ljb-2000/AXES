#!/usr/bin/env python
# encoding: utf-8

import pymongo
import ConfigParser
import re
import os
import zabbixapi
ip_regular = "(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])"
port_regular = ip_regular + ":\d{2,5}"
pathdir = os.getcwd()


def connDB(collection, document):
    conf = ConfigParser.ConfigParser()
    conf.read(os.path.join(pathdir, 'config.conf'))
    dbname = conf.get('mongodb', 'database')
    port = conf.get('mongodb', 'port')
    host = conf.get('mongodb', 'host')

    client = pymongo.MongoClient(host, int(port))

    db = client[dbname][collection][document]
    return db


def processUrl(url):
    ip = re.search(port_regular, url).group() if re.search(port_regular, url) else re.search(ip_regular, url).group()
    ip = ip.split('.')[3].split(':')[0]
    collection = ''.join(['zabbix', ip])
    return collection


def getHost(url, host_id=None, host_name=None, group_id=None, group_name=None):
    collection = processUrl(url)
    db = connDB(collection, 'host')
    if host_id:
        return db.find_one({'hostid': host_id})
    elif host_name:
        return db.find_one({'host': host_name})
    elif group_id:
        return db.find({'groups.groupid': group_id})
    elif group_name:
        return db.find({'groups.name': group_name})
    else:
        return db.find()


def regexGetHost(url, group_name):
    collection = processUrl(url)
    db = connDB(collection, 'host')
    return db.find({'groups.name': {'$regex': group_name}})


def getGroup(url, group_id=None, group_name=None):
    collection = processUrl(url)
    db = connDB(collection, 'host_group')
    if group_id:
        return db.find_one({'groupid': group_id})
    elif group_name:
        return db.find_one({'name': group_name})
    else:
        return db.find()


def getTemplate(url, template_name=None, template_host=None):
    collection = processUrl(url)
    db = connDB(collection, 'template')
    if template_name:
        return db.find_one({'name': template_name})
    elif template_host:
        return db.find_one({'host': template_host})
    else:
        return db.find()


def getProxy(url):
    collection = processUrl(url)
    db = connDB(collection, 'proxy')
    return db.find()


def getLog(url):
    collection = processUrl(url)
    db = connDB(collection, 'log')
    return db.find()


def insertLog(url, log):
    collection = processUrl(url)
    db = connDB(collection, 'log')
    db.insert(log)


def createHost(url, document):
    collection = processUrl(url)
    db = connDB(collection, 'host')
    db.insert(document)


def updateHost(url, host_id, update):
    collection = processUrl(url)
    db = connDB(collection, 'host')
    db.update({"hostid": host_id}, update)


def updateGroup(url, name, group_id):
    collection = processUrl(url)
    db = connDB(collection, 'host_group')
    db.update({"groupid": group_id}, {"$set": {"name": name}})
    host_db = connDB(collection, 'host')
    host_db.update({"groups.groupid": group_id}, {"$set": {"groups.$.name": name}})


def updateGroupHostCount(url, group_id=None):
    collection = processUrl(url)
    db = connDB(collection, 'host_group')
    if group_id:
        count = len(zabbixapi.getGroupInfo(url, group_id=group_id)['result'][0]['hosts'])
        db.update({"groupid": group_id}, {"$set": {"hosts": count}})
    else:
        all_group = db.find()
        for group in all_group:
            count = len(zabbixapi.getGroupInfo(url, group_id=group['groupid'])['result'][0]['hosts'])
            db.update({"groupid": group['groupid']}, {"$set": {"hosts": count}})


def updateProxy(url, proxy_id=None):
    collection = processUrl(url)
    db = connDB(collection, 'proxy')
    if proxy_id:
        update = zabbixapi.getProxyInfo(url, proxy_id)['result'][0]
        db.update({'proxyid': proxy_id}, update)
    else:
        all_proxy = db.find()
        for proxy in all_proxy:
            print proxy['proxyid']
            update = zabbixapi.getProxyInfo(url, proxy['proxyid'])['result'][0]
            db.update({'proxyid': proxy['proxyid']}, update)


def manageStatus(url, host_id, status):
    collection = processUrl(url)
    db = connDB(collection, 'host')
    db.update({"hostid": host_id}, {"$set": {"status": status}})


def updateTemplate(url, update, template_id):
    collection = processUrl(url)
    db = connDB(collection, 'template')
    db.update({'templateid': template_id})


def createGroup(url, document):
    collection = processUrl(url)
    db = connDB(collection, 'host_group')
    db.insert(document)


def deleteGroup(url, group_ids):
    collection = processUrl(url)
    db = connDB(collection, 'host_group')
    for gid in group_ids:
        db.remove({"groupid": gid})


def deleteHost(url, host_name=None, group_id=None, host_id=None):
    collection = processUrl(url)
    db = connDB(collection, 'host')
    if group_id:
        db.remove({"groups.groupid": group_id})
    elif host_name:
        db.remove({"host": host_name})
    elif host_id:
        if isinstance(host_id, list):
            for id in host_id:
                db.remove({"hostid": id})
        else:
            db.remove({"hostid": host_id})


def createMaintenance(url, document):
    collection = processUrl(url)
    db = connDB(collection, 'maintenance')
    db.insert(document)


def getMaintenance(url, name=None):
    if name:
        collection = processUrl(url)
        db = connDB(collection, 'maintenance')
        return db.find_one({'name': name})
    else:
        collection = processUrl(url)
        db = connDB(collection, 'maintenance')
        return db.find()


def delMaintenance(url, name):
    collection = processUrl(url)
    db = connDB(collection, 'maintenance')
    db.remove({"name": name})


def changeMaintenanceStatus(url, name, status):
    collection = processUrl(url)
    db = connDB(collection, 'maintenance')
    db.update_one({'name': name}, {"$set": {"status": status}})

if __name__ == '__main__':
    db = connDB('zabbix164', 'host')
    result = getTemplate('http:123.59.6.164/aaa')
    for i in result:
        print i
    #  print db.find_one()
    #  result = getHost('http:123.59.6.164/aaa')
    #  for i in result:
    #  print i

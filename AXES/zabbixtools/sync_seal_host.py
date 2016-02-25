#!/usr/bin/env python
# encoding: utf-8
import MySQLdb
import urllib
import urllib2
import json
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
path = os.getcwd()


def getDBProjectData():
    project_list = []
    try:
        conn = MySQLdb.connect(host='127.0.0.1', user="root", passwd="root", db="AXESDatabases", port=3306, charset='utf8')
        try:
            cur = conn.cursor()
            sql_str = u"select game_name_cn from systemmanage_game"
            cur.execute(sql_str)
        except Exception, e1:
            print e1
    except Exception, e2:
        print e2
    else:
        for result in cur.fetchall():
            project_name_cn = result[0]
            project_list.append(project_name_cn)
        cur.close()
        conn.close()
    return project_list


def getDataFromSeal(project_name):
    url = u"http://seal.cyou-inc.com/a/application/deviceInterface/getDeviceInfo/assetInfo?"
    project_name = urllib.urlencode({'productName': project_name.decode('utf-8')})
    url += project_name
    request_data = urllib2.Request(url, '')
    header = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; rv:16.0) Gecko/20100101 Firefox/16.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Connection': 'keep-alive'
    }
    for key in header:
        request_data.add_header(key, header[key])
    try:
        data = urllib2.urlopen(request_data)
    except Exception as e:
        print e
    else:
        return json.loads(data.read())


def getDataFromTxt():
    with open('hostlist.txt', 'r') as f:
        project_list = f.readlines()
    return project_list


def main():
    dicts = {}
    if os.path.isfile(os.path.join(path, 'hostlist.txt')):
        os.remove(os.path.join(path, 'hostlist.txt'))
    game = getDBProjectData()
    for project in game:
        project_info = getDataFromSeal(project)
        dicts[project] = project_info
    strs = json.dumps(dicts)
    with open('hostlist.txt', 'a+') as f:
        f.write(strs)


if __name__ == '__main__':
    main()
    #  getDataFromTxt()

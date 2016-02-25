#!/usr/bin/env python
# encoding: utf-8
import urllib
import urllib2
import MySQLdb
import json
import zabbixapi
import models_mongodb as db
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def getSealData(project_name):
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


def getDBProjectData():
    project_dict = {}
    project_list = []
    try:
        conn = MySQLdb.connect(host='127.0.0.1', user="root", passwd="root", db="AXESDatabases", port=3306, charset='utf8')
        try:
            cur = conn.cursor()
            sql_str = u"select game_name_cn, game_name_py from systemmanage_game"
            cur.execute(sql_str)
        except Exception, e1:
            print e1
    except Exception, e2:
        print e2
    else:
        for result in cur.fetchall():
            project_name_cn = result[0]
            project_name_py = result[1]
            project_dict['name_cn'] = project_name_cn
            project_dict['name_py'] = project_name_py
            project_list.append(project_dict)
            project_dict = {}
        cur.close()
        conn.close()
    return project_list


def getDBIDCData(idc_name_cn):
    try:
        conn = MySQLdb.connect(host='127.0.0.1', user="root", passwd="root", db="AXESDatabases", port=3306, charset='utf8')
        try:
            cur = conn.cursor()
            sql_str = u"select ip, idc_name_py, proxy_name from systemmanage_idc where idc_name_cn='%s'" %idc_name_cn
            cur.execute(sql_str)
        except Exception, e1:
            print e1
    except Exception, e2:
        print e2
    else:
        for result in cur.fetchall():
            idc_ip = result[0]
            idc_name_py = result[1]
            proxy_name = result[2]
        cur.close()
        conn.close()
    return (idc_ip, idc_name_py, proxy_name)


def getUrl():
    url = []
    try:
        conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root', db='AXESDatabases', port=3306, charset='utf8')
        try:
            cur = conn.cursor()
            sql_str = u"select url from systemmanage_zabbixurl"
            cur.execute(sql_str)
        except Exception, e1:
            print e1
    except Exception, e2:
        print e2
    else:
        for result in cur.fetchall():
            url.append("http://" + result[0] + "/api_jsonrpc.php")
        cur.close()
        conn.close()
    return url


def main():
    project =getDBProjectData()
    urls = getUrl()
    for url in urls:
        tmp_list = []
        template_name = db.getTemplate(url)
        for template in template_name:
            tmp = re.split(' |_', template['host'])
            tmp_list.append(tmp)
        for i in project:
            hostlists = []
            project_info = getSealData(i['name_cn'])
            group_list = zabbixapi.getGroupInfo(url)['result']
            group_list = [{'groupid': k['groupid'], 'name': k['name']} for k in group_list]
            for k in group_list:
                if k['name'].split('_')[0] == i['name_cn']:
                    hostlist = zabbixapi.getHostInfo(url, group_id=k['groupid'])['result']
                    for m in hostlist:
                        hostlists.append(m['host'])
            for j in project_info:
                if j['idcName']:
                    flag = False
                    idc_name_cn = ''.join(list(j['idcName'])[0:2]).decode('utf8')
                    idc_name_cn = u'木樨园' if idc_name_cn == u'木樨' else idc_name_cn
                    ip_type = getDBIDCData(idc_name_cn)[0]
                    host = j[ip_type].split(';')[0]
                    if host:
                        if host in hostlists:
                            hostinfo = db.getHost(url, host_name=host)
                            host_id = hostinfo['hostid']
                            status = j['statue']
                            function = j['function']
                            sub_function = j['subFunction']
                            idc_name_py = getDBIDCData(idc_name_cn)[1]
                            proxy_name = getDBIDCData(idc_name_cn)[2]
                            group_no = j['serverGroupNo']
                            host_name = processHostName(i['name_py'], j['wanIpTd'].split(';')[0], group_no, idc_name_py, status, function, sub_function)
                            group_name = processGroup(i['name_cn'], status, function)
                            print group_name
                            proxy_id = processProxy(url, proxy_name)
                            template_name = hostinfo['parentTemplates'][0]['name']
                            template_old = db.getTemplate(url, template_name=template_name)['host']
                            template_old_id = db.getTemplate(url, template_name=template_name)['templateid']
                            template_now = ""
                            for m in tmp_list:
                                if function.capitalize() != 'Other':
                                    if i['name_py'] in m and function.upper() in m:
                                        template_now = '_'.join(m)
                                    else:
                                        template_now = 'zabbix_for_PRC_linux'
                                else:
                                    if i['name_py'] in m:
                                        for n in m:
                                            if re.search(n, sub_function):
                                                template_now = '_'.join(m)
                                        if not template_now:
                                            template_now = 'zabbix_for_PRC_linux'
                                    else:
                                        template_now = 'zabbix_for_PRC_linux'
                            template_new = template_old_id
                            group_new = hostinfo['groups'][0]['name']
                            proxy_id_new = hostinfo['proxy_hostid']
                            name_new = hostinfo['name']
                            if host_name != hostinfo['name']:
                                flag = True
                                name_new = host_name
                            if group_name != hostinfo['groups'][0]['name']:
                                flag = True
                                group_new = group_name
                            if proxy_id != hostinfo['proxy_hostid']:
                                flag = True
                                proxy_id_new = proxy_id
                            #  if template_old != template_now:
                                #  flag = True
                                #  template_new = db.getTemplate(url, template_host=template_now)['templateid']
                            if zabbixapi.isGroup(url, group_new):
                                group_info = zabbixapi.getGroupInfo(url, group_new)
                                group_id = group_info['result'][0]['groupid']
                            else:
                                group_info = zabbixapi.createGroup(url, group_new)
                                group_id = group_info['result']['groupids'][0]
                            if flag:
                                print 'have %s' %host
                                info = updateHost(url, host_id, host, name_new, template_old, template_new, group_id, proxy_id_new)
                                print info
                        else:
                            status = j['statue']
                            function = j['function']
                            sub_function = j['subFunction']
                            idc_name_py = getDBIDCData(idc_name_cn)[1]
                            proxy_name = getDBIDCData(idc_name_cn)[2]
                            group_no = j['serverGroupNo']
                            host_name = processHostName(i['name_py'], j['wanIpTd'].split(';')[0], group_no, idc_name_py, status, function, sub_function)
                            group_name = processGroup(i['name_cn'], status, function)
                            if zabbixapi.isGroup(url, group_name):
                                group_info = zabbixapi.getGroupInfo(url, group_name)
                                group_id = group_info['result'][0]['groupid']
                            else:
                                group_info = zabbixapi.createGroup(url, group_name)
                                group_id = group_info['result']['groupids'][0]
                            proxy_id = processProxy(url, proxy_name)
                            template_now = ""
                            for m in tmp_list:
                                if function.capitalize() != 'Other':
                                    if i['name_py'] in m and function.upper() in m:
                                        template_now = '_'.join(m)
                                    else:
                                        template_now = 'zabbix_for_PRC_linux'
                                else:
                                    if i['name_py'] in m:
                                        for n in m:
                                            if re.search(n, sub_function):
                                                template_now = '_'.join(m)
                                        if not template_now:
                                            template_now = 'zabbix_for_PRC_linux'
                                    else:
                                        template_now = 'zabbix_for_PRC_linux'
                            if template_now:
                                template_id = db.getTemplate(url, template_host=template_now)['templateid']
                            else:
                                template_id = db.getTemplate(url, template_host='zabbix_for_PRC_linux')['templateid']
                            print group_id
                            info = createHost(url, host, host_name, group_id, proxy_id, template_id)
                            print 'do not have %s' %host
                            print info


def createHost(url, host, name, group_id, proxy_id, template_id):
    auth_code = zabbixapi.auth(url)
    method = "host.create"
    interfaces = [{"type": 1, "main": 1, "useip": 1, "ip": host, "dns": "", "port": "10050"}]
    params = {
        "host": host,
        "name": name,
        "interfaces": interfaces,
        "groups": [{
            "groupid": group_id,
        }],
        "templates": [{
            "templateid": template_id,
        }],
        "proxy_hostid": proxy_id
    }
    new_host_infos = zabbixapi.processData(url, method, params, auth_code)
    if 'error' in new_host_infos:
        error = zabbixapi.processLogData('create host', new_host_infos['error'], url, params, 'error')
        db.insertLog(url, log=error)
    else:
        success = zabbixapi.processLogData('create host', new_host_infos['result'], url, params, 'success')
        db.insertLog(url, log=success)
        document = zabbixapi.getHostInfo(url, host_name=host)['result'][0]
        db.createHost(url, document)
    return new_host_infos


def updateHost(url, host_id, host, name_new, template_old, template_new, group_new, proxy_new):
    auth_code = zabbixapi.auth(url)
    method = "host.update"
    params = {
        "hostid": host_id,
        "templates_clear": [{
            "templateid": template_old,
        }],
    }
    print zabbixapi.processData(url, method, params, auth_code)
    params = {
        "hostid": host_id,
        "host": host,
        "name": name_new,
        "templates": [{
            "templateid": template_new,
        }],
        "groups": [{
            "groupid": group_new,
        }],
        "proxy_hostid": proxy_new,
    }
    update_info = zabbixapi.processData(url, method, params, auth_code)
    if 'error' in update_info:
        error = zabbixapi.processLogData('update host', update_info['error'], url, params, 'error')
        db.insertLog(url, log=error)
    else:
        success = zabbixapi.processLogData('update host', update_info['result'], url, params, 'success')
        db.insertLog(url, log=success)
        document = zabbixapi.getHostInfo(url, host_id=host_id)['result'][0]
        db.updateHost(url=url, host_id=host_id, update=document)
    return update_info


def processHostName(project, host, group_no, idc_name_py, status, function, sub_function):
    if group_no:
        host_name = '_'.join([project, idc_name_py, group_no, host])
    else:
        if function == u'Other':
            sub_str = sub_function if sub_function else 'None'
            host_name = '_'.join([project, idc_name_py, sub_str, host])
        else:
            host_name = '_'.join([project, idc_name_py, 'None', host])
    return host_name


def processGroup(project, status, function):
    if status.capitalize() == 'Online':
        group_name = '_'.join([project, function])
    elif status.capitalize() == 'Standby':
        group_name = '_'.join([project, function, 'beiji'])
    else:
        group_name = '_'.join([project, function, 'beiji'])
    return group_name


def processProxy(url, proxy_name):
    """通过机房信息，判断proxy_id"""
    all_proxy_infos = zabbixapi.getProxyInfo(url)['result']
    proxy_id = None if proxy_name == u'None' else [proxy_info['proxyid'] for proxy_info in all_proxy_infos if proxy_name == proxy_info['host']][0]
    return proxy_id


if __name__ == '__main__':
    main()
    #  a = getDBProjectData()
    #  for i in a:
    #  print i
    #  a = getSealData(u'Warframe')[0]['idcName']
    #  print a
    #  print json.dumps(a, indent=4)
    #  print getDBIDCData(u'青岛')

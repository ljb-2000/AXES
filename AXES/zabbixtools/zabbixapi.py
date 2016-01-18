#!/usr/bin/env python
# encoding: utf-8

import json
import urllib2
import MySQLdb
import sys
import re
import models_mongodb as db
from Crypto.Cipher import AES
from binascii import a2b_hex
from collections import OrderedDict
import datetime
reload(sys)
sys.setdefaultencoding('utf8')
ip_regular = "(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])"
port_regular = ip_regular + ":\d{2,5}"
the_salt = "oXg#Xk^z4GYP%SEv"
key = "UmGBaI[YuF]H=hi&"


def decrypt(password):
    cryptor = AES.new(key, AES.MODE_CBC, the_salt)
    plain_text = cryptor.decrypt(a2b_hex(password))
    return plain_text.rstrip('\0')


def auth(url):
    ip = re.search(port_regular, url).group() if re.search(port_regular, url) else re.search(ip_regular, url).group()
    try:
        conn = MySQLdb.connect(host='localhost', user="root", passwd="root", db="AXESDatabases", port=3306)
        cur = conn.cursor()
        sql_str = "select username, password from systemmanage_zabbixurl where url='%s'" %ip
        cur.execute(sql_str)
        for result in cur.fetchall():
            username = result[0]
            passwd = result[1]
        password = decrypt(passwd)
        cur.close()
        conn.close()
    except MySQLdb.Error, e:
        print 'Erro %s' %e
    data = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": username,
            "password": password
        },
        "id": 1
    }
    post_data = json.dumps(data)
    header = {"Content-Type": "application/json"}
    request_data = urllib2.Request(url, post_data)
    for key in header:
        request_data.add_header(key, header[key])
    result = urllib2.urlopen(request_data)
    auth_code = json.loads(result.read())['result']
    return auth_code


def processData(url, method, params, auth_code):
    header = {"Content-Type": "application/json"}
    data = {
        "jsonrpc": "2.0",
        "method": "",
        "params": {},
        "auth": "",
        "id": 1
    }
    data['method'] = method
    data['params'] = params
    data['auth'] = auth_code
    post_data = json.dumps(data)
    request_data = urllib2.Request(url, post_data)
    for key in header:
        request_data.add_header(key, header[key])
    try:
        result = urllib2.urlopen(request_data)
    except Exception as e:
        print e
    else:
        response = json.loads(result.read())
        return response


def processLogData(log_type, log_info, url, params, result):
    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = {}
    log['type'] = log_type
    log['info'] = log_info
    log['url'] = url
    log['detail'] = params
    log['date'] = date_time
    log['result'] = result
    return log


def createHost(url, host):
    auth_code = auth(url)
    method = "host.create"
    interfaces = [{"type": 1, "main": 1, "useip": 1, "ip": host['host_ip'].split(';')[0], "dns": "", "port": "10050"}]
    params = {
        "host": host['host_ip'].split(';')[0],
        "name": host['host_name'],
        "interfaces": interfaces,
        "groups": [{
            "groupid": host['group_id']
        }],
        "templates": [{
            "templateid": host['template_id']
        }],
        "proxy_hostid": host["proxy_id"]
    }
    new_host_infos = processData(url, method, params, auth_code)
    if 'error' in new_host_infos:
        error = processLogData('create host', new_host_infos['error'], url, params, 'error')
        db.insertLog(log=error)
    else:
        success = processLogData('create host', new_host_infos['result'], url, params, 'success')
        db.insertLog(log=success)
        document = getHostInfo(url, host_name=host['host_ip'].split(';')[0])['result'][0]
        db.createHost(url, document)
    print new_host_infos
    return new_host_infos


def createOneHost(url, host, macros=None):
    auth_code = auth(url)
    method = "host.create"
    interfaces = [{"type": 1, "main": 1, "useip": 1, "ip": host['host_ip'].split(';')[0], "dns": "", "port": "10050"}]
    group_id = host['group_id']
    template_id = host['template_id']
    groups = [{"groupid": i} for i in group_id]
    templates = [{"templateid": i} for i in template_id]
    if macros:
        params = {
            "host": host['host_ip'].split(';')[0],
            "name": host['host_name'],
            "interfaces": interfaces,
            "groups": groups,
            "templates": templates,
            "proxy_hostid": host["proxy_id"],
            "macros": macros,
        }
        new_host_infos = processData(url, method, params, auth_code)
        if 'error' in new_host_infos:
            error = processLogData('create host', new_host_infos['error'], url, params, 'error')
            db.insertLog(log=error)
        else:
            success = processLogData('create host', new_host_infos['result'], url, params, 'success')
            db.insertLog(log=success)
            document = getHostInfo(url, host_name=host['host_ip'].split(';')[0])['result'][0]
            db.createHost(url, document)
        return new_host_infos
    else:
        params = {
            "host": host['host_ip'].split(';')[0],
            "name": host['host_name'],
            "interfaces": interfaces,
            "groups": groups,
            "templates": templates,
            "proxy_hostid": host["proxy_id"]
        }
        new_host_infos = processData(url, method, params, auth_code)
        if 'error' in new_host_infos:
            error = processLogData('create host', new_host_infos['error'], url, params, 'error')
            db.insertLog(log=error)
        else:
            success = processLogData('create host', new_host_infos['result'], url, params, 'success')
            db.insertLog(log=success)
            document = getHostInfo(url, host_name=host['host_ip'].split(';')[0])['result'][0]
            db.createHost(url, document)
        return new_host_infos


def deleteHost(url, host_id=None, group_id=None):
    auth_code = auth(url)
    method = "host.delete"
    if host_id:
        params = host_id
    elif group_id:
        hosts_info = getHostInfo(url, group_id)['result']
        host_id_list = [x['hostid'] for x in hosts_info]
        params = host_id_list
    delete_info = processData(url, method, params, auth_code)
    if 'error' in delete_info:
        error = processLogData('delete host', delete_info['error'], url, params, 'error')
        db.insertLog(log=error)
    else:
        success = processLogData('delete host', delete_info['result'], url, params, 'success')
        db.insertLog(log=success)
        if host_id:
            db.deleteHost(url, host_id=host_id)
        else:
            for i in host_id_list:
                db.deleteHost(url, host_id=i)
    return delete_info


def updateHost(url, host_id, name_new, template_old, template_new, group_new, status, macros, info_dict=None):
    auth_code = auth(url)
    method = "host.update"
    params = {
        "hostid": host_id,
        "templates_clear": template_old,
    }
    print processData(url, method, params, auth_code)
    params = {
        "hostid": host_id,
        "name": name_new,
        "templates": template_new,
        "groups": group_new,
        "status": status,
        "macros": macros,
    }
    update_info = processData(url, method, params, auth_code)
    if 'error' in update_info:
        error = processLogData('delete host', update_info['error'], url, params, 'error')
        db.insertLog(log=error)
    else:
        success = processLogData('delete host', update_info['result'], url, params, 'success')
        db.insertLog(log=success)
        document = getHostInfo(url, host_id=host_id)['result'][0]
        db.updateHost(url=url, host_id=host_id, update=document)
    return update_info


def updateMacros(url, host_id, macros):
    auth_code = auth(url)
    method = "host.update"
    params = {
        "hostid": host_id,
        "macros": macros,
    }
    update_info = processData(url, method, params, auth_code)
    if 'error' in update_info:
        error = processLogData('update macros', update_info['error'], url, params, 'error')
        db.insertLog(log=error)
    else:
        success = processLogData('update macros', update_info['result'], url, params, 'success')
        db.insertLog(log=success)
        document = getHostInfo(url, host_id=host_id)['result'][0]
        db.updateHost(url=url, host_id=host_id, update=document)
    return update_info


def getHostInfo(url, group_id=None, host_name=None, host_id=None):
    auth_code = auth(url)
    method = "host.get"
    if group_id:
        params = {
            "output": ["hostid", "name", "host", "proxy_hostid", "status"],
            "selectParentTemplates": [
                "templateid",
                "name",
            ],
            "selectMacros": [
                "macro",
                "value",
            ],
            "selectGroups": [
                "groupid",
                "name"
            ],
            "groupids": group_id
        }
    elif host_name:
        params = {
            "output": ["hostid", "name", "host", "proxy_hostid", "status"],
            "selectParentTemplates": [
                "templateid",
                "name",
            ],
            "selectGroups": [
                "groupid",
                "name"
            ],
            "selectMacros": [
                "macro",
                "value",
            ],
            "filter": {
                "host": host_name
            }
        }
    elif host_id:
        params = {
            "output": ["hostid", "name", "host", "proxy_hostid", "status"],
            "selectParentTemplates": [
                "templateid",
                "name",
            ],
            "selectMacros": [
                "macro",
                "value",
            ],
            "selectGroups": [
                "groupid",
                "name"
            ],
            "hostids": host_id
        }
    else:
        params = {
            "output": ["hostid", "name", "host", "proxy_hostid", "status"],
            "selectParentTemplates": [
                "templateid",
                "name",
            ],
            "selectGroups": [
                "groupid",
                "name"
            ],
            "selectGroups": [
                "groupid",
                "name"
            ],
            "selectMacros": [
                "macro",
                "value",
            ],
        }
    host_info = processData(url, method, params, auth_code)
    return host_info


def createGroup(url, group_name):
    auth_code = auth(url)
    method = "hostgroup.create"
    params = {
        "name": group_name
    }
    new_group_infos = processData(url, method, params, auth_code)
    if 'error' in new_group_infos:
        error = processLogData('update group', new_group_infos['error'], url, params, 'error')
        db.insertLog(log=error)
    else:
        success = processLogData('update group', new_group_infos['result'], url, params, 'success')
        db.insertLog(log=success)
        document = getGroupInfo(url, group_name=group_name)['result'][0]
        document['hosts'] = len(document['hosts'])
        db.createGroup(url, document=document)
    print new_group_infos
    return new_group_infos


def deleteGroup(url, group_ids):
    auth_code = auth(url)
    method = "hostgroup.delete"
    params = group_ids
    delete_groups_info = processData(url, method, params, auth_code)
    if 'error' in delete_groups_info:
        error = processLogData('delete group', delete_groups_info['error'], url, params, 'error')
        db.insertLog(log=error)
    else:
        success = processLogData('delete group', delete_groups_info['result'], url, params, 'success')
        db.insertLog(log=success)
        db.deleteGroup(url, group_ids)
    return delete_groups_info


def updateGroup(url, group_id, group_name):
    auth_code = auth(url)
    method = "hostgroup.update"
    params = {
        "groupid": group_id,
        "name": group_name,
    }
    update_group = processData(url, method, params, auth_code)
    if 'error' in update_group:
        error = processLogData('update group', update_group['error'], url, params, 'error')
        db.insertLog(log=error)
    else:
        success = processLogData('update group', update_group['result'], url, params, 'success')
        db.insertLog(log=success)
        db.updateGroup(url, group_id=group_id, name=group_name)
    return update_group


def getGroupInfo(url, group_name=None, group_id=None):
    auth_code = auth(url)
    method = "hostgroup.get"
    if group_name:
        params = {
            "output": "extend",
            "selectHosts": ["host", "hostid", "name", "proxy_hostid", "status"],
            "filter": {
                "name": group_name
            }
        }
    elif group_id:
        params = {
            "output": "extend",
            "selectHosts": ["host", "hostid", "name", "proxy_hostid", "status"],
            "filter": {
                "groupid": group_id
            }
        }
    else:
        params = {
            "ouput": "extend",
            "selectHosts": "count"
        }
    group_info = processData(url, method, params, auth_code)
    return group_info


def getGlobalMacrosInfo(url):
    auth_code = auth(url)
    method = "usermacro.get"
    params = {
        "globalmacro": True,
        "output": "extend"
    }
    macro_info = processData(url, method, params, auth_code)
    return macro_info


def getProxyInfo(url, proxy_id=None):
    auth_code = auth(url)
    method = "proxy.get"
    if proxy_id:
        params = {
            "output": ["host"],
            "selectHosts": ["hostid", "host", "name"],
            "filter": {
                "proxy_id": proxy_id
            },
        }
    else:
        params = {
            "output": ["proxyid", "host"],
            #  "selectHosts": "extend"
            "selectHosts": ["hostid", "host", "name"],
        }
    proxy_data = processData(url, method, params, auth_code)
    return proxy_data


def getTemplateInfo(url, template_name=None):
    auth_code = auth(url)
    method = "template.get"
    if template_name:
        params = {
            "output": ["host", "name", "template"],
            "filter": {
                "name": [template_name]
            },
            "selectMacros": [
                "macro",
                "value",
                "count"
            ],
            "selectTemplates": [
                "templateid",
                "host",
                "name",
                "count"
            ],
            "selectParentTemplates": [
                "templateid",
                "host",
                "name",
                "count"
            ],
            "selectItems": [
                "itemid",
                "name",
                "description",
                "count"
            ],
        }
    else:
        params = {
            "output": ["host", "name", "template"],
            "selectMacros": [
                "macro",
                "value",
                "count"
            ],
            "selectItems": [
                "itemid",
                "name",
                "description",
                "count"
            ],
            "selectTemplates": [
                "templateid",
                "host",
                "name",
                "count"
            ],
            "selectParentTemplates": [
                "templateid",
                "host",
                "name",
                "count"
            ],
        }
    templates_info = processData(url, method, params, auth_code)
    return templates_info


def updateTemplate(url, template_id, host_new, name_new, linked_template_old, linked_template_new, macros):
    auth_code = auth(url)
    method = "template.update"
    params = {
        "templateid": template_id,
        "template_clear": linked_template_old,
    }
    clear_info = processData(url, method, params, auth_code)
    print clear_info
    params = {
        "templateid": template_id,
        "name": name_new,
        "host": host_new,
        "templates": linked_template_new,
        "macros": macros,
    }
    update_info = processData(url, method, params, auth_code)
    if 'error' in update_info:
        error = processLogData('update template', update_info['error'], url, params, 'error')
        db.insertLog(log=error)
    else:
        success = {}
        success = processLogData('update template', update_info['result'], url, params, 'success')
        db.insertLog(log=success)
        document = getTemplateInfo(url, template_name=name_new)['result'][0]
        db.createTemplate(url, template_id=template_id, update=document)
    return update_info


def getItemInfo(url, host_id=None, template_id=None):
    auth_code = auth(url)
    method = "item.get"
    if host_id:
        params = {
            "output": "extend",
            "hostids": host_id,
        }
    elif template_id:
        params = {
            "output": "extend",
            "templateids": template_id,
        }
    item_info = processData(url, method, params, auth_code)
    return item_info


def isGroup(url, group_name):
    auth_code = auth(url)
    method = "hostgroup.exists"
    params = {
        "name": group_name
    }
    is_exists = processData(url, method, params, auth_code)
    return is_exists['result']


def createMaintenance(url, params):
    auth_code = auth(url)
    method = "maintenance.create"
    print json.dumps(params, indent=4)
    create_info = processData(url, method, params, auth_code)
    if 'error' in create_info:
        error = processLogData('create maintenance', create_info['error'], url, params, 'error')
        db.insertLog(log=error)
    else:
        success = processLogData('create maintenance', create_info['result'], url, params, 'success')
        db.insertLog(log=success)
    return create_info


def getMaintenance(url, maintenanceid=None, maintenance_name=None):
    auth_code = auth(url)
    method = "maintenance.get"
    if maintenanceid:
        params = {
            "filter": {
                "maintenanceid": maintenanceid,
            },
            "selectTimeperiods": "extend",
            "selectHosts": ['name', 'host', 'hostid'],
            "selectGroups": ['groupid', 'name'],
            "output": "extend",
        }
    elif maintenance_name:
        params = {
            "filter": {
                "name": maintenance_name,
            },
            "selectTimeperiods": "extend",
            "selectHosts": ['name', 'host', 'hostid'],
            "selectGroups": ['groupid', 'name'],
            "output": "extend",
        }
    else:
        params = {
            "selectTimeperiods": "extend",
            "selectHosts": ['name', 'host', 'hostid'],
            "selectGroups": ['groupid', 'name'],
            "output": "extend",
        }
    maintenance_info = processData(url, method, params, auth_code)
    return maintenance_info


def stopMaintenance(url, maintenance_name, end_time):
    auth_code = auth(url)
    method = "maintenance.update"
    maintenance_info = getMaintenance(url, maintenance_name=maintenance_name)
    groupids = [group['groupid'] for group in maintenance_info['result'][0]['groups']]
    hostids = [host['hostid'] for host in maintenance_info['result'][0]['hosts']]
    timeperiods = maintenance_info['result'][0]['timeperiods']
    params = {
        "maintenanceid": maintenance_info['result'][0]['maintenanceid'],
        "active_since": end_time,
        "active_till": end_time,
        "timeperiods": timeperiods,
        "hostids": hostids,
        "groupids": groupids,
    }
    update_info = processData(url, method, params, auth_code)
    detail = OrderedDict()
    detail['maintenance-name'] = maintenance_name
    detail['hosts'] = ', '.join([host['name'] for host in maintenance_info['result'][0]['hosts']])
    detail['groups'] = ', '.join([group['name'] for group in maintenance_info['result'][0]['groups']])
    if 'error' in update_info:
        error = processLogData('stop maintenance', update_info['error'], url, detail, 'error')
        db.insertLog(log=error)
    else:
        success = processLogData('stop maintenance', {'maintenanceid': update_info['result']['maintenanceids'][0]}, url, detail, 'success')
        db.insertLog(log=success)
        db.changeMaintenanceStatus(url, maintenance_name, 0)
    return update_info


def startMaintenance(url, maintenance_name, active_since, active_till, start_time):
    auth_code = auth(url)
    method = "maintenance.update"
    maintenance_info = getMaintenance(url, maintenance_name=maintenance_name)
    groupids = [group['groupid'] for group in maintenance_info['result'][0]['groups']]
    hostids = [host['hostid'] for host in maintenance_info['result'][0]['hosts']]
    #  timeperiods = maintenance_info['result'][0]['timeperiods']
    #  timeperiods[0]['period'] = "86400"
    #  timeperiods[0]['start_time'] = start_time
    params = {
        "maintenanceid": maintenance_info['result'][0]['maintenanceid'],
        "active_since": active_since,
        "active_till": active_till,
        "timeperiods": [{
            "start_date": active_since,
            "start_time": start_time,
            "period": "86400",
            "timeperoid_type": 0,
        }],
        "hostids": hostids,
        "groupids": groupids,
    }
    update_info = processData(url, method, params, auth_code)
    detail = OrderedDict()
    detail['maintenance-name'] = maintenance_name
    detail['hosts'] = ', '.join([host['name'] for host in maintenance_info['result'][0]['hosts']])
    detail['groups'] = ', '.join([group['name'] for group in maintenance_info['result'][0]['groups']])
    if 'error' in update_info:
        error = processLogData('start maintenance', update_info['error'], url, detail, 'error')
        db.insertLog(log=error)
    else:
        success = processLogData('start maintenance', {'maintenanceid': update_info['result']['maintenanceids'][0]}, url, detail, 'success')
        db.insertLog(log=success)
        db.changeMaintenanceStatus(url, maintenance_name, 1)
    return update_info


def manageMonitoring(url, host_ids, status):
    auth_code = auth(url)
    method = "host.update"
    for host_id in host_ids:
        params = {
            "hostid": host_id,
            "status": status,
        }
        update_info = processData(url, method, params, auth_code)
        status_str = 'off' if status == "1" else 'up'
        if 'error' in update_info:
            error = processLogData('%s monitoring' %status_str, update_info['error'], url, params, 'error')
            db.insertLog(log=error)
        else:
            success = {}
            success = processLogData('%s monitoring' %status_str, update_info['result'], url, params, 'success')
            db.insertLog(log=success)
            db.manageStatus(url=url, host_id=host_id, status=status)


if __name__ == '__main__':
    url = "http://123.59.6.164/api_jsonrpc.php"
    print json.dumps(getMaintenance(url, maintenance_name='4442'), indent=4)
    #  print json.dumps(getGroupInfo(url, group_id="179"), indent=4)
    #  print isGroup(url, "aaa")
    #  print json.dumps(getHostInfo(url, host_id="12243"))
    #  for i in getHostInfo(url)['result']:
    #  print i
    #  print json.dumps(getTemplateInfo(url, template_name=u"Template SNMP OS Windows"), indent=4)
    #  updateMacros(url, "12159", [{"macro": "{$AAA}", "value": "123"}])
    #  print json.dumps(getHostInfo(url, host_id="12159"), indent=4)
    #  print getTemplateInfo(url)
    #  print json.dumps(getHostInfo(url, host_id="11857"), indent=4)

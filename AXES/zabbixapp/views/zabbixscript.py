#!/usr/bin/env python
# encoding: utf-8

import json
import urllib2
import urllib
import sys
import Queue
import threading
import zabbixtools.zabbixapi as zabbixapi
from systemmanage.models import Idc, Game

reload(sys)
sys.setdefaultencoding('utf8')
THREAD_NUM = 5


class MyThread(threading.Thread):

    def __init__(self, url, queue):
        super(MyThread, self).__init__()
        self.queue = queue
        self.url = url

    def run(self):
        while True:
            host = self.queue.get()
            zabbixapi.createHost(self.url, host)
            self.queue.task_done()


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


def processSealData(url, project_name, queue, template_id, server_state, function):
    data = getDataFromSeal(project_name)
    for i in data:
        if i['wanIpTd']:
            host_dict = {}
            """在线服后缀无备机，GS、DB、Other根据用户选择定义"""
            if i['statue'] == 'Online' and 'Online' in server_state:
                if i['function'] in function:
                    group_name = '_'.join([project_name, i['function']])
                else:
                    continue
            elif i['statue'] == 'Standby' and 'Standby' in server_state:
                if i['function'] in function:
                    group_name = '_'.join([project_name, i['function'], 'beiji'])
                else:
                    continue
            else:
                continue
            idc_name_cn = ''.join(list(i['idcName'])[0:2]).decode('utf8')
            if idc_name_cn == u'木樨':
                idc_name_cn = u'木樨园'
            idc = Idc.objects.get(idc_name_cn=idc_name_cn)
            game = Game.objects.get(game_name_cn=project_name)
            proxy_name = idc.proxy_name
            idc_name = idc.idc_name_py
            game_name = game.game_name_py
            """获取信息，命名host_name 项目_机房_组号_IP"""
            if i['serverGroupNo']:
                host_name = '_'.join([game_name, idc_name, i['serverGroupNo'], i['wanIpTd']])
            else:
                if i['subFunction'] == 'Billing':
                    host_name = '_'.join([game_name, idc_name, i['subFunction'], i['wanIpTd']])
                else:
                    host_name = '_'.join([game_name, idc_name, 'None', i['wanIpTd']])
            """通过机房信息，判断proxy_id"""
            all_proxy_infos = zabbixapi.getProxyInfo(url)['result']
            if proxy_name == u'None':
                proxy_id = None
            else:
                proxy_id = [proxy_info['proxyid'] for proxy_info in all_proxy_infos if proxy_name == proxy_info['host']][0]
            print proxy_id
            """获取组id，如果存在组，通过zabbix读取，不存在，创建并读取"""
            if group_name:
                if zabbixapi.isGroup(url, group_name):
                    group_info = zabbixapi.getGroupInfo(url, group_name)
                    group_id = group_info['result'][0]['groupid']
                else:
                    group_info = zabbixapi.createGroup(url, group_name)
                    group_id = group_info['result']['groupids']
            """将数据整合"""
            if group_id and host_name:
                host_dict['template_id'] = template_id
                host_dict['group_id'] = group_id
                host_dict['proxy_id'] = proxy_id
                host_dict['host_name'] = host_name
                if i['subFunction'] == 'Billing':
                    host_dict['host_ip'] = i['lanIpTd']
                else:
                    host_dict['host_ip'] = i['wanIpTd']
            else:
                continue
            print host_dict
            queue.put(host_dict)


def main(url, project_name, template_id, server_state, function):
    queue = Queue.Queue(maxsize=-1)
    for i in xrange(THREAD_NUM):
        thread = MyThread(url, queue)
        thread.setDaemon(True)
        thread.start()
    processSealData(url, project_name, queue, template_id, server_state, function)
    queue.join()

if __name__ == '__main__':
    queue = Queue.Queue()
    #  url = "http://123.59.6.164/api_jsonrpc.php"
    #  print json.dumps(zabbixapi.getGroupInfo(url, u'狩龙战纪_GS')['result'][0]['groupid'], indent=4)
    #  print zabbixapi.getTemplateInfo(url, u'Template OS Linux')['result']
    #  updateHost(url, 11270, 'tesl1t', [{"templateid": 10105}], [31], 1)
    #  print json.dumps(getGroupInfo(url, 104)['result'], indent=4)
    #  project_name = u"狩龙战纪"
    #  #  processSealData(url, project_name, queue, "10105", ['Online'], ['DB'])
    #  main(url, project_name, "10105,10104", ["Online"], ["GS"])

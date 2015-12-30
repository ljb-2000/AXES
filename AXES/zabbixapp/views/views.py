# encoding: utf-8
from django.shortcuts import render
from systemmanage.models import Game, ZabbixUrl
import zabbixtools.zabbixapi as zabbixapi
import zabbixscript
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import re
from collections import OrderedDict
import sys

reload(sys)
sys.setdefaultencoding('utf8')


def getCookieUrl(request):
    if request.COOKIES.get('url'):
        url = request.COOKIES.get('url')
    else:
        url = "http://123.59.6.164/api_jsonrpc.php"
    return url


def getUrlView(request, URL):
    if URL:
        url = "http://" + URL + "/api_jsonrpc.php"
    httpresponse = HttpResponseRedirect(reverse('isjkgamelisturl'))
    httpresponse.set_cookie(key="url", value=url)
    return httpresponse


def notjkGameListView(request):
    url = getCookieUrl(request)
    games_info = Game.objects.all()
    game_list = []
    is_exist_game = [group_name['name'].split('_')[0] for group_name in zabbixapi.getGroupInfo(url)['result']]
    is_exist_game = list(set(is_exist_game))
    for i in games_info:
        if i.game_name_cn not in is_exist_game:
            game_list.append(i)
    context_dict = {
        'list': game_list
    }
    return render(request, 'zabbixmanage/gametablenotjk.html', context_dict)


def jkGameListView(request):
    url = getCookieUrl(request)
    zabbix_url = ZabbixUrl.objects.all()
    urllist = [i.url for i in zabbix_url]
    games_info = Game.objects.all()
    game_list = []
    is_exist_game = [group_name['name'].split('_')[0] for group_name in zabbixapi.getGroupInfo(url)['result']]
    is_exist_game = list(set(is_exist_game))
    for i in games_info:
        if i.game_name_cn in is_exist_game:
            game_list.append(i)
    context_dict = {
        'list': game_list
    }
    request.session['urllist'] = urllist
    request.session['length'] = len(urllist)
    return render(request, 'zabbixmanage/gametableisjk.html', context_dict)


def templateListView(request):
    url = getCookieUrl(request)
    template_info = zabbixapi.getTemplateInfo(url)['result']
    context_dict = {
        'list': template_info,
    }
    return render(request, 'zabbixmanage/templatetable.html', context_dict)


def groupListView(request):
    url = getCookieUrl(request)
    group_info = zabbixapi.getGroupInfo(url)['result']
    context_dict = {
        'list': group_info,
    }
    return render(request, 'zabbixmanage/grouptable.html', context_dict)


def createGroupView(request):
    url = getCookieUrl(request)
    if request.method == 'POST':
        group_name = request.POST['group_name']
        zabbixapi.createGroup(url, group_name)
        return HttpResponseRedirect(reverse('grouplisturl'))
    else:
        return render(request, 'zabbixmanage/creategroup.html')


def delGroupAndHostView(request):
    url = getCookieUrl(request)
    group_ids = request.REQUEST.getlist('group_list')
    for group_id in group_ids:
        zabbixapi.deleteHost(url, group_id=group_id)
    zabbixapi.deleteGroup(url, group_ids)
    return HttpResponseRedirect(reverse('grouplisturl'))


def delGroupView(request):
    url = getCookieUrl(request)
    id_list = []
    ID = request.POST['del_ids']
    id_list.append(ID)
    zabbixapi.deleteGroup(url, id_list)
    return HttpResponseRedirect(reverse('grouplisturl'))


def delHostByNameView(request):
    url = getCookieUrl(request)
    game_name_cn = request.POST['del_names']
    groups = zabbixapi.getGroupInfo(url)['result']
    for group in groups:
        if game_name_cn == group['name'].split('_')[0]:
            zabbixapi.deleteHost(url, group_id=group['groupid'])
            zabbixapi.deleteGroup(url, [group['groupid']])
    return HttpResponseRedirect(reverse('isjkgamelisturl'))


def delHostView(request, GNAME):
    url = getCookieUrl(request)
    host_id = request.POST['del_id']
    zabbixapi.deleteHost(url, host_id=[host_id])
    return HttpResponseRedirect(reverse('grouphostlisturl', args=[GNAME]))


def delHostProjectView(request, GNAME):
    url = getCookieUrl(request)
    host_id = request.POST['del_id']
    zabbixapi.deleteHost(url, host_id=[host_id])
    return HttpResponseRedirect(reverse('hostlisturl', args=[GNAME]))


def manageHostInGroupView(request, GNAME):
    url = getCookieUrl(request)
    if request.method == 'POST':
        if 'create' in request.POST:
            game_list = [GNAME]
            template_list = zabbixapi.getTemplateInfo(url)['result']
            context_dict ={
                'list': game_list,
                'options': template_list
            }
            return render(request, 'zabbixmanage/createhost.html', context_dict)
        elif 'update' in request.POST:
            host_dict = OrderedDict()
            host_id = request.REQUEST.getlist('host_list')
            host_info = zabbixapi.getHostInfo(url, host_id=host_id)['result']
            host_ids = ';'.join([host['hostid'] for host in host_info])
            host_names = ';'.join([host['host'] for host in host_info])
            host_status = host_info[0]['status']
            host_group = ';'.join(list(set([host['groups'][0]['name'] for host in host_info])))
            host_templates = ';'.join(list(set([host['parentTemplates'][0]['name'] for host in host_info])))
            host_dict[u'id'] = host_ids
            host_dict[u'主机名称'] = host_names
            host_dict[u'主机组'] = host_group
            host_dict[u'模板'] = host_templates
            host_dict[u'主机状态'] = host_status
            context_dict = {
                'host_dict': host_dict,
            }
            return render(request, 'zabbixmanage/updatehosts.html', context_dict)
        else:
            host_id = request.REQUEST.getlist('host_list')
            zabbixapi.deleteHost(url, host_id=host_id)
            return HttpResponseRedirect(reverse('hostlisturl', args=[GNAME]))


def createHostsView(request):
    url = getCookieUrl(request)
    game_list = request.REQUEST.getlist('game_list')
    if request.method == 'POST':
        template_list = request.REQUEST.getlist('template_list')[0]
        for game in game_list:
            state_list = request.REQUEST.getlist('_'.join([game, 'state_list']))
            function_list = request.REQUEST.getlist('_'.join([game, 'function_list']))
            zabbixscript.main(url, game, template_list, state_list, function_list, )
        if len(game_list) > 1:
            return HttpResponseRedirect(reverse('grouplisturl'))
        elif len(game_list) == 1:
            return HttpResponseRedirect(reverse('hostlisturl', args=game_list))
    else:
        template_list = zabbixapi.getTemplateInfo(url)['result']
    context_dict ={
        'list': game_list,
        'options': template_list
    }
    return render(request, 'zabbixmanage/createhost.html', context_dict)


def createHostView(request):
    url = getCookieUrl(request)
    if request.method == 'POST':
        host = request.POST.get('host')
        name = request.POST.get('name')
        groups = [i for i in re.split(',|;| ', request.POST.get('group')) if i]
        groupid = []
        for group in groups:
            if zabbixapi.isGroup(url, group):
                groupid.append(zabbixapi.getGroupInfo(url, group_name=group)['result'][0]['groupid'])
            else:
                groupid.append(zabbixapi.createGroup(url, group)['result']['groupids'][0])
        template = request.POST.getlist('template')
        proxyid = request.POST.get('proxy')
        host_dict = dict(zip(['host_ip', 'host_name', 'group_id', 'template_id', 'proxy_id'], [host, name, groupid, template, proxyid]))
        macros_key = request.POST.getlist('macro_key')
        macros_value = request.POST.getlist('macro_value')
        macro_dict = {}
        macros = []
        for i in zip(macros_key, macros_value):
            macro_dict = {}
            if len(i[0]) >= 1 and len(i[1]) >= 1:
                macro_dict['macro'] = i[0].strip().upper()
                macro_dict['value'] = i[1].strip()
            if macro_dict:
                macros.append(macro_dict)
        zabbixapi.createOneHost(url, host_dict, macros)
        return HttpResponseRedirect(reverse('hostinfourl', args=[host]))
    else:
        template_list = zabbixapi.getTemplateInfo(url)['result']
        global_macro = zabbixapi.getGlobalMacrosInfo(url)['result']
        proxy_list = zabbixapi.getProxyInfo(url)['result']
    context_dict = {
        "options": template_list,
        "global_macros": global_macro,
        "proxys": proxy_list,
    }
    return render(request, 'zabbixmanage/createonehost.html', context_dict)


def hostListView(request, GNAME):
    url = getCookieUrl(request)
    all_group = zabbixapi.getGroupInfo(url)['result']
    host_list = []
    host_dict = {}
    for group in all_group:
        if re.search(GNAME, group['name']):
            result =zabbixapi.getGroupInfo(url, group_name=group['name'])['result']
            host_list.append(result[0])
    for i in host_list:
        host_dict[i['name']] = i['hosts']
    proxy = zabbixapi.getProxyInfo(url)['result']
    context_dict = {
        'dict': host_dict,
        'proxy': proxy,
        'game_name': GNAME,
    }
    return render(request, 'zabbixmanage/hostlist.html', context_dict)


def groupHostListView(request, GNAME):
    url = getCookieUrl(request)
    result = zabbixapi.getGroupInfo(url, group_name=GNAME)['result']
    group_id = result[0]['groupid']
    host_infos = zabbixapi.getHostInfo(url, group_id=group_id)['result']
    proxy = zabbixapi.getProxyInfo(url)['result']
    group_name = result[0]['name']
    game_name = result[0]['name'].split('_')[0]
    context_dict = {
        'list': host_infos,
        'group_name': group_name,
        'proxy': proxy,
        'game_name': game_name,
    }
    return render(request, 'zabbixmanage/grouphostlist.html', context_dict)


def updateTemplateView(request, TNAME):
    url = getCookieUrl(request)
    result = zabbixapi.getTemplateInfo(url, template_name=TNAME)['result'][0]
    is_linked_template = result['parentTemplates']
    template_old_id_list = [template['templateid'] for template in is_linked_template]
    if request.method == 'POST':
        template_old = [{'templateid': template_old_id_list[i]} for i in xrange(len(template_old_id_list))]
        template_id = request.POST.get('template_id')
        host_new = request.POST.get('template_host')
        name_new = request.POST.get('template_name')
        template_new_list = request.POST.getlist('linked_template_list')
        template_old_list = request.POST.getlist('is_linked_template_list')
        template_new_list[0:0] = template_old_list
        template_new = [{'templateid': template_new_list[i]} for i in xrange(len(template_new_list))]
        if 'update' in request.POST:
            macros_key = request.POST.getlist('macro_key')
            macros_value = request.POST.getlist('macro_value')
            macros = []
            for i in zip(macros_key, macros_value):
                macro_dict = {}
                if len(i[0]) >= 1 and len(i[1]) >= 1:
                    macro_dict['macro'] = i[0].strip().upper()
                    macro_dict['value'] = i[1].strip()
                if macro_dict:
                    macros.append(macro_dict)
            zabbixapi.updateTemplate(url, template_id, host_new, name_new, template_old, template_new, macros)
        return HttpResponseRedirect(reverse('updatetemplateurl', args=[TNAME]))
    else:
        template_list = zabbixapi.getTemplateInfo(url)['result']
        macros_list = result['macros']
        macros_flag = len(macros_list)
        global_macro = zabbixapi.getGlobalMacrosInfo(url)['result']
        item_list = zabbixapi.getItemInfo(url, template_id=result['templateid'])['result']
    context_dict = {
        "template_dict": result,
        "options": template_list,
        "TNAME": TNAME,
        "is_linked": template_old_id_list,
        "is_linked_list": is_linked_template,
        'macros_flag': macros_flag,
        "global_macros": global_macro,
        "item_list": item_list,
    }
    return render(request, 'zabbixmanage/updatetemplate.html', context_dict)


def oneHostInfoView(request, HNAME):
    url = getCookieUrl(request)
    result = zabbixapi.getHostInfo(url, host_name=HNAME)['result'][0]
    template_current = result['parentTemplates']
    key = ['templateid' for i in range(len(template_current))]
    value = [template['templateid'] for template in template_current]
    template_old = [{key[i]: value[i]} for i in xrange(len(key))]
    if request.method == 'POST':
        template_ids = []
        host_id = request.POST.get(u'id')
        host_name = request.POST.get(u'主机名称')
        name = request.POST.get(u'可见名称')
        group_name = request.POST.get(u'主机组')
        group = [zabbixapi.getGroupInfo(url, group_name=group_name)['result'][0]['groupid']]
        templates = request.POST.get(u'模板')
        if len(templates):
            templates = templates.split(',')
        else:
            templates = []
        if templates:
            for template in templates:
                template = template.strip()
                template_dict = {}
                for template_info in zabbixapi.getTemplateInfo(url, template)['result']:
                    template_id = template_info['templateid']
                    template_dict['templateid'] = template_id
                template_ids.append(template_dict)
        status = request.POST[u'主机状态']
        if 'update' in request.POST:
            macros_key = request.POST.getlist('macro_key')
            macros_value = request.POST.getlist('macro_value')
            macro_dict = {}
            macros = []
            for i in zip(macros_key, macros_value):
                macro_dict = {}
                if len(i[0]) >= 1 and len(i[1]) >= 1:
                    macro_dict['macro'] = i[0].strip().upper()
                    macro_dict['value'] = i[1].strip()
                if macro_dict:
                    macros.append(macro_dict)
            zabbixapi.updateHost(url, host_id, name, template_old, template_ids, group, status, macros)
        elif 'del-macro' in request.POST:
            macros = []
            macros_list = result['macros']
            del_macro_list = request.REQUEST.getlist('macro_list')
            macros = [macro for macro in macros_list if macro.get('macro') not in del_macro_list]
            zabbixapi.updateHost(url, host_id, name, template_old, template_ids, group, status, macros)
        return HttpResponseRedirect(reverse('hostinfourl', args=[host_name]))
    else:
        host_dict = OrderedDict()
        template_list = []
        template_list = [template['name'] for template in result['parentTemplates']]
        host_dict[u'id'] = result['hostid']
        host_dict[u'主机名称'] = result['host']
        host_dict[u'可见名称'] = result['name']
        host_dict[u'主机组'] = result['groups'][0]['name']
        host_dict[u'模板'] = ','.join(template_list)
        host_dict[u'主机状态'] = result['status']
        item_list = zabbixapi.getItemInfo(url, host_id=result['hostid'])['result']
        macros_list = result['macros']
        macros_flag = len(macros_list)
        global_macro = zabbixapi.getGlobalMacrosInfo(url)['result']
    context_dict = {
        "global_macros": global_macro,
        'host_dict': host_dict,
        'item_list': item_list,
        'macros_list': macros_list,
        'macros_flag': macros_flag,
        'HNAME': HNAME,
        'GNAME': result['groups'][0]['name'].split('_')[0],
    }
    return render(request, 'zabbixmanage/updatehost.html', context_dict)


def proxyListView(request):
    url = getCookieUrl(request)
    result = zabbixapi.getProxyInfo(url)['result']
    for proxy in result:
        count = len(proxy['hosts'])
        proxy['count'] = count
    context_dict = {
        "proxy_dict": result,
    }
    return render(request, 'zabbixmanage/proxylist.html', context_dict)


def updateGroupView(request, GID):
    url = getCookieUrl(request)
    if request.method == 'POST':
        GNAME = request.POST['group_name']
        zabbixapi.updateGroup(url, group_id=GID, group_name=GNAME)
        return HttpResponseRedirect(reverse('updategroupurl', args=[GID]))
    else:
        result = zabbixapi.getGroupInfo(url, group_id=GID)['result'][0]
        GNAME = result['name']
    context_dict = {
        "GNAME": GNAME,
        'GID': GID,
    }
    return render(request, 'zabbixmanage/updategroup.html', context_dict)

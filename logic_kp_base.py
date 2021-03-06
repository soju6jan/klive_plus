import os, sys, traceback, re, json, threading, time, shutil, platform, urllib, requests
from datetime import datetime
from flask import request, render_template, jsonify, redirect, send_file, Response
from .plugin import P, logger, package_name, ModelSetting, LogicModuleBase, scheduler, app, SystemModelSetting, path_data, d
name = 'base'

from tool_base import ToolUtil

class LogicKPBase(LogicModuleBase):
    db_default = {
        f'{name}_db_version' : '1',
        f'{name}_auto_start' : 'False',
        f'{name}_interval' : '30',
        f'{name}_use_spotv': 'True',
        f'{name}_spotv_username': '',
        f'{name}_spotv_password': '',
        f'{name}_use_spotv_proxy': 'False',
        f'{name}_use_naver_sports': 'True',
        f'{name}_use_coupangplay': 'True',
        f'{name}_coupangplay_username': '',
        f'{name}_coupangplay_password': '',
        f'{name}_use_sstv': 'True',
        f'{name}_sstv_only_kor': 'True',
        f'{name}_use_reystream': 'True',
        f'{name}_use_naver_now': 'True',
    }

    def __init__(self, P):
        super(LogicKPBase, self).__init__(P, 'list')
        self.name = name

    def process_menu(self, sub, req):
        arg = P.ModelSetting.to_dict()
        arg['sub'] = self.name
        try:
            arg['api_m3u'] = ToolUtil.make_apikey_url(f"/{package_name}/api/base/m3u")
            arg['scheduler'] = str(scheduler.is_include(self.get_scheduler_name()))
            arg['is_running'] = str(scheduler.is_running(self.get_scheduler_name())) 
            return render_template(f'{package_name}_{name}_{sub}.html', arg=arg)
        except Exception as e:
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())
            return render_template('sample.html', title=f"{package_name}/{name}/{sub}")

    def process_ajax(self, sub, req):
        try:
            ret = {}
            if sub == 'command':
                command = req.form['command']
                if command == 'broad_list':
                    ret = {'ret':'success', 'ch_list':self.get_ch_list()}
                elif command == 'play_url':
                    data = self.get_url(req.form['arg1'], req.form['arg2'])
                    ret = {'ret':'success', 'data':{'url':data['url'], 'title':data['current']}}
            return jsonify(ret)
        except Exception as e: 
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())
            return jsonify({'ret':'danger', 'msg':str(e)})
    
    def process_api(self, sub, req):
        try:
            if sub == 'm3u':
                return self.make_m3u()
            elif sub == 'url.m3u8':
                req_source = req.args.get('source')
                req_ch_id = req.args.get('ch_id')
                url = self.get_url(req_source, req_ch_id)['url']
                if req_source == 'spotv' and ModelSetting.get_bool(f'{name}_use_spotv_proxy'):
                    url = url.replace('playlist.m3u8', 'chunklist_b6192000.m3u8')
                    url = ToolUtil.make_apikey_url(f"/{package_name}/api/base/spotv.m3u8?url={urllib.parse.quote_plus(url)}")
                return redirect(url, code=302)
            elif sub == 'spotv.m3u8':
                url = req.args.get('url')
                url = urllib.parse.unquote_plus(url)
                data = requests.get(url).text
                fix_url = url.rsplit('/', 1)[0]
                new_data = []
                tmp = re.compile(r'\.ts$', re.MULTILINE).finditer(data)
                for line in data.splitlines():
                    line = line.strip()
                    if line.endswith('.ts'):
                        ts_url = urllib.parse.quote_plus(f"{fix_url}/{line}")
                        u2 = ToolUtil.make_apikey_url(f"/{package_name}/api/base/spotv.ts?url={ts_url}")
                        new_data.append(u2)
                    else:
                        new_data.append(line)
                data = '\n'.join(new_data)
                return data
            elif sub == 'spotv.ts':
                url = req.args.get('url')
                url = urllib.parse.unquote_plus(url)
                headers = {'Connection' : 'keep-alive'}
                r = requests.get(url, headers=headers, stream=True, verify=False)
                #rv = Response(r.iter_content(chunk_size=1024), r.status_code, content_type=r.headers['Content-Type'], direct_passthrough=True)
                rv = Response(r.iter_content(chunk_size=1048576), r.status_code, content_type='video/MP2T', direct_passthrough=True)
                rv.headers.add('Content-Range', r.headers.get('Content-Range'))
                return rv
            elif sub == 'reystream.m3u8':
                for source in self.source_map:
                    if source.source_name == 'reystream':
                        return source.reystream_m3u8(req)
            elif sub == 'reystream.ts':
                for source in self.source_map:
                    if source.source_name == 'reystream':
                        return source.reystream_ts(req)
        except Exception as e: 
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())
        
    ###########################################################################
    source_map = None

    def plugin_load(self):
        from .tool import Tool
        self.source_map = Tool.source_decrypt()
        #logger.debug(self.source_map)


    def get_ch_list(self):
        ch_list = []
        for source in self.source_map:
            try:
                if ModelSetting.get_bool(f"{name}_use_{source.source_name}") == False:
                    logger.debug(f'{source.name} not use')
                    continue
                source_ch_list = source.get_list()
                if source_ch_list == None:
                    logger.debug(f'{source.name} ch_list None')
                    continue
                logger.debug(f"{source.name} {len(source_ch_list.items())}")
                for source_id, ch in source_ch_list.items():
                    ch_list.append(ch.as_dict())
            except Exception as e: 
                P.logger.error(f'Exception:{str(e)}')
                P.logger.error(traceback.format_exc())
        return ch_list


    def make_m3u(self):
        M3U_FORMAT = '#EXTINF:-1 tvg-id=\"{id}\" tvg-name=\"{title}\" tvg-logo=\"{logo}\" group-title=\"{group}\" tvg-chno=\"{ch_no}\" tvh-chnum=\"{ch_no}\",{title}\n{url}\n' 
        m3u = '#EXTM3U\n'
        count = 1
        for source in self.source_map:
            try:
                #logger.debug(source.name)
                #logger.debug(ModelSetting.get_bool(f"{name}_use_{source.source_name}") )
                if ModelSetting.get_bool(f"{name}_use_{source.source_name}") == False:
                    continue
                source_ch_list = source.get_list()
                #logger.debug(len(source_ch_list))
                if source_ch_list == None:
                    continue
                for key, ch in source_ch_list.items():
                    m3u += M3U_FORMAT.format(
                        id=f"{source.source_name}|{ch.ch_id}",
                        title=ch.get_title(),
                        group=source.name,
                        ch_no=str(count+1),
                        url=ToolUtil.make_apikey_url(f"/{package_name}/api/base/url.m3u8?source={source.source_name}&ch_id={ch.ch_id}"),
                        logo= ch.logo,
                    )
                    count += 1
            except Exception as e: 
                P.logger.error(f'Exception:{str(e)}')
                P.logger.error(traceback.format_exc())
        return m3u


    def get_url(self, req_source, req_ch_id):
        data = None
        for source in self.source_map:
            if source.source_name == req_source:
                ch = source.ch_list[req_ch_id]
                data = ch.as_dict()
                if ch.url == None:
                    data['url'] = source.get_url(req_ch_id)
                #logger.info(d(data))
                return data
                
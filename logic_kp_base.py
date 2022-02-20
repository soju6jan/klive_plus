import os, sys, traceback, re, json, threading, time, shutil, platform
from datetime import datetime
from flask import request, render_template, jsonify, redirect, send_file
from .plugin import P, logger, package_name, ModelSetting, LogicModuleBase, scheduler, app, SystemModelSetting, path_data, d
name = 'base'

from tool_base import ToolUtil

class LogicKPBase(LogicModuleBase):
    db_default = {
        f'{name}_db_version' : '1',
        f'{name}_auto_start' : 'False',
        f'{name}_interval' : '30',
        f'{name}_use_naver_sports': 'True',
        f'{name}_use_spotv': 'True',
        f'{name}_spotv_username': '',
        f'{name}_spotv_password': '',
    }

    def __init__(self, P):
        super(LogicKPBase, self).__init__(P, 'list')
        self.name = name

    def process_menu(self, sub, req):
        logger.error(sub)
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
                logger.debug(command)
                if command == 'make':
                    self.task_interface(req.form['arg1'], 'manual')
                    ret = {'ret':'success', 'msg':'생성을 시작합니다.'}
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
                for source in self.source_map:
                    if source.source_name == req_source:
                        ch = source.ch_list[req_ch_id]
                        if ch.url != None:
                            url = ch.url
                        else:
                            url = source.get_url(req_ch_id)
                        logger.debug(url)
                        return redirect(url, code=302)
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


    def get_ch_list(self):
        ch_list = []
        for source in self.source_map:
            try:
                source_ch_list = source.get_list()
                for source_id, ch in source_ch_list.items():
                    ch_list.append(ch)
            except Exception as e: 
                P.logger.error(f'Exception:{str(e)}')
                P.logger.error(traceback.format_exc())
        return ch_list


    def make_m3u(self):
        M3U_FORMAT = '#EXTINF:-1 tvg-id=\"{id}\" tvg-name=\"{title}\" tvg-logo=\"{logo}\" group-title=\"{group}\" tvg-chno=\"{ch_no}\" tvh-chnum=\"{ch_no}\",{title}\n{url}\n' 
        m3u = '#EXTM3U\n'
        count = 1
        for source in self.source_map:
            for key, ch in source.get_list().items():
                m3u += M3U_FORMAT.format(
                    id=f"{source.source_name}|{ch.ch_id}",
                    title=ch.get_title(),
                    group=source.name,
                    ch_no=str(count+1),
                    url=ToolUtil.make_apikey_url(f"/{package_name}/api/base/url.m3u8?source={source.source_name}&ch_id={ch.ch_id}"),
                    logo= ch.logo,
                )
                count += 1
        return m3u

import argparse
import json
import os
import platform
import re
import sys
import traceback
import urllib.parse
from collections import OrderedDict
from datetime import datetime, timedelta

import requests
from flask import Response
from support import SupportFile, d, default_headers
from tool import ToolUtil

from .setup import *


class SourceBase:
    def __init__(self):
        self.reset_ch_list()
        self.name = ''
        self.source_name = ''
        self.poster = ""
        self.headers = {}
         
    def get_list(self):
        pass

    def get_url(self, ch_id):
        pass
    
    def reset_ch_list(self):
        self.ch_list = OrderedDict()

    def process_m3u8(self, req):
        pass

    def process_ts(self, req):
        pass

    def get_max_bandwidth(self, text, first=False):
        try:
            max_data = {'set':False, 'bandwidth':0, 'url':''}
            for tmp in text.split('\n'):
                if tmp.startswith('#'):
                    if 'SAMPLE-AES' in tmp:
                        max_data['ret'] = 'drm'
                        logger.warning('DRM channel!!')
                        break
                    match = re.search("(,|:)BANDWIDTH=(?P<bw>\d+)(\,|$)", tmp)
                    if match:
                        if max_data['bandwidth'] < int(match.group('bw')):
                            max_data['bandwidth'] = int(match.group('bw'))
                            max_data['set'] = True
                else:
                    if max_data['set']:
                        max_data['url'] = tmp
                        max_data['set'] = False
                        if first:
                            break
                    else:
                        continue
            max_data['ret'] = 'success'
        except Exception as e:
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())
            max_data['ret'] = 'fail'
        return max_data
    
    def setting_save_after(self, change_list):
        pass

    
    def make_cookies(self, text):
        lines = text.split('\n')
        cookie_list = []
        for line in lines:
            line = line.strip()
            if line == '' or line.startswith('#'):
                continue
            tmps = line.split('\t')
            if len(tmps) == 7:
                cookie_list.append((tmps[5], tmps[6]))
        return '; '.join([f"{cookie[0]}={cookie[1]}" for cookie in cookie_list])



class Channel:
    def __init__(self, ch_id, ch_name, current, url=None, logo='', info=None, source=None, group=None):
        self.ch_id = ch_id
        self.ch_name = ch_name
        self.current = current
        self.url = url
        self.logo = logo
        self.info = info
        self.source = source
        self.group = group
        
    def get_title(self):
        if self.current == None or self.current == '':
            tmp = self.ch_name
        else:
            tmp = f"{self.current} ({self.ch_name})".replace('()', '')
        return tmp

    def as_dict(self):
        return {attr:getattr(self, attr) for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")}

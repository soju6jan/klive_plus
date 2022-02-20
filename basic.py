import os, sys, traceback, json, requests, argparse, platform, re, urllib.parse
from datetime import datetime, timedelta
from collections import OrderedDict 
logger = None

if platform.system() == 'Windows':
    sys.path += ["C:\SJVA3\lib2", "C:\SJVA3\data\custom", "C:\SJVA3_DEV"]
else:
    sys.path += ["/root/SJVA3/lib2", "/root/SJVA3/data/custom"]

try:
    from .plugin import logger, ModelSetting, package_name
    from tool_base import ToolUtil
    from flask import Response, request
except:
    pass

from support.base import get_logger, d, default_headers

if logger == None:
    logger = get_logger()

class SourceBase:
    def __init__(self):
        self.reset_ch_list()
        self.get_list()

    def get_list(self):
        pass

    def get_url(self, ch_id):
        pass
    
    def reset_ch_list(self):
        self.ch_list = OrderedDict()


class Channel:
    def __init__(self, ch_id, ch_name, current, url=None, logo='', info=None, source=None, source1=None):
        self.ch_name = ch_name
        self.ch_id = ch_id
        self.current = current
        self.url = url
        self.logo = logo
        self.info = info
        self.source = source
        self.source1 = source1
        
    def get_title(self):
        tmp = f"{self.current} ({self.ch_name})".replace('()', '')
        return tmp

    def as_dict(self):
        return {attr:getattr(self, attr) for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")}

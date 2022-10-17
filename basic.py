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
from support import default_headers
from tool import ToolUtil

from .setup import *

logger = None

class SourceBase:
    def __init__(self):
        self.reset_ch_list()
        try:
            self.get_list()
        except Exception as e: 
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())
            
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

import os, sys, traceback, json, urllib.parse, requests, argparse, yaml, platform, time, re, base64
if __name__ == '__main__':
    if platform.system() == 'Windows':
        sys.path += ["C:\SJVA3\lib2", "C:\SJVA3\data\custom", "C:\SJVA3_DEV"]
    else:
        sys.path += ["/root/SJVA3/lib2", "/root/SJVA3/data/custom"]

from support.base import get_logger, d, default_headers, SupportAES, SupportFile

logger = get_logger()
from urllib.parse import urlencode, unquote, quote
from datetime import datetime

# cd /host/root/sjva/plugin/loading/klive_plus
# python3 tool.py
class Tool:
    def test(self):
        text = SupportAES.encrypt('''aaa''')
        logger.debug(text)
        ori = SupportAES.decrypt(text)
        logger.debug(ori)
    
    @classmethod
    def source_encrypt(cls):
        current_folder = os.path.join(os.path.dirname(__file__))
        if current_folder == '':
            current_folder = os.getcwd()
        for filename in os.listdir(current_folder):
            if filename.startswith('original_') == False:
                continue
            filepath = os.path.join(current_folder, filename)
            target = filepath.replace('original_', 'decrypt_')
            text = SupportAES.encrypt(base64.b64encode(SupportFile.read_file(filepath).encode()).decode())
            SupportFile.write_file(target, text)
            src = base64.b64decode(SupportAES.decrypt(text)).decode()

    @classmethod
    def source_decrypt(cls):
        current_folder = None
        if os.path.exists(os.path.join(os.path.dirname(__file__), 'original_source_spotv.py')) == True:
            from .original_source_spotv import SourceSpotv
            from .original_source_naver_sports import SourceNaverSports
            from .original_source_coupangplay import SourceCoupangplay
            from .original_source_reystream import SourceReystream
            from .original_source_sstv import SourceSSTV
            
        else:
            source_map = []
            current_folder = os.path.join(os.path.dirname(__file__))
            if current_folder == '':
                current_folder = os.getcwd()
            for filename in os.listdir(current_folder):
                if filename.startswith('decrypt_') == False:
                    continue
                filepath = os.path.join(current_folder, filename)
                mod_name = filename.replace('decrypt_', '').replace('.py', '')
                target = filepath.replace('decrypt_', '')
                text = base64.b64decode(SupportAES.decrypt(SupportFile.read_file(filepath))).decode()
                SupportFile.write_file(target, text)
                from .source_spotv import SourceSpotv
                from .source_naver_sports import SourceNaverSports
                from .source_coupangplay import SourceCoupangplay
                from .source_reystream import SourceReystream
                from .source_sstv import SourceSSTV
        
        source_map = [SourceSpotv(), SourceNaverSports(), SourceCoupangplay(), SourceSSTV(), SourceReystream()]
        for filename in os.listdir(current_folder):
            if filename.startswith('source_'):
                os.remove(os.path.join(current_folder, filename))

        return source_map




    @classmethod
    def clear(cls):
        current_folder = os.path.join(os.path.dirname(__file__))
        if current_folder == '':
            current_folder = os.getcwd()
        for filename in os.listdir(current_folder):
            if filename.startswith('source_') == False:
                continue
            filepath = os.path.join(current_folder, filename)
            os.remove(filepath)

if __name__ == '__main__':
    Tool().source_encrypt()
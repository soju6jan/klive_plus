setting = {
    'filepath' : __file__,
    'use_db': True,
    'use_default_setting': True,
    'home_module': None,
    'menu': {
        'uri': __package__,
        'name': 'KLive+',
        'list': [
            {
                'uri': 'main',
                'name': '전체',
                'list': [
                    {
                        'uri': 'setting',
                        'name': '설정',
                    },
                    {
                        'uri': 'list',
                        'name': '채널',
                    },
                ]
            },
            {
                'uri': 'log',
                'name': '로그',
            },
        ]
    },
    'default_route': 'normal',
}

from plugin import *

DEFINE_DEV = False
if os.path.exists(os.path.join(os.path.dirname(__file__), 'mod_main.py')):
    DEFINE_DEV = True
    
P = create_plugin_instance(setting)
logger = P.logger

try:
    if DEFINE_DEV:
        from .mod_main import ModuleMain
    else:
        from support import SupportSC
        ModuleMain = SupportSC.load_module_P(P, 'mod_main').ModuleMain

    P.set_module_list([ModuleMain])
except Exception as e:
    P.logger.error(f'Exception:{str(e)}')
    P.logger.error(traceback.format_exc())


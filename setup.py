setting = {
    'filepath' : __file__,
    'use_db': True,
    'use_default_setting': True,
    'home_module': 'main',
    'menu': {
        'uri': __package__,
        'name': 'KLive+',
        'list': [
            {
                'uri': 'main',
                'name': 'MAIN',
                'list': [
                    {
                        'uri': 'setting',
                        'name': '설정',
                    },
                    {
                        'uri': 'list',
                        'name': '목록',
                    },
                    {
                        'uri': 'cpl',
                        'name': '쿠플 예정',
                    }
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

DEFINE_DEV = False

from plugin import *

P = create_plugin_instance(setting)
try:
    if DEFINE_DEV and os.path.exists(os.path.join(os.path.dirname(__file__), 'mod_main.py')):
        from .mod_main import ModuleMain
    else:
        from support import SupportSC
        ModuleMain = SupportSC.load_module_P(P, 'mod_main').ModuleMain

    P.set_module_list([ModuleMain])
except Exception as e:
    P.logger.error(f'Exception:{str(e)}')
    P.logger.error(traceback.format_exc())


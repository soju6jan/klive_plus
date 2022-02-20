import os, sys, traceback, re
from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify, redirect
from framework import app, path_data, path_app_root, db, scheduler, SystemModelSetting, socketio, celery, get_logger
from plugin import LogicModuleBase, get_model_setting, Logic, default_route, PluginUtil


class P(object):
    package_name = __name__.split('.')[0]
    logger = get_logger(package_name)
    blueprint = Blueprint(package_name, package_name, url_prefix=f'/{package_name}', template_folder=os.path.join(os.path.dirname(__file__), 'templates'), static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    menu = {
        'main' : [package_name, 'KLive+'],
        'sub' : [
            ['base', '전체'], ['navertv', '네이버 스포츠'], ['log', '로그']
        ], 
        'category' : 'tv',
        'sub2' : {
            'base' : [
                ['setting', '설정'], ['list', '채널목록']
            ],
            'navertv' : [
                ['setting', '설정']
            ],
        }
    }  

    plugin_info = {
        'version' : '1.0.0.0',
        'name' : package_name,
        'category' : menu['category'],
        'icon' : '',
        'developer' : 'soju6jan',
        'description' : 'KLive+',
        'home' : f'https://github.com/soju6jan/{package_name}',
        'more' : '',
    }
    ModelSetting = get_model_setting(package_name, logger)
    logic = None
    module_list = None
    home_module = 'base'

    
from tool_base import d
logger = P.logger
package_name = P.package_name
ModelSetting = P.ModelSetting


def initialize():
    try:
        app.config['SQLALCHEMY_BINDS'][P.package_name] = 'sqlite:///%s' % (os.path.join(path_data, 'db', '{package_name}.db'.format(package_name=P.package_name)))
        PluginUtil.make_info_json(P.plugin_info, __file__)
        from .logic_kp_base import LogicKPBase
        #from .logic_kp_navertv import LogicKPNaver
        P.module_list = [LogicKPBase(P)]#, LogicKPNaver(P)]
        P.logic = Logic(P)
        default_route(P)
    except Exception as e: 
        P.logger.error(f'Exception:{str(e)}')
        P.logger.error(traceback.format_exc())

initialize()


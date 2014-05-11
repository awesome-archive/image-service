# coding: utf-8

from cores.captcha_generator import CaptchaGenerator
from cores.app import app, run as start_http_server
from libs.process import set_current_proc_title as _set_current_proc_title, ProcessPool
from libs import process
from libs.daemon import Daemon
from cores.constants import Constants

set_current_proc_title = lambda name: _set_current_proc_title(name, Constants.PROC_NAME)
process.base_proc_title = 'python'

from argparse import ArgumentParser
import sys
import os
path = os.path

class Manager(object):
    def __init__(self):
        self.namespace = self.define_argparser().parse_args()
        self._init_config()
        self.run_dir = sys.path[0]
        self.pidfile = None
        self.log_path = None

        self._init_log_and_pid_file()
        self._package_check()

    def _init_config(self):
        for attr_name in dir(self.namespace):
            if attr_name.startswith('_'):
                continue
            attr = getattr(self.namespace, attr_name)

            if not callable(attr):
                setattr(self, attr_name, attr)

    def _package_check(self):
        import gevent
        import gunicorn
        import PIL
        import bottle
        import scgi

    def _init_log_and_pid_file(self):
        self.log_path = log_path = path.join(self.run_dir, 'logs')

        if not path.isdir(log_path):
            os.mkdir(log_path)

        self.pidfile = path.join(log_path, 'ImageService.pid')

    def loop(self):
        """ 启动应用 """
        set_current_proc_title('Master')

        elements = [self.start_http_service, self.start_captcha_generat_service]

        def _start_pool_proc(element):
            if type(element).__name__ == 'instancemethod':
                element()

        ProcessPool().map(_start_pool_proc, elements)

    class _MainDaemon(Daemon):
        def __init__(self, manager, *args, **kwargs):
            self.manager = manager
            Daemon.__init__(self, *args, **kwargs)

        def run(self):
            self.manager.loop()

    def _operate(self, operation):

        error = path.join(self.log_path, 'error.log')

        daemon = self._MainDaemon(self, self.pidfile, stderr=error, stdout=error)

        getattr(daemon, operation)()

    def run(self):
        operation = self.namespace.operation

        self._operate(operation)

    def start_http_service(self):
        """ 开启验证码webApi服务 """
        set_current_proc_title('Http Service')
        start_http_server(self.http_host, self.http_port, self.debug)

    def start_captcha_generat_service(self):
        """ 开启验证码自产进程 """
        set_current_proc_title('Captcha Generator Service')
        CaptchaGenerator(self.captch_cache_min_count, self.captch_check_interval).workloop()

    def define_argparser(self):
        parser = ArgumentParser()
        parser.add_argument('-d', '--debug', help='是否调试模式启动', default=False)
        subparsers = parser.add_subparsers(help='请选择一个操作: ', dest='operation')

        parser.add_argument('--http_host', help='http服务绑定ip, 默认为127.0.0.1', default='127.0.0.1', action='store')
        parser.add_argument('--http_port', help='http服务绑定端口号, 默认为4301', default=4301, action='store', type=int)
        parser.add_argument('--with_scgi', help='是否自动伴随启动scgi服务, 为现有系统提供支持, 默认关闭',
                            default=False, action='store_true')
        parser.add_argument('--scgi_host', help='scgi服务绑定ip, 默认为127.0.0.1', default='127.0.0.1', action='store')
        parser.add_argument('--scgi_port', help='scgi服务端口号, 默认为4302', default=4302, action='store', type=int)
        parser.add_argument('--captch_cache_min_count', help='验证码缓存池最小数, 默认为100',
                            action='store', default=100, type=int)
        parser.add_argument('--captch_check_interval', help='检查验证码缓存池的时间间隔, 默认为10s',
                            default=10, action='store', type=int)

        subparsers.add_parser('start', help='开启服务')
        subparsers.add_parser('restart', help='重启服务')
        subparsers.add_parser('stop', help='关闭服务')

        return parser

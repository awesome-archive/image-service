# coding: utf-8

from cores import CaptchaGenerator
from cores import start_http_server
from cores import start_scgi_server
from cores.constants import Constants
from libs.process import set_current_proc_title as _set_current_proc_title, ProcessPool
from libs import process
from libs.daemon import Daemon

set_current_proc_title = lambda name: _set_current_proc_title(name, Constants.PROC_NAME)
process.base_proc_title = 'python'

from argparse import ArgumentParser, RawTextHelpFormatter
from functools import wraps
import sys
import os

path = os.path

Commands = ['start', 'stop', 'restart']


def _define_command(func):
    global Commands
    Commands.append(func.__name__)

    @wraps(func)
    def _(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            sys.stdout.write('Shutdown by <CTL+C>\n')

    return _


class Manager(object):
    def __init__(self):
        self.namespace = self.define_argparser().parse_args()
        self._init_config()
        self.run_dir = sys.path[0]
        self.pidfile = None
        self.log_path = None

        self.with_scgi = None
        self.http_host = '0.0.0.0'
        self.http_port = 4231
        self.debug = False
        self.captcha_cache_min_count = 10000
        self.captcha_cache_check_interval = 30
        self.scgi_host = '0.0.0.0'
        self.scgi_port = 4230
        self.scgi_max_children = 5
        self.scgi_detailed_log = True

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

    def _init_log_and_pid_file(self):
        self.log_path = log_path = path.join(self.run_dir, 'logs')

        if not path.isdir(log_path):
            os.mkdir(log_path)

        self.pidfile = path.join(log_path, 'ImageService.pid')

    def loop(self):
        """ 启动应用 """
        set_current_proc_title('Master')

        elements = [self.run_http_service, self.run_captcha_generate_service]

        if self.with_scgi:
            elements.append(self.run_scgi_service)

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

        daemon = self._MainDaemon(self, self.pidfile, stderr=error, stdout=os.devnull)

        getattr(daemon, operation)()

    def run(self):
        operation = self.namespace.operation

        sys.argv = sys.argv[:1]  # 修正gunicore会从argv中获取参数导致错误的问题

        if operation.startswith('run_'):
            getattr(self, operation)()
        else:
            self._operate(operation)

    @_define_command
    def run_http_service(self):
        """ 开启验证码webApi服务 """
        set_current_proc_title('Http')
        start_http_server(self.http_host, self.http_port, self.debug)

    @_define_command
    def run_captcha_generate_service(self):
        """ 开启验证码自产进程 """
        set_current_proc_title('CaptchaGenerate')
        CaptchaGenerator(self.captcha_cache_min_count, self.captcha_cache_check_interval).workloop()

    @_define_command
    def run_scgi_service(self):
        """ 开启scgi图片服务 """
        set_current_proc_title('Scgi')
        start_scgi_server(path.join(sys.path[0], 'libs/images/fonts'), host=self.scgi_host,
                          port=self.scgi_port, max_children=self.scgi_max_children,
                          detailed_log=self.scgi_detailed_log)

    @staticmethod
    def define_argparser():
        parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
        parser.add_argument('-d', '--debug', help='是否调试模式启动', default=False)

        parser.add_argument('--http_host', help='http服务绑定ip, 默认为127.0.0.1', default='127.0.0.1', action='store')
        parser.add_argument('--http_port', help='http服务绑定端口号, 默认为4301', default=4301, action='store', type=int)

        parser.add_argument('--with_scgi', help='是否自动伴随启动scgi服务, 为现有系统提供支持, 默认关闭',
                            default=False, action='store_true')
        parser.add_argument('--scgi_host', help='scgi服务绑定ip, 默认为127.0.0.1', default='127.0.0.1', action='store')
        parser.add_argument('--scgi_port', help='scgi服务端口号, 默认为4302', default=4302, action='store', type=int)
        parser.add_argument('--scgi_max_children', help='scgi 默认worker进程数', default=5, action='store', type=int)
        parser.add_argument('--scgi_detailed_log', help='scgi Handler记录详细请求日志', action='store_true')

        parser.add_argument('--captcha_cache_min_count', help='验证码缓存池最小数, 默认为10000',
                            action='store', default=10000, type=int)
        parser.add_argument('--captcha_cache_check_interval', help='检查验证码缓存池的时间间隔, 默认为10s',
                            default=10, action='store', type=int)

        parser.add_argument('operation', help=',\n'.join(Commands), choices=Commands, type=str)

        return parser

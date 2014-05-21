# coding: utf-8

import scgi
import os

from libs.process import set_current_proc_title
from .image_handler import ImageHandler
from ..constants import Constants


class _SCGIServer(scgi.scgi_server.SCGIServer):
    def __init__(self, *args, **kwargs):
        scgi.scgi_server.SCGIServer.__init__(self, *args, **kwargs)


class _Child:
    def __init__(self, pid, fd):
        set_current_proc_title('Worker[%s]' % os.getpid(), '%s Scgi' % Constants.PROC_NAME)
        self.pid = pid
        self.fd = fd
        self.closed = 0

    def close(self):
        if not self.closed:
            os.close(self.fd)
        self.closed = 1


scgi.scgi_server.Child = _Child


def run(fonts_path, host, port, max_children=5, detailed_log=False):
    ImageHandler.fonts_path = fonts_path  # 定位字体位置
    ImageHandler.detailed_log = detailed_log
    _SCGIServer(ImageHandler, host=host, port=port, max_children=max_children).serve()

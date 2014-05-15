#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import traceback

from scgi.scgi_server import SCGIHandler


class HandlerException(Exception):
    pass


class HandlerBase(SCGIHandler):
    detailed_log = False

    def __init__(self, *args, **kwargs):
        SCGIHandler.__init__(self, *args, **kwargs)
        self.output = None

    @staticmethod
    def debug(msg):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        sys.stderr.write("[%s] %s\n" % (timestamp, msg))

    def handle_connection(self, conn):
        _input = conn.makefile("r")
        output = conn.makefile("w")
        env = self.read_env(_input)
        bodysize = int(env.get('CONTENT_LENGTH', 0))

        if self.__class__.detailed_log:
            self.debug('request params: %s' % env)

        self.output = output

        try:
            self.produce(env, bodysize, _input)
        except:

            eType, eValue, eBraceback = sys.exc_info()

            self.debug(traceback.extract_tb(eBraceback))
            error_message = '%s: %s' % (eType, eValue)

            output.write("0\x00%s" % error_message)

        try:
            _input.close()
            output.close()
            conn.close()
        except IOError, err:
            self.debug("IOError while closing connection ignored: %s" % err)

    def respond(self, body):
        #self.output.write(body)
        self.output.write("1\x00%s" % body)

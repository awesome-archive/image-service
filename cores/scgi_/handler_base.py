#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time

from scgi.scgi_server import SCGIHandler

class HandlerException(Exception):
    pass

class HandlerBase(SCGIHandler):

    def debug(self, msg):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        sys.stderr.write("[%s] %s\n" % (timestamp, msg))

    def handle_connection(self, conn):
        input = conn.makefile("r")
        output = conn.makefile("w")
        env = self.read_env(input)
        bodysize = int(env.get('CONTENT_LENGTH', 0))

        self.output = output

        try:
            self.produce(env, bodysize, input)
        except:
            import traceback

            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()

            traceback.print_exc(file=sys.stderr)
            output.write("0\x00%s: %s" % (exceptionType, exceptionValue))

        try:
            input.close()
            output.close()
            conn.close()
        except IOError, err:
            self.debug("IOError while closing connection ignored: %s" % err)

    def respond(self, body, contentType='text/html'):
        #self.output.write(body)
        self.output.write("1\x00%s" % body)

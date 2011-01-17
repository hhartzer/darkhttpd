#!/usr/bin/env python
import unittest
import socket
import signal

class Conn:
    def __init__(self):
        self.port = 12346
        self.s = socket.socket()
        self.s.connect(("0.0.0.0", self.port))
        # connect throws socket.error on connection refused

    def get(self, req):
        self.s.send(req)
        ret = ""
        while True:
            signal.alarm(1)
            r = self.s.recv(65536)
            signal.alarm(0)
            if r == "":
                break
            else:
                ret += r
        return ret

class TestCases(unittest.TestCase):
    def assertContains(self, body, *strings):
        for s in strings:
            self.assertTrue(s in body,
                            msg="expected %s in %s"%(repr(s), repr(body)))

    def assertIsIndex(self, body, path):
        self.assertContains(body,
            "<title>%s</title>\n"%path,
            "<h1>%s</h1>\n"%path,
            '<a href="..">..</a>/',
            'Generated by darkhttpd')

    def assertIsInvalid(self, body, path):
        self.assertContains(body,
            "<title>400 Bad Request</title>",
            "<h1>Bad Request</h1>\n",
            "You requested an invalid URI: %s\n"%path,
            'Generated by darkhttpd')

    # FIXME: failing
    #def testIndex_HTTP_0_9(self):
    #    body = Conn().get("GET /\n\n")
    #    self.assertIsIndex(body)

    def testIndex_HTTP_1_0(self):
        body = Conn().get("GET / HTTP/1.0\n\n")
        self.assertIsIndex(body, "/")

    def testUpDirValid(self):
        body = Conn().get("GET /dir/../ HTTP/1.0\n\n")
        self.assertIsIndex(body, "/dir/../")

    def testExtraneousSlashes(self):
        body = Conn().get("GET //dir///..//// HTTP/1.0\n\n")
        self.assertIsIndex(body, "//dir///..////")

    def testWithoutTrailingSlash(self):
        body = Conn().get("GET /dir/.. HTTP/1.0\n\n")
        self.assertIsIndex(body, "/dir/..")

    def testWithoutLeadingSlashFails(self):
        body = Conn().get("GET dir/../ HTTP/1.0\n\n")
        self.assertIsInvalid(body, "dir/../")

    def testUpDirInvalid(self):
        body = Conn().get("GET /../ HTTP/1.0\n\n")
        self.assertIsInvalid(body, "/../")

    def testUpDirInvalidFancy(self):
        body = Conn().get("GET /dir/../../ HTTP/1.0\n\n")
        self.assertIsInvalid(body, "/dir/../../")

if __name__ == '__main__':
    unittest.main()
    #print Conn().get("GET /xyz/../ HTTP/1.0")

# vim:set ts=4 sw=4 et:
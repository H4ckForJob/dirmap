"""Fuzing for IPy.py"""

# TODO: unify assert / FilIf usage

import sys
import functools
import itertools
sys.path.append('.')
sys.path.append('..')

import IPy
import unittest
import random

if sys.version_info >= (3,):
    xrange = range

# on Python-2.7 and higher, we use load_tests to multiply out the test cases so that unittest
# represents each as an individual test case.
def iterate_27(n):
    def wrap(func):
        func.iterations = n
        return func
    return wrap

def load_tests(loader, tests, pattern):
    def expand(tests):
        if isinstance(tests, unittest.TestCase):
            method_name = tests._testMethodName
            meth = getattr(tests, method_name)
            if hasattr(meth, 'iterations'):
                tests = unittest.TestSuite(type(tests)(method_name) for i in xrange(meth.iterations))
        else:
            tests = unittest.TestSuite(expand(t) for t in tests)
        return tests
    return expand(tests)

# On older Pythons, we run the requisite iterations directly, in a single test case.
def iterate_old(n):
    def wrap(func):
        @functools.wraps(func)
        def replacement(*args):
            for i in xrange(n):
                func(*args)
        return replacement
    return wrap

if sys.version_info >= (2,7):
    iterate = iterate_27
else:
    iterate = iterate_old

# utilities

def random_ipv4_prefix():
    prefixlen = random.randrange(32)
    int_ip = random.randrange(IPy.MAX_IPV4_ADDRESS)
    int_ip &= 0xffffffff << (32-prefixlen)
    return IPy.IP('.'.join(map(str, (int_ip >> 24,
                                    (int_ip >> 16) & 0xff,
                                    (int_ip >> 8) & 0xff,
                                    int_ip & 0xff)))
                           + '/%d' % prefixlen)

# tests

class ParseAndBack(unittest.TestCase):

    @iterate(500)
    def testRandomValuesv4(self):
        question = random.randrange(0xffffffff)
        self.assertEqual(IPy.parseAddress(IPy.intToIp(question, 4)), (question, 4), hex(question))

    @iterate(500)
    def testRandomValuesv6(self):
        question = random.randrange(0xffffffffffffffffffffffffffffffff)
        self.assertEqual(IPy.parseAddress(IPy.intToIp(question, 6)), (question, 6), hex(question))

class TestIPSet(unittest.TestCase):

    @iterate(1000)
    def testRandomContains(self):
        prefixes = [random_ipv4_prefix() for i in xrange(random.randrange(50))]
        question = random_ipv4_prefix()
        answer = any(question in pfx for pfx in prefixes)
        ipset = IPy.IPSet(prefixes)
        self.assertEqual(question in ipset, answer,
                "%s in %s != %s (made from %s)" % (question, ipset, answer, prefixes))
        

    @iterate(1000)
    def testRandomDisjoint(self):
        prefixes1 = [random_ipv4_prefix() for i in xrange(random.randrange(50))]
        prefixes2 = [random_ipv4_prefix() for i in xrange(random.randrange(50))]
        # test disjointnes the stupid way
        disjoint = True
        for p1, p2 in itertools.product(prefixes1, prefixes2):
            if p1 in p2 or p2 in p1:
                disjoint = False
                break
        ipset1 = IPy.IPSet(prefixes1)
        ipset2 = IPy.IPSet(prefixes2)
        self.assertEqual(ipset1.isdisjoint(ipset2), disjoint,
                "%s.isdisjoint(%s) != %s" % (ipset1, ipset2, disjoint))
        self.assertEqual(ipset2.isdisjoint(ipset1), disjoint,
                "%s.isdisjoint(%s) != %s" % (ipset2, ipset1, disjoint))

if __name__ == "__main__":
    unittest.main()

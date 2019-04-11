#!/usr/bin/env python
import doctest
import sys
if hasattr(doctest, "testfile"):
    total_failures, total_tests = (0, 0)

    print("=== Test file: README ===")
    failure, tests = doctest.testfile('README', optionflags=doctest.ELLIPSIS)
    total_failures += failure
    total_tests += tests

    print("=== Test file: test.rst ===")
    failure, tests = doctest.testfile('test/test.rst', optionflags=doctest.ELLIPSIS)
    total_failures += failure
    total_tests += tests

    print("=== Test IPy module ===")
    import IPy
    failure, tests = doctest.testmod(IPy)
    total_failures += failure
    total_tests += tests

    print("=== Overall Results ===")
    print("total tests %d, failures %d" % (total_tests, total_failures))
    if total_failures:
        sys.exit(1)
else:
    sys.stderr.write("WARNING: doctest has no function testfile (before Python 2.4), unable to check README\n")


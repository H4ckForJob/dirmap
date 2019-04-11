Non regression tests
====================

>>> from IPy import IP
>>> IP('::ffff:1.2.3.4').strCompressed()
'::ffff:1.2.3.4'
>>> IP('::ffff:192.168.10.0/120').strCompressed()
'::ffff:192.168.10.0/120'
>>> IP('::ffff:192.168.10.42/120', make_net=True).strCompressed()
'::ffff:192.168.10.0/120'
>>> IP('::/0', make_net=True).net()
IP('::')
>>> IP('0.0.0.0/0') + IP('0.0.0.0/0')
Traceback (most recent call last):
  ...
ValueError: Networks with a prefixlen longer than /1 can't be added.


Compare 0.0.0.0/0 and ::/0 bug
==============================

>>> IP('0.0.0.0/0') < IP('::/0')
True
>>> IP('0.0.0.0/0') > IP('::/0')
False
>>> IP('0.0.0.0/0') == IP('::/0')
False

>>> d={}
>>> d[IP('0.0.0.0/0')] = 1
>>> d[IP('::/0')] = 2
>>> d
{IP('::/0'): 2, IP('0.0.0.0/0'): 1}

>>> addresses = [IP('0.0.0.0/16'), IP('::7'), IP('::3'), IP('::0'),
...              IP('0.0.0.0'), IP('0.0.0.3'), IP('0.0.0.0/0'), IP('::/0')]
...
>>> addresses.sort()
>>> addresses
[IP('0.0.0.0/0'), IP('0.0.0.0/16'), IP('0.0.0.0'), IP('0.0.0.3'), IP('::/0'), IP('::'), IP('::3'), IP('::7')]

>>> IP('::/0').netmask()
IP('::')


IP types
========

>>> IP('10.8.3.0/24').iptype()
'PRIVATE'
>>> IP('88.164.127.124').iptype()
'PUBLIC'
>>> IP('223.0.0.0/8').iptype()
'PUBLIC'
>>> IP('224.0.0.0/8').iptype()
'RESERVED'

Reverse name
============

>>> IP('::ffff:193.0.1.208').reverseName()
'208.1.0.193.in-addr.arpa.'
>>> IP('::ffff:193.0.1.208').reverseNames()
['208.1.0.193.in-addr.arpa.']
>>> IP('128.0.0.0/7').reverseName()
'128-255..in-addr.arpa.'
>>> IP('128.0.0.0/7').reverseNames()
['128.in-addr.arpa.', '129.in-addr.arpa.']
>>> IP('::ffff:128.0.0.0/103').reverseName() == IP('128.0.0.0/7').reverseName()
True
>>> IP('::ffff:128.0.0.0/103').reverseNames() == IP('128.0.0.0/7').reverseNames()
True

Issue #2 and #9
===============

>>> IP('1.2.3.4') == None
False
>>> IP('1.2.3.4') == object()
False
>>> IP('1.2.3.4') != None
True
>>> IP('1.2.3.4') != object()
True


get_mac()
=========

>>> IP('fe80::f66d:04ff:fe47:2fae').get_mac()
'f4:6d:04:47:2f:ae'
>>> IP('2001:DB8::212:7FFF:FEEB:6B40').get_mac()
'00:12:7f:eb:6b:40'
>>> IP('::1').get_mac() is None
True
>>> IP('1.2.3.4').get_mac() is None
True

Issue #12: IPv6[index] -> IPv4
==============================

>>> IP('1.2.3.0/24')[4]
IP('1.2.3.4')
>>> IP('::/0')[1]
IP('::1')


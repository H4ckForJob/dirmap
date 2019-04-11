# This is a hack I use to generate my tinydns configuration
# It serves as e test for converting from Perl Net::IP to
# Python and IPy

# Further Information might be available at http://c0re.jp/c0de/IPy/
# Hacked 2001 by drt@un.bewaff.net

import sys
sys.path.append('..')

import IPy


ns = {'ns.nerxs.com': '213.221.113.70',
      'ns.dorsch.org': '195.143.234.25',
      'ns.c0re.jp': '217.6.214.130'}

print "# *** nameservers ***"
for x in ns.keys():
    print "=%s:%s" % (x, ns[x])

print "\n# *** domains ***"

fd = open('domains')

for x in fd.readlines():
    if x[0] != '#':
        if x[-1] == '\n':
            x = x[:-1]
        (domain, owner) = x.split(':')
        print "'%s:Contact for this domain is %s" % (domain, owner)
        for y in ns.keys(): 
            print ".%s::%s" % (domain, y)

fd.close()

print "\n# *** Networks ***"

fd = open('networks')
ip6map = {}
rmap = {}
nmap = {}

for x in fd.readlines():
    if x[-1] == '\n':
        x = x[:-1]
    if len(x) > 0 and x[0] != '#':
        nets = x.split(',')
        name = nets.pop(0)
        print "# Network: %s" % name
        for y in nets:
            ip = IPy.IP(y)
            print "# Address range: %s (%s), %d addresses" % (ip.strCompressed(), ip.iptype(), ip.len())
            print "=net.%s:%s" % (name, ip.net())
            print "=broadcast.%s:%s" % (name, ip.broadcast())
            
            if ip.version() == 4:
                for z in ip:
                    # TODO reverse?
                    nmap[z.int()] = name
                    rmap[z.int()] = z.strBin() + "." + name
            else:
                # IPv6
                for z in ns.keys():
                    for v in ip.reverseName():
                        print ".%s::%s" % (v, z) 
                ip6map[ip.strFullsize(0)] = name

fd.close()

print "\n# *** hosts ***"
      
fd = open('hosts')

for x in fd.readlines():
    if x[-1] == '\n':
        x = x[:-1]
    if x != '' and x[0] != '#':
        if "@Z'.".find(x[0]) >= 0:
            print x
        else:
            if "=+'".find(x[0]) >= 0:
                i = x.split(':')
                rmap[IPy.IP(i[1]).int()] = ''
                print x
            else:
                x = x[1:]
                x += '||||'
                fields = x.split('|')
                name = fields.pop(0)
                if name[0] == '.':
                    name = name[1:]
                v = fields.pop(0)
                ips = v.split(',')
                v = fields.pop(0)
                aliases = v.split(',')
                if aliases == ['']:
                    aliases = []
                admin = fields.pop()
                if admin == '':
                    admin = 'technik@c0re.23.nu'
                v = fields.pop()
                mxes = v.split(',')
                if mxes == ['']:
                    mxes = []
                for y in ips:
                    ip = IPy.IP(y) 
                    if ip.version() == 4:
                        # IPv4 is easy
                        if not nmap.has_key(ip.int()):
                            print >>sys.stderr, "*** warning: no network for %s (%s) - ignoring" % (y, name)
                            print "# no network for %s (%s)" % (y, name)
                        else:
                            print "=%s.%s:%s" % (name, nmap[ip.int()], y)
                            print "'%s.%s:Host contact is %s" % (name, nmap[ip.int()], admin)
                            rmap[ip.int()] = ''      
                            for z in aliases:
                                print "+%s:%s" % (z, ip)
                                print "'%s:Host contact is %s" % (z, admin)
                    else:
                        #IPv6 here
                        net = ip.strFullsize(0)
                        net = net[:19] + ':0000:0000:0000:0000'
                        if ip6map.has_key(net):
                            print >>sys.stderr, "*** warning: no network for %s (%s) - ignoring" % (ip, name)
                            print "# no network for %s (%s) - ignoring" % (ip, name)
                        else:  
                            print "6%s.%s:%s"; (name, ip6map[net], ip.strHex()[2:])
                            for z in aliases:
                                print "3%s:%s" % (name, ip.strHex()[2:])
                                print "'%s:Host contact is %s" % (name, admin)

fd.close()

print "\n# *** reverse lookup ***"
k = nmap.keys()
k.sort()
for x in k:
    if rmap.has_key(x) and rmap[x] != '':
      print "=%s:%s" % (rmap[x], str(IPy.IP(x)))


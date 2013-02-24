#!/usr/bin/python

# wille


# ue : 9F
# ae : 8A

#print "\x9f\x8a\x9a".decode("mac-roman")

import collections, os, sys


def createRef(pattern):
    ref = collections.deque([i for i in pattern], len(pattern))
    x = collections.deque(["\x00" for _ in range(len(ref))], len(ref))
    return ref, x
    
def findPattern(data, pattern, callback):
    ref, x = createRef(pattern)
    P = len(ref)
    pos = 0
    first = ref[0]
    L = len(data)
    while pos < L:
        if first not in x:
            x.extend(data[pos:pos+P])
            pos += P
        else:
            x.append(data[pos])
            pos += 1
        if x == ref:
            callback(data, pos)

f = open("Vallader.lzm", "r")
data = f.read()
f.close()

def anlz_01ff05():
    # row
    # 01 FF 05 00 00 00 00 3E C0 C0
    e = {}
    
    def cb(d, p):
        t = d[p]
        count, _ = e.get(t, (0, 0))
        e[t] = count + 1, p
    
    findPattern(data, "\x01\xFF\x05\x00\x00\x00\x00", cb)

    print '%8s   %6s    %8s' % ("next chr", "count", "lastaddr")
    print '-' * 80
    items = e.items()
    items.sort(key=lambda i : i[1][0], reverse=True)
    for key, (count, last) in items:
        res = '%8s : %6i  @ %8x' % (repr(key), count, last)
        print res

 
def analyze_xxx():
    
    e = {}
    
    def cb(d, p):
        t = d[p-5]
        count, _ = e.get(t, (0, 0))
        e[t] = count + 1, p
    
    findPattern(data, "\x03xxx", cb)
    
    print '%8s   %6s    %8s   %s' % ("next chr", "count", "lastaddr", "contents")
    print '-' * 80
    items = e.items()
    items.sort(key=lambda i : i[1][0], reverse=True)
    for key, (count, last) in items:
        res = '%8s : %6i  @ %8x : "%s"' % (repr(key), count, last, repr(data[last:last+10]))
        print res

def rnd(value, multiple):
    return (value + multiple - 1) & (-multiple)

def read0x200():
    import struct, parse.page
    L = len(data)
    pos = 0x1000
    pageSize = 0x400-0x10
    parser = parse.page.Parser()
    while pos < L:
        # type |      |      |      |      |      | size | table |
        # 00 00 00 00 | 00 5E 00 00 | 00 D2 00 09 | 00 59 C1 11 |  
        etype, _, _, _, _, _, esize, table = struct.unpack_from(">HHHHHHHH", data, pos)
        print "@ %8x : %4i %4x" % (pos, esize, table)
        
        pos += 0x10
        # Problem with esize at entry at 0x87c00 which is somewhat larger
#        pagedata = data[pos:pos+esize]
        pagedata = data[pos:pos+pageSize]
        
        if table == 0xc105:
            parser.dicziunari(pagedata, etype)
        
        pos = rnd(pos + esize, 0x400)
        
    print "Entries:", len(parser.entries)
        
read0x200()

#def anlz_hbam():
#    "HBAM3016AUG95"
# bis 0x1000

#anlz_01ff05()

#analyze_xxx()



#!/usr/bin/python

# wille


# ue : 9F
# ae : 8A

#print "\x9f\x8a\x9a".decode("mac-roman")

import collections, os, sys
from lzmparser import Parser


def parse():
    parser = Parser("Vallader.lzm")
    parser.parseFile()
        
    print "Entries:   ", len(parser.entries)
    print "Collisions:", parser.collisions
    
    # http://www.blog.pythonlibrary.org/2012/07/18/python-a-simple-step-by-step-sqlite-tutorial/
parse()



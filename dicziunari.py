#!/usr/bin/python
# coding=utf-8

import commands, os, sys, argparse, time
from lzmparser import Parser


def parse(dicziunariPath):
    parser = Parser("Vallader.lzm")
    parser.parseFile()
        
    print "Entries:   ", len(parser.entries)
    print "Collisions:", parser.collisions
    
    # http://www.blog.pythonlibrary.org/2012/07/18/python-a-simple-step-by-step-sqlite-tutorial/

def makeDicziunarisReady():
    # Encryption: openssl aes-256-cbc -in dicziunaris.tar.bz2 -out dicziunaris.tar.bz2.aes
    # Decryption: openssl aes-256-cbc -d -in dicziunaris.tar.bz2.aes -out dicziunaris.tar.bz2
    if not os.path.exists("./Vallader.lzm"):
        (s, o) = commands.getstatusoutput("openssl aes-256-cbc -d -in dicziunaris.tar.bz2.aes |"
                                          "tar xjf -")
        if s != 0:
            print >> sys.stderr, "Eu n'ha gnü ün problem da dechiffrar ils dicziunaris: %s (%i)" % (o, s)
            sys.exit(1)
        print "Ueilà, ils dicziunaris sun pronts a maldüsar!"

if __name__ == "__main__":
    print "Trar oura pleds (TOP) 1.0 copyright (c) 2012-%s cls et al." % time.strftime("%Y")
    makeDicziunarisReady()
    
    ap = argparse.ArgumentParser()
    apDictSelectGroup = ap.add_mutually_exclusive_group()
    apDictSelectGroup.add_argument("-p", "--puter", action='store_true', help="operar cul puter dicziunari")
    apDictSelectGroup.add_argument("-v", "--vallader", action='store_true', help="operar cul vallader dicziunari (default)")
    args = ap.parse_args()
    
    if args.puter:
        dPath = "./Puter.lzm"
    else:
        dPath = "./Vallader.lzm"
    
    parse(dPath)

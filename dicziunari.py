#!/usr/bin/python
# coding=utf-8

import commands, os, sys, argparse, time
from lzmparser import Parser

def main():
    print "Trar oura pleds (TOP) 1.0 copyright (c) 2012-%s cls et al." % time.strftime("%Y")
    makeDicziunarisReady()
    
    ap = argparse.ArgumentParser()
    apDictSelectGroup = ap.add_mutually_exclusive_group()
    apDictSelectGroup.add_argument("-p", "--puter", action='store_true', help="operar cul puter dicziunari")
    apDictSelectGroup.add_argument("-v", "--vallader", action='store_true', help="operar cul vallader dicziunari (default)")
    ap.add_argument("-s", "--sqlite", action='store_true', help="crea SQLite banca da datas")
    args = ap.parse_args()
    
    if args.puter:
        dPath = "./Puter.lzm"
    else:
        dPath = "./Vallader.lzm"
    
    parser = parse(dPath)
    
    if args.sqlite:
        dbPath = os.path.splitext(dPath)[0] + ".db"
        createSQLite(dbPath, parser)

def parse(dicziunariPath):
    parser = Parser("Vallader.lzm")
    parser.parseFile()
        
    print "Entries:   ", len(parser.entries)
    print "Collisions:", parser.collisions
    
    cols = parser.getColumns()
    print "Columns:   ", len(cols), ", ".join(["'%s'" % c for c in cols])
    return parser


def createSQLite(sqliteDbPath, parser, tableName = "dicziunari"):    
    # http://www.blog.pythonlibrary.org/2012/07/18/python-a-simple-step-by-step-sqlite-tutorial/
    import sqlite3
    
    if os.path.exists(sqliteDbPath):
        commands.getstatusoutput('rm -f "%s"' % sqliteDbPath)
    conn = sqlite3.connect(sqliteDbPath)
     
    cursor = conn.cursor()
     
    cols = parser.getColumns()
    C = len(cols)
    colMap = {'address':'address',
              'A': 'aa',
              'B': 'bb',
              'E': 'ee',
              'D': 'dd',
              'G': 'gg',
              'I': 'ii',
              'H': 'hh',
              'K': 'kk',
              'J': 'jj',
              'L': 'll',
              'O': 'oo',
              'N': 'nn',
              'Q': 'qq',
              'P': 'pp',
              'S': 'ss',
              'R': 'rr',
              'T': 'tt',
              'W': 'ww',
              'V': 'vv',
              'X': 'xx',
              '_': 'us',
              '^': 'zf',
              'e': 'e',
              'd': 'd',
              'k': 'k',
              'j': 'j',
              'm': 'm',
              'n': 'n',}
    
    # create a table
    colList = ", ".join([colMap[c] for c in cols])
    cursor.execute(u"\n".join(["CREATE TABLE %s\n" % tableName,
                               "(id, " + colList + ")",
                               ])
                   + "\n")
    rows = []
    for rowId, entry in parser.entries.items():
        row = []
        row.append(rowId)
        for c in cols:
            row.append(entry.get(c, u""))
        rows.append(tuple(row))
    cursor.executemany("INSERT INTO %s VALUES (%s)" % (tableName,
                                                       ", ".join(["?" for _ in range(C+1)])),
                       rows)
    conn.commit()
    
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
    main()

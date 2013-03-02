#!/usr/bin/python
# coding=utf-8

import commands, os, sys, argparse, time, sqlite3
from lzmparser import Parser

def main():
    print "Trar oura pleds (TOP) 1.0 copyright (c) 2012-%s cls et al." % time.strftime("%Y")
    makeDicziunarisReady()
    
    ap = argparse.ArgumentParser()
    apDictSelectGroup = ap.add_mutually_exclusive_group()
    apDictSelectGroup.add_argument("-p", "--puter", action='store_true', help="lavurar cul puter dicziunari")
    apDictSelectGroup.add_argument("-v", "--vallader", action='store_true', help="lavurar cul vallader dicziunari (cas standard)")
    anaSqlGrp = ap.add_mutually_exclusive_group()
    anaSqlGrp.add_argument("-a", "--analisar", action='store_true', help="be analisa la veglia banca da datas")
    anaSqlGrp.add_argument("-s", "--sqlite", action='store_true', help="crea SQLite banca da datas")
    anaSqlGrp.add_argument("-t", "--tscherchar", help="tschercha alch aint illa nouva banca da datas")
    anaSqlGrp.add_argument("-l", "--lingias", help="tschercha alch aint illa nouva banca da datas ma muossa las crüjas lingias")
    args = ap.parse_args()
    
    if args.puter:
        dPath = "./Puter.lzm"
    else:
        dPath = "./Vallader.lzm"
        
    dbPath = None
    if dbPath is None:
        dbPath = os.path.splitext(dPath)[0] + ".db"
    
    if args.sqlite:
        parser = parse(dPath)
        createSQLite(dbPath, parser)
    elif args.analisar:
        parser = parse(dPath)        
        
    if args.tscherchar:
        query(dbPath, args.tscherchar)
    if len(args.lingias) > 0:
        query(dbPath, args.lingias, raw=True)

def parse(dicziunariPath):
    parser = Parser(dicziunariPath)
    parser.parseFile()
        
    print "Entries:   ", len(parser.entries)
    print "Collisions:", parser.collisions
    
    cols = parser.getColumns()
    print "Columns:   ", len(cols), ", ".join(["'%s'" % c for c in cols])
    return parser

def query(sqliteDbPath, query, raw=False):
    if not os.path.exists(sqliteDbPath):
        print >> sys.stderr, "%s not found. Refer to -h for further information."
    conn = sqlite3.connect(sqliteDbPath)
    cursor = conn.cursor()
    
    if raw:
        cursor.execute("PRAGMA table_info(dicziunari)")
        cols = cursor.fetchall()
        sql = "SELECT * FROM dicziunari WHERE m LIKE '%%%s%%' OR n LIKE '%%%s%%'" % (query, query)
    else:
        sql = "SELECT m, n FROM dicziunari WHERE m LIKE '%%%s%%' OR n LIKE '%%%s%%'" % (query, query)
    cursor.execute(sql)
    res = cursor.fetchall()
    if raw:
        for row in res:
            for i, col in enumerate(row):
                print "%s : %s" % (cols[i][1], col)
            print "-" * 80
    else:
        for m, n, in res:
            print "  %35s : %-35s" % (m, n)
        

def createSQLite(sqliteDbPath, parser, tableName = "dicziunari"):
    # http://www.blog.pythonlibrary.org/2012/07/18/python-a-simple-step-by-step-sqlite-tutorial/
    
    if os.path.exists(sqliteDbPath):
        commands.getstatusoutput('rm -f "%s"' % sqliteDbPath)
    conn = sqlite3.connect(sqliteDbPath)
     
    cursor = conn.cursor()
     
    cols = parser.getColumns()
    C = len(cols)
    colMap = {'address':'address',
              'A': 'aa', # vallader only
              'C': 'cc', # puter only
              'B': 'bb',    # Stichwort key (rumantsch)
              'E': 'ee',
              'D': 'dd',
              'G': 'gg',
              'I': 'ii',    # bereich (rumantsch)
              'H': 'hh',    # a), 2. (rumantsch)
              'K': 'kk',
              'J': 'jj',
              'L': 'll',    # gener (rumantsch)
              'O': 'oo',
              'N': 'nn',
              'Q': 'qq',
              'P': 'pp',
              'S': 'ss',
              'R': 'rr',    # bereich (tudais-ch)
              'T': 'tt',    # plural/variazionen/deklinationen
              'W': 'ww',    # gener (tudais-ch)
              'V': 'vv',    # Stichwort key Deutsch
              'X': 'xx',
              '_': 'us',    # Wortgruppe Rumantsch
              '^': 'zf',    # Wortgruppe Deutsch
              'e': 'e',
              'd': 'd',
              'k': 'k',     # Duplicat Rumantsch (ma perche?)
              'j': 'j',     # Duplicat Tudais-ch (ma perche?)
              'm': 'm',     # Tudais-ch
              'n': 'n',     # Rumantsch
              }

    
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
            print >> sys.stderr, "Eu n'ha gnü ün problem da decifrar ils dicziunaris: %s (%i)" % (o, s)
            sys.exit(1)
        print "Ueilà! ils vegls e sgrischaivels dicziunaris sun pronts ad abüsar!"

if __name__ == "__main__":
    main()

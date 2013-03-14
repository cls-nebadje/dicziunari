#!/usr/bin/python
# coding=utf-8
#
# Dicziunari - A collection of linguistic tools for the Rhaeto-Romance
#              language
# 
# Copyright (C) 2012-2013 Uli Franke (cls) et al.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# IMPORTANT NOTICE: All software, content, intellectual property coming
# with this program (usually contained in files) can not be used in any
# way by the Lia Rumantscha (www.liarumantscha.ch/) without explicit
# permission, as they actively block software innovation targeting the
# Rhaeto-Romance language.
#

import commands, os, sys, argparse, time, sqlite3, re, ast
from lzmparser import Parser

DB_SRC_FILE_VALLADER = "Vallader.lzm"
DB_SRC_FILE_PUTER    = "Puter.lzm"
DB_SRC_FILE_GRISCHUN = "Grischun.usr"

def main():
    print "Trar oura pleds (TOP) 1.0 copyright (c) 2012-%s cls et al." % time.strftime("%Y")
    makeDicziunarisReady()
    
    ap = argparse.ArgumentParser()
    apDictSelectGroup = ap.add_mutually_exclusive_group()
    apDictSelectGroup.add_argument("-p", "--puter", action='store_true', help="lavurar cul puter dicziunari")
    apDictSelectGroup.add_argument("-v", "--vallader", action='store_true', help="lavurar cul vallader dicziunari (cas standard)")
    apDictSelectGroup.add_argument("-g", "--grischun", action='store_true', help="lavurar cul rumantsch grischun dicziunari")
    anaSqlGrp = ap.add_mutually_exclusive_group()
    anaSqlGrp.add_argument("-a", "--analisar", action='store_true', help="be analisa la veglia banca da datas")
    anaSqlGrp.add_argument("-s", "--sqlite", action='store_true', help="crea SQLite banca da datas")
    anaSqlGrp.add_argument("-t", "--tscherchar", help="tschercha alch aint illa nouva banca da datas")
    anaSqlGrp.add_argument("-l", "--lingias", help="tschercha alch aint illa nouva banca da datas ma muossa las crüjas lingias")
    ap.add_argument("-c", "--culuonnas", type=dictArg, help="selecziuna las culuonnas chi ston esser inclus aint illa nouve banca da datas. per exaimpel \"{m:wort,n:pled}\"")
    ap.add_argument("--ciffra", action='store_true', help="tar e ciffra ils dicziunaris")
    args = ap.parse_args()
    
    if args.ciffra:
        packAndEncryptDicziunaris()
        return
    
    if args.puter:
        dPath = DB_SRC_FILE_PUTER
    elif args.grischun:
        dPath = DB_SRC_FILE_GRISCHUN
    else:
        dPath = DB_SRC_FILE_VALLADER
        
    dbPath = None
    if dbPath is None:
        dbPath = os.path.splitext(dPath)[0] + ".db"
        
    if args.sqlite:
        parser = parse(dPath)
        createSQLite(dbPath, parser, colSelect=args.culuonnas)
    elif args.analisar:
        parser = parse(dPath)        
        
    if args.tscherchar:
        query(dbPath, args.tscherchar)

    if args.lingias:
        query(dbPath, args.lingias, raw=True)

def parse(dicziunariPath):
    parser = Parser(dicziunariPath)
    parser.parseFile()
        
    print "Entries:   ", len(parser.entries)
    print "Collisions:", parser.collisions
    
    cols = parser.getColumns()
    print "Columns:   ", len(cols), ", ".join(["'%s'" % c for c in cols])
    return parser

DB_OUT_TABLE_NAME = "dicziunari"

def query(sqliteDbPath, query, raw=False):
    if not os.path.exists(sqliteDbPath):
        print >> sys.stderr, "%s not found. Refer to -h for further information."
    conn = sqlite3.connect(sqliteDbPath)
    cursor = conn.cursor()
    
    querySql = "%%%s%%" % query.decode("utf-8")
    
    if raw:
        columns = "*"
        cursor.execute("PRAGMA table_info(%s)" % DB_OUT_TABLE_NAME)
        cols = cursor.fetchall()
    if pathRelatedSrc(sqliteDbPath, DB_SRC_FILE_GRISCHUN):
        primColDeu = "bb"
        primColRum = "ii"
        if not raw:
            columns = "bb, ii"
    else:
        primColDeu = "m"
        primColRum = "n"
        if not raw:
            columns = "m, n"
    sql = "SELECT %s FROM %s WHERE %s LIKE ? OR %s LIKE ?" % \
          (columns, DB_OUT_TABLE_NAME, primColDeu, primColRum)
    cursor.execute(sql, [querySql, querySql])
    res = cursor.fetchall()
    if raw:
        for row in res:
            for i, col in enumerate(row):
                print "%s : %s" % (cols[i][1], col)
            print "-" * 80
    else:
        for m, n, in res:
            print "  %35s : %-35s" % (m, n)

def pathRelatedSrc(path, src):
    return os.path.splitext(src)[0] in path

def createSQLite(sqliteDbPath, parser, colSelect=None):
    # http://www.blog.pythonlibrary.org/2012/07/18/python-a-simple-step-by-step-sqlite-tutorial/
    
    if os.path.exists(sqliteDbPath):
        commands.getstatusoutput('rm -f "%s"' % sqliteDbPath)
    conn = sqlite3.connect(sqliteDbPath)
     
    cursor = conn.cursor()
     
    cols = parser.getColumns()
    C = len(cols)
    if pathRelatedSrc(sqliteDbPath, DB_SRC_FILE_GRISCHUN):
        colMap = {'address':'address',
                  'A': 'aa',
                  'B': 'bb',    # deutsch
                  'C': 'cc',    # key deutsch
                  'D': 'dd',    # geschlecht
                  'E': 'ee',    # grammatik deutsch
                  'F': 'ff',
                  'G': 'gg',    # annotation deutsch
                  'I': 'ii',    # rumantsch
                  'J': 'jj',    # key rumantsch
                  'K': 'kk',    # geschlecht
                  'L': 'll',    # grammatica rumantscha
                  'M': 'mm',
                  'N': 'nn',
                  'O': 'oo',
                  'P': 'pp',
                  'Q': 'qq',    # annotaziun rumantsch
                  'R': 'rr',
                  'S': 'ss',
                  'V': 'vv',
                  'm': 'm', 
                  'n': 'n',     # datum
                  'u': 'u',     # ID
                  }
    else:
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
    # Remap columns on request
    if colSelect:
        if len(colSelect) == 0:
            print >> sys.stderr, 'culuonnas dicziunari es vöd.'
            sys.exit(1)
        m = {}
        for k, v in colSelect.items():
            if k not in colMap:
                print >> sys.stderr, 'culuonna "%s" nö exsista.'
                sys.exit(1)
            m[k] = v
        cols = m.keys()
        C = len(cols)
        colMap = m
        
    # create a table
    colList = ", ".join([colMap[c] for c in cols])
    cursor.execute(u"\n".join(["CREATE TABLE %s\n" % DB_OUT_TABLE_NAME,
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
    cursor.execute('ANALYZE')
    cursor.execute('VACUUM')
    conn.commit()

def packAndEncryptDicziunaris():
    print "Cumprimer dicziunaris..."
    (s, o) = commands.getstatusoutput("tar cjf dicziunaris.tar.bz2 *.lzm *.usr")
    if s != 0:
        print "Errur dürant cumprimer ils dicziunaris: %s (%i)" % (o, s)
        return
    (s, o) = commands.getstatusoutput("openssl aes-256-cbc -in dicziunaris.tar.bz2 -out dicziunaris.tar.bz2.aes")
    if s != 0:
        print "Errur dürant ciffrar ils dicziunaris: %s (%i)" % (o, s)
        return
    (s, o) = commands.getstatusoutput("rm dicziunaris.tar.bz2")
    if s != 0:
        print "Errur rumir sü davo ciffrar ils dicziunaris: %s (%i)" % (o, s)
        return
    
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

_DICT_RE = re.compile(r"([^:{,]*):([^:,}]*)")

def dictArg(argstr):
    try:
        argstr = _DICT_RE.sub(r'"\1":"\2"', argstr)
    except Exception as e:
        raise argparse.ArgumentTypeError('Argument "%s" doesn\'t seem to be a dictionary: %s' % (argstr, str(e)))
    try:
        arg = ast.literal_eval(argstr)
    except Exception as e:
        raise argparse.ArgumentTypeError('Argument "%s" doesn\'t seem to be a dictionary: %s' % (argstr, str(e)))
    if not isinstance(arg, dict):
        raise argparse.ArgumentTypeError('Argument "%s" doesn\'t seem to be a dictionary.' % (argstr))
    return arg

if __name__ == "__main__":
    main()

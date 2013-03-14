#!/usr/bin/python
#
# Dicziunari -- A collection of linguistic tools for the Rhaeto-Romance
#               language
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

import struct, time, sys

def rnd(value, multiple):
    return (value + multiple - 1) & (-multiple)

# 0x6d7b0 : "Bezugsdatensaetze markieren mit xxx"

class Parser:
    dictionariPageCode = 0xc105
    
    def __init__(self, filePath):
        f = open(filePath, "r")
        self.fileData = f.read()
        f.close()
        self.entries = {}
        self.collisions = []
        
    def parseFile(self):
        L = len(self.fileData)
        pos = 0x1000
        while pos < L:
            #                                                |-> page data start (size counts) 
            # type |      |      |      |      |      | size | table |
            # 00 00 00 00 | 00 5E 00 00 | 00 D2 00 09 | 00 59 C1 11 |  
            etype, _, _, _, _, _, esize, table = struct.unpack_from(">HHHHHHHH", self.fileData, pos)
            print "@ %8x : %4i %4x" % (pos, esize, table)
            
            pos += 0x10
            size = esize - 0x02
            pagedata = self.fileData[pos:pos+size]
            
            if table == self.dictionariPageCode:
                self.parsePage(pagedata, etype, pos-0x10)
            
            pos = rnd(pos + esize, 0x400)
    
    def parsePage(self, data, etype, pageAddress):
        
        if etype != 0x0000:
            print "Unknown table entry type: %x" % etype
            return

        pos = 0
        L = len(data)
        
        # At least 4 bytes are required to read the row ID
        while pos < L-4 and 0xC0 != ord(data[pos]):
            rowId, = struct.unpack_from(">I", data, pos)
            pos += 0x04
            
            entry = self.entries.get(rowId, {})
            self.entries[rowId] = entry
            entry["address"] = pageAddress
            
            while pos < L:
                col, = struct.unpack_from(">B", data, pos)
                pos += 1
                
                colLen = 1  # Col len in bytes
                
                if col == 0xC0:
                    if pos < L:
                        tmp, = struct.unpack_from(">B", data, pos)
                        if tmp == 0xc0 or tmp == 0x00:
                            # end of entry (to be verified!)
                            pos = L
                    break
                
                elif col == 0xC1:   # Special control sequences
                    # Encountered
                    #            col  a    b
                    # 0x0006d800 0xc1 0x0b
                    # 0x00071400 0xc1 0x0b 0xc0
                    # 0x0007dc00 0xc1 0x0b 0xc2
                    # 0x00815000 0xc1 0x0f
                    # 0x00334010 0xc1 0x0f 0xc2
                    # 0x0098a000 0xc1 0x05 0xc0
                    # 0x017d5c00 0xc1 0x12 0xc0
                    # 0x0213f4de 0xc1 0x02
                    # 0x019bae63 0xc1 0x16
                    # 0x0615c880 0xc1 0x2D 0xff    (pledari grond)
                    a, = struct.unpack_from(">B", data, pos)
                    pos += 1

                    if a in [0x05, 0x02, 0x0b, 0x0f, 0x12, 0x16, 0x2d]:
                        if pos == L:
                            break
                        b, = struct.unpack_from(">B", data, pos)
                        if b == 0xc0:
                            pos += 1
                            continue
                        elif b == 0xff: # Long string field (pledari grond)
                            pos += 1
                            col, = struct.unpack_from(">B", data, pos)
                            pos += 1
                            colLen = 2
                        elif b == 0xc2: # Unknown data block following (for examples see above)
                            pos = L
                            break
                        else:
                            continue

                elif col == 0x01:
                    # Those magic 01ff05 blocks which seem to have a constant
                    # length of 89 but actually haven't :/
                    ab = struct.unpack_from(">BB", data, pos)
                    if ab == (0xff, 0x05):
                        npos = data.find("\xc0\xc0", pos)
                        if npos == -1:  # probably end of page
                            pos = L
                        else:
                            pos = npos + 2
                        continue
                    elif ab == (0xfc, 0x05): # 0x01 fc 05 blocks (pledari grond)
                        npos = data.find("\xc0", pos)
                        if npos == -1:  # probably end of page
                            pos = L
                        else:
                            pos = npos + 1
                        break
                elif col == 0x02:   # pledari grond
                    # 027ad1f0 0x02 01 02 03 S23
                    # 01d26d70 0x02 01 02 04 INST
                    abc = struct.unpack_from(">BBB", data, pos)
                    pos += 3 + abc[2]
                    continue
                                
                if colLen == 1:
                    clen, = struct.unpack_from(">B", data, pos)
                    pos += 1
                elif colLen == 2:
                    clen, = struct.unpack_from(">H", data, pos)
                    pos += 2
                else:
                    print "Unhandled col length: %i @ %i" % (colLen, pos)
                    sys.exit(1)
                                    
                content = data[pos:pos+clen]
                pos += clen
    
                content = content.decode('mac-roman')
                ecol = chr(col).decode('mac-roman')
                
                if ecol in entry:
                    if content not in "xxx":
                        self.collisions.append([rowId, ecol, [content, entry[ecol]]])
                        print "Entry collision: %x %s %s" % (rowId, ecol, content)
                entry[ecol] = content

    def getColumns(self):
        cols = set()
        for _rowId, row in self.entries.items():
            for col in row:
                cols.add(col)
        return cols


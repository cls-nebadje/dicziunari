
import struct, time, sys

def rnd(value, multiple):
    return (value + multiple - 1) & (-multiple)

# 0x6d7b0 : "Bezugsdatensaetze markieren mit xxx"

class Parser:
    pageSize = 0x400-0x10
    dictionariPageCode = 0xc105
    
    def __init__(self, filePath):
        f = open("Vallader.lzm", "r")
        self.fileData = f.read()
        f.close()
        self.entries = {}
        self.collisions = []
        
    def parseFile(self):
        L = len(self.fileData)
        pos = 0x1000
        while pos < L:
            # type |      |      |      |      |      | size | table |
            # 00 00 00 00 | 00 5E 00 00 | 00 D2 00 09 | 00 59 C1 11 |  
            etype, _, _, _, _, _, esize, table = struct.unpack_from(">HHHHHHHH", self.fileData, pos)
            print "@ %8x : %4i %4x" % (pos, esize, table)
            
            pos += 0x10
            # Problem with esize at entry at 0x87c00 which is somewhat larger
    #        pagedata = data[pos:pos+esize]
            pagedata = self.fileData[pos:pos+self.pageSize]
            
            if table == self.dictionariPageCode:
                self.parsePage(pagedata, etype, pos-0x10)
            
#            pos = rnd(pos + esize, 0x400)
            pos += self.pageSize
    
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
                
                if col == 0x00: # hack because of page data length problem
                    pos = L
                    break
                
                if col == 0xC0:
                    if pos < L:
                        tmp, = struct.unpack_from(">B", data, pos)
                        if tmp == 0xc0 or tmp == 0x00:
                            # end of entry (to be verified!)
                            pos = L
                    break
                
                elif col == 0xC1:   # Special control sequences
                    # Encountered
                    # 0x0006d800 0xc1 0x0b
                    # 0x00071400 0xc1 0x0b 0xc0
                    # 0x0007dc00 0xc1 0x0b 0xc2
                    # 0x00815000 0xc1 0x0f
                    # 0x00334010 0xc1 0x0f 0xc2
                    # 0x0098a000 0xc1 0x05 0xc0
                    # 0x017d5c00 0xc1 0x12 0xc0
                    # 0x0213f4de 0xc1 0x02
                    # 0x019bae63 0xc1 0x16
                    a, b = struct.unpack_from(">BB", data, pos)
                    if a in [0x05, 0x02, 0x0b, 0x0f, 0x12, 0x16]:
                        if b == 0xc0:
                            pos += 0x02
                        elif b == 0xc2: # Unknown data block following (for examples see above)
                            pos = L
                            break
                        else:
                            pos += 0x01
                    continue
                
                if col == 0x01:
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
    
                clen, = struct.unpack_from(">B", data, pos)            
                pos += 1
                
                content = data[pos:pos+clen]
                pos += clen
    
                content = content.decode('mac-roman')
                ecol = chr(col).decode('mac-roman')
#                if ecol not in ['A', 'B', 'E', 'D', 'G', 'I', 'H', 'K', 'J', 'L', 'O', 'N', 'Q', 'P', 'S', 'R', 'T', 'W', 'V', 'X', '_', '^', 'e', 'd', 'k', 'j', 'm', 'n']:
#                    print repr(ecol)
#                    print pos
#                    print content
#                    time.sleep(3)
#                
                    
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

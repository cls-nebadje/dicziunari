
import struct, time, sys

# 0x6d7b0 : "Bezugsdatensaetze markieren mit xxx"

class Parser:
    def __init__(self):
        self.entries = {}
        
    def handle01ff05(self, data):
        print "Detected 0x01ff05 block"
    
    
    def dicziunari(self, data, etype):
        
        if etype == 0x0000:
            pos = 0
            L = len(data)
            
            while pos < L and 0xC0 != ord(data[pos]):
                rowId, = struct.unpack_from(">I", data, pos)
                pos += 0x04
                
                rowCount = self.entries.get(rowId, 0)
                self.entries[rowId] = rowCount + 1
                
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
                        a, b = struct.unpack_from(">BB", data, pos)
                        if a in [0x0b, 0x05, 0x0f]:
                            if b == 0xc0:
                                pos += 0x02
                            elif b == 0xc2: # Unknown data block following (for examples see above)
                                pos = L
                                break
                            else:
                                pos += 0x01
                        continue
                    
                    if col == 0x01:
                        ff, five = struct.unpack_from(">BB", data, pos)
                        if ff == 0xff and five == 0x05:
                            self.handle01ff05(data[pos-1:])
                            pos = L
                            break
        
                    clen, = struct.unpack_from(">B", data, pos)            
                    pos += 1
                    
                    content = data[pos:pos+clen]
                    pos += clen
        
                    content = content.decode('mac-roman')
#                    print "%x : %c : %s" % (rowId, col, content)
        else:
            print "Unknown table entry type: %x" % etype
                
#    time.sleep(1)
#XGauge to ELM converter

import logging
from obd2lib.utils import hex_to_bin
from obd2lib.elmdb import ELMdb
from obd2lib.elmdecoder import decode_answer
from obd2lib.obdconnector import OBDConnector

import pdb

class XGauge2ELM:

    def __init__(self, Name, TXD, RXF, RXD, MTH, units, obd2_obj):
        self.name = Name
        self.TXD = TXD
        self.RXF = RXF
        self.RXD = RXD
        self.MTH = MTH
        self.obd = obd2_obj
        self.units = units
        
        if((len(self.TXD) < 4) and (len(self.TXD)%2 != 0)):  #minimum and even number of characters
            print 'Invalid CAN XGauge'
            return
        if((len(self.RXF) < 12) and (len(self.RXF)%2 != 0)):  #minimum and even number of characters
            print 'Invalid CAN XGauge'
            return
        if((len(self.RXD) < 4) and (len(self.RXD)%2 != 0)):  #minimum and even number of characters
            print 'Invalid CAN XGauge'
            return
        if((len(self.MTH) < 12) and (len(self.MTH)%2 != 0)):  #minimum and even number of characters
            print 'Invalid CAN XGauge'
            return

        if(self.TXD[0] != '0'):
            print 'Invalid CAN XGauge'
            return

        if( len(self.TXD) >= 8 and len(self.TXD) <= 10):
            self.pid = self.TXD[6:] #return characters after the first 6 (PID)
            self.mode = self.TXD[4:6]
            self.txid = self.TXD[1:4]
            self.rxid = ''
            self.rxmask = ''
        else:
            #passive gauge (only listening for data already on the bus)
            fake_txid = int('0x' + self.TXD[0:4], 16)
            self.rxid = hex((fake_txid ^ 0x8) & 0xFF8) #mask off lower 3 bits
            self.rxmask = 0xFF8
            return

        self.offsets = {int(self.RXF[1],16)-1, int(self.RXF[5],16)-1, int(self.RXF[9],16)-1}
        self.matches = {self.RXF[2:4], self.RXF[6:8], self.RXF[10:12]}
        self.data_offset = int(self.RXD[0:2],16)
        self.data_length = int(self.RXD[2:4],16)
        
        if(self.RXF[4] == '8'):
            self.scale = 10
        elif(self.RXF[4] == '4'):
            self.scale = 100
        else: #elif(self.RXF[4] == '2'):
            self.scale = 1
        
        self.multiply = int(self.MTH[0:4],16)
        self.divide = int(self.MTH[4:8],16)
        self.add_sub = int(self.MTH[8:12],16)
        if((self.add_sub & 0x8000) != 0):
            self.add_sub = self.add_sub - 0x10000
        return
    
    def pid(self):
        if( len(self.TXD) >= 8 and len(self.TXD) <= 10):
            return self.TXD[6:] #return characters after the first 6 (PID)
        else:
            return ''

#    def mode(self):
#        if( len(self.TXD) >= ):
    
    def get_parameter(self):
        if(self.rxid != ''): #is this a passive read?
            print 'not yet impmented'
        else:
            self.obd.run_OBD_command('ATSH ' + self.txid, expert = True) #set the sending ID
            buffer,valid_resp = self.obd.run_OBD_command(self.mode + self.pid, expert = True)
            buffer = '0' + buffer
        #if(valid_resp == 'Y'):
        pdb.set_trace()
        match_test = [buffer[offset*2:offset*2+2] for offset in self.offsets]
        if(match_test == self.matches):
            buffer_bits = len(buffer)*4 #len of buffer is number of octets
            buffer_int = int(buffer,16)
            #shift data right so that result sits at LSb
            interm_result = buffer_int >> (buffer_bits - (self.data_offset + self.data_length))
            interm_result = interm_result & (2**self.data_length-1) #mask off the part we want
            #scale and shift result
            interm_result = ((interm_result * self.multiply) / self.divide) + self.add_sub
            result = interm_result * self.scale
            return result
        else:
            return
        #else:
        #    return
            

def connect(port, baudrate, reconnectattempts, sertimeout):
        connector = OBDConnector(
            port, baudrate, reconnectattempts, sertimeout)
        logging.info('Connecting...')
        success = connector.initCommunication()
        if success != 1:
            logging.error('Connection error...')
            sys.exit(1)
        logging.info('Connected')
        return connector
    
def main():
    obd = connect('com3', 115200, 5, 10)
    obd.run_OBD_command('ATS0') #Turn off spaces in result
    trans_temp = XGauge2ELM('Trans Fluid Temp','07E0221674','046205160674','3010','000100080000','F',obd)
    print trans_temp.get_parameter()
    obd.run_OBD_command('END')
if __name__ == '__main__':
    main()

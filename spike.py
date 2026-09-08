import pyvisa
from datetime import datetime
import time
import math

class Spike:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource('TCPIP0::localhost::5025::SOCKET')
        self.inst.read_termination = '\n'
        self.inst.write_termination = '\n'

        self.__autoVBW__ = True
        self.__autoRBW__ = True
        self.__autoifbwidth__ = True
        self.__current_mode__ = None

        self.inst.write(":BAND:AUTO ON")
        while(self.inst.query("*OPC?") != "1"):
            continue
        self.inst.write(":BAND:VID:AUTO ON")
        while(self.inst.query("*OPC?") != "1"):
            continue
        self.inst.write(":ZS:CAP:IFBWidth:AUTO ON")
        while(self.inst.query("*OPC?") != "1"):
            continue
        self.inst.write(":FORMat:IQ BIN")


    def close(self):
        self.rm.close()


    def set_continuous_mode(self, enabled: bool):
        if(enabled is None):
            raise ValueError("Continuous mode cannot be none")
        if(enabled):
            self.inst.write("INIT:CONT ON")
        if(not enabled):
            self.inst.write("INIT:CONT OFF")

    
    def set_measurement_mode(self, mode: str):
        if(mode is None):
            raise ValueError("Measurement mode cannot be set to none")
        if(mode not in ["SA", "ZS"]):
            raise ValueError("Currently the only implemented modes are: sweep analysis (SA) and Zero-Span IQ mode (ZS)")
        self.inst.write(f"INSTRUMENT:SELECT {mode}")
        self.__current_mode__ = mode

    def get_measurement_mode(self):
        return self.__current_mode__

    def set_rbw(self, rbw):
        if(rbw is None):
            raise ValueError("rbw cannot be set to none")
        if(self.__autoRBW__):
                print("RBW is set to auto, please disable before manually setting it")
                return
        if(rbw < 10000 or rbw > 3000000000):
            raise ValueError("rbw must be in allowed range of 10000 to 3000000000")
        
        
        self.inst.write(f":BAND {rbw}")

    def get_rbw(self):
        return self.inst.query(":BAND?")

    def toggle_auto_rbw(self):
            if(self.__autoRBW__):
                self.inst.write(":BAND:AUTO OFF")
                self.__autoRBW__ = False
                print("Auto rbw off")
            else:
                self.inst.write(":BAND:AUTO ON")
                self.__autoRBW__ = True
                print("auto rbw on")

    def get_auto_rbw_status(self):
        return self.__autoRBW__

    def set_vbw(self, vbw):
        if(vbw is None):
            raise ValueError("vbw cannot be set to none")
        if(vbw < 10000 or vbw > 10000000):
            raise ValueError("vbw must be in allowed range of 10000 to 10000000")
        if(self.__autoVBW__):
            print("VBW is set to auto, please disable before manually setting it")
            return
        
        self.inst.write(f":BAND:VID {vbw}")

    def get_vbw(self):
        return self.inst.query(":BAND:VID?")

    def toggle_auto_vbw(self):
        if(self.__autoVBW__):
            self.inst.write("BAND:VID:AUTO OFF")
            self.__autoVBW__ = False
        else:
            self.inst.write("BAND:VID:AUTO ON")
            self.__autoVBW__ = True

    def get_auto_vbw_status(self):
        return self.__autoVBW__

    def set_span(self, span):
        if(span is None):
            raise ValueError("span cannot be set to none")
        if(span > 6000000000 or span < 20):
            raise ValueError("span cannot be set to more than 6GHz or less than 20Hz")
        self.inst.write(f"FREQ:SPAN {span}Hz")

    def get_span(self):
        return self.inst.write("FREQ:SPAN?")

    def set_cent(self, cent):
        if(cent is None):
            raise ValueError("center cannot be set to none")
        if(self.__current_mode__ == "SA"):
            self.inst.write(f"FREQ:CENT {cent}Hz")
        elif(self.__current_mode__ == "ZS"):
            self.inst.write(f":ZS:CAP:CENT {cent}Hz")

    def get_cent(self):
        if(self.__current_mode__ == "SA"):
            return self.inst.query(":FREQ:CENT?")
        elif(self.__current_mode__ == "ZS"):
            return self.inst.query(":ZS:CENT?")

    def set_ref_levels(self, ref):
        if(ref is None):
            raise ValueError("Reference level cannot be set to none")
        if(ref > 20 or ref < -130):
            raise ValueError("Reference level outside of accepted range")
        if(self.__current_mode__ == "SA"):
            self.inst.write(f":POW:RF:RLEV {ref}")
        elif(self.__current_mode__ == "ZS"):
            self.inst.write(f":ZS:CAP:RLEV {ref}")

    def get_ref_levels(self):
        if(self.__current_mode__ == "SA"):
            return self.inst.query(":POW:RF:RLEV?")
        elif(self.__current_mode__ == "ZS"):
            return self.inst.write(f":ZS:CAP:RLEV?")

    def get_unit(self):
        return self.inst.query(":POW:RF:RLEV:UNIT?")

    def start_record(self):
        self.inst.write(f":REC:SWE:STAR")

    def stop_record(self):
        self.inst.write(f":REC:SWE:STOP")

    def record_time(self, rec: int):
        try:
            self.inst.write(f":REC:SWE:STAR")
            while(self.inst.query("*OPC?") != "1"):
                continue
            time.sleep(rec) #find better solution for this so we can do other things while recording
            self.inst.write(f":REC:SWE:STOP")
        except Exception:
            self.inst.write(f":REC:SWE:STOP")
            self.close()

    def set_decimaton(self, type, time, detector):
        if(type is None):
            raise ValueError("Decimation cannot be set to none")
        if(time is None):
            raise ValueError("Time cannot be set to none")
        if(detector is None):
            raise ValueError("Detector cannot be set to none")
        if(type not in ["TIME", "COUNT"]):
            raise ValueError("Decimation type must be either TIME or COUNT")
        if(detector not in ["AVER", "MAX"]):
            raise ValueError("Detector type must be either AVER or MAX")
        
        self.inst.write(f":REC:SWE:DEC:TYPE {type}")
        while(self.inst.query("*OPC?") != "1"):
            continue
        self.inst.write(f":REC:SWE:DEC:TIME {time}")
        while(self.inst.query("*OPC?") != "1"):
            continue
        self.inst.write(f":REC:DEC:DET {detector}")

    def get_device(self):
        return self.inst.query("*IDN?")

    def set_start_freq(self, freq):
        if(freq is None):
            raise ValueError("Start frequency cannot be set to none")
        self.inst.write(f":FREQ:STAR {freq}")

    def get_start(self):
        return self.inst.query(":FREQ:STAR?")

    def set_stop_freq(self, freq):
        if(freq is None):
            raise ValueError("Stop frequency cannot be set to none")
        self.inst.write(f":FREQ:STOP {freq}")

    def get_stop(self):
        return self.inst.query(":FREQ:STOP?")

    def get_span(self):
        return self.inst.query(":FREQ:SPAN?")

    def set_directory(self, dir):
        if(dir is None):
            raise ValueError("Directory cannot be set to none")
        self.inst.write(f":REC:SWE:FILE:DIR {dir}")

    def get_directory(self):
        return self.inst.query(f":REC:SWE:FILE:DIR?")

    def set_max_size(self, size):
        self.inst.write(f":REC:SWE:FILE:SIZE:MAX {size}")

    def is_recording(self):
        status = self.inst.query(":REC:SWE:STATUS?")
        if(status == "0"):
            return False
        elif(status == "1"):
            return True

    def recording_info(self):
        if(not self.is_recording):
            print("Analyzer is not currently recording")
            return
        print(f"Sweep count: {self.inst.query(":REC:SWE:COUNT?")}")
        print(f"Current file size: {self.inst.query(":REC:SWE:FILE:SIZE?")}")

    def set_sample_rate(self, rate):
        n = rate/61.44
        if(not math.log2(n).is_integer()):
            raise ValueError("Invalid Sampling rate. Sampling rate must be equivalent to 61.44MS/n where n is the decimation." \
            "n must be a power of 2 and must be no less than 1 and no greater than 4096")
        self.inst.write(f":ZS:CAP:SRAT {rate}")

    def get_sample_rate(self):
        return self.inst.write(f":ZS:CAP:SRAT?")

    def set_ifbwidth(self, freq):
        if(self.__autoifbwidth__):
            print("Auto ifbwidth is turned on, no change applied")
            return
        self.inst.write(f":ZS:CAP:IFBW {freq}hz")

    def get_ifbwidth(self):
        self.inst.write(f":ZS:CAPture:IFBWidth?")

    def get_auto_ifbwidth_status(self):
        return self.__autoifbwidth__

    def toggle_auto_ifbwidth(self):
        if(self.__autoifbwidth__):
            self.inst.write(f":ZS:CAPture:IFBWidth:AUTO OFF")
            self.__autoifbwidth__ = False
        else:
            self.inst.write(f":ZS:CAPture:IFBWidth:AUTO ON")
            self.__autoifbwidth__ = True


    def set_iq_sweep_time(self, time):
        self.inst.write(f":ZS:CAP:SWE:TIME {time}")

    def get_iq_sweep_time(self):
        self.inst.write(f":ZS:CAP:SWE:TIME?")

    def record_iq(self, save_file, end_timestamp = None, duration = None, ):
        if(end_timestamp is None and duration is None):
            raise ValueError("An end time stamp or a time amount must be provided to record iq")
        if(end_timestamp is not None and duration is not None):
            raise ValueError("Too many period arguments proided")
        
        self.set_continuous_mode(True)
        while(self.inst.query("*OPC?") != "1"):
                    continue

        if(end_timestamp):
            with open(save_file, "wb") as f:
                while(datetime.now().timestamp() is not end_timestamp):
                    f.write(self.inst.query_binary_values(":FETCH:ZS? 1", datatype='s', container=bytes))
        else:
            with open(save_file, "wb") as f:
                start = datetime.now().timestamp()
                current = 0
                while(duration > current):
                    f.write(self.inst.query_binary_values(":FETCH:ZS? 1", datatype='s', container=bytes))
                    current = datetime.now().timestamp() - start

    def write_meta_data():
        print("Todo")

    def single_capture(self, save_file):
        print(f"start of capture at {datetime.now().timestamp()}" )
        self.inst.write("INIT")
        while(self.inst.query("*OPC?") != "1"):
            continue
        response = self.inst.query_binary_values(":FETCH:ZS? 1", datatype='s', container=bytes)
        print(f"end of capture and retrieval at {datetime.now().timestamp()}" )
        with open(save_file, "wb") as f:
            f.write(response)








    

    

        


    

        
        
    
        

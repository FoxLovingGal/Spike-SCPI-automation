import pyvisa
from datetime import datetime
import time
import math
import sigmf
from sigmf.utils import get_sigmf_iso8601_datetime_now
import numpy as np

class Spike:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource('TCPIP0::localhost::5025::SOCKET')
        self.inst.read_termination = '\n'
        self.inst.write_termination = '\n'

        self.__autoVBW = True
        self.__autoRBW = True
        self.__autoifbwidth = True
        self.__current_mode = None
        self.__sample_rate = None
        self.__center_frequency = None

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
        self.__current_mode = mode

    def get_measurement_mode(self):
        return self.__current_mode

    def set_rbw(self, rbw):
        if(rbw is None):
            raise ValueError("rbw cannot be set to none")
        if(self.__autoRBW):
                print("RBW is set to auto, please disable before manually setting it")
                return
        if(rbw < 10000 or rbw > 3000000000):
            raise ValueError("rbw must be in allowed range of 10000 to 3000000000")
        
        
        self.inst.write(f":BAND {rbw}")

    def get_rbw(self):
        return self.inst.query(":BAND?")

    def toggle_auto_rbw(self):
            if(self.__autoRBW):
                self.inst.write(":BAND:AUTO OFF")
                self.__autoRBW = False
                print("Auto rbw off")
            else:
                self.inst.write(":BAND:AUTO ON")
                self.__autoRBW = True
                print("auto rbw on")

    def get_auto_rbw_status(self):
        return self.__autoRBW

    def set_vbw(self, vbw):
        if(vbw is None):
            raise ValueError("vbw cannot be set to none")
        if(vbw < 10000 or vbw > 10000000):
            raise ValueError("vbw must be in allowed range of 10000 to 10000000")
        if(self.__autoVBW):
            print("VBW is set to auto, please disable before manually setting it")
            return
        
        self.inst.write(f":BAND:VID {vbw}")

    def get_vbw(self):
        return self.inst.query(":BAND:VID?")

    def toggle_auto_vbw(self):
        if(self.__autoVBW):
            self.inst.write("BAND:VID:AUTO OFF")
            self.__autoVBW = False
        else:
            self.inst.write("BAND:VID:AUTO ON")
            self.__autoVBW = True

    def get_auto_vbw_status(self):
        return self.__autoVBW

    def set_span(self, span):
        if(span is None):
            raise ValueError("span cannot be set to none")
        if(span > 15000000000 or span < 20):
            raise ValueError("span cannot be set to more than 15GHz or less than 20Hz")
        self.inst.write(f"FREQ:SPAN {span}Hz")

    def get_span(self):
        return self.inst.write("FREQ:SPAN?")

    def set_cent(self, cent):
        if(cent is None):
            raise ValueError("center cannot be set to none")
        if(self.__current_mode == "SA"):
            self.inst.write(f"FREQ:CENT {cent}Hz")
        elif(self.__current_mode == "ZS"):
            self.inst.write(f":ZS:CAP:CENT {cent}Hz")
        self.__center_frequency = cent

    def get_cent(self):
        if(self.__current_mode == "SA"):
            return self.inst.query(":FREQ:CENT?")
        elif(self.__current_mode == "ZS"):
            return self.inst.query(":ZS:CENT?")

    def set_ref_levels(self, ref):
        if(ref is None):
            raise ValueError("Reference level cannot be set to none")
        if(ref > 20 or ref < -130):
            raise ValueError("Reference level outside of accepted range")
        if(self.__current_mode == "SA"):
            self.inst.write(f":POW:RF:RLEV {ref}")
        elif(self.__current_mode == "ZS"):
            self.inst.write(f":ZS:CAP:RLEV {ref}")

    def get_ref_levels(self):
        if(self.__current_mode == "SA"):
            return self.inst.query(":POW:RF:RLEV?")
        elif(self.__current_mode == "ZS"):
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
        self.__sample_rate = rate
        self.inst.write(f":ZS:CAP:SRAT {rate}")

    def get_sample_rate(self):
        return self.inst.write(f":ZS:CAP:SRAT?")

    def set_ifbwidth(self, freq):
        if(self.__autoifbwidth):
            print("Auto ifbwidth is turned on, no change applied")
            return
        self.inst.write(f":ZS:CAP:IFBW {freq}hz")

    def get_ifbwidth(self):
        self.inst.write(f":ZS:CAPture:IFBWidth?")

    def get_auto_ifbwidth_status(self):
        return self.__autoifbwidth

    def toggle_auto_ifbwidth(self):
        if(self.__autoifbwidth):
            self.inst.write(f":ZS:CAPture:IFBWidth:AUTO OFF")
            self.__autoifbwidth = False
        else:
            self.inst.write(f":ZS:CAPture:IFBWidth:AUTO ON")
            self.__autoifbwidth = True


    def set_iq_sweep_time(self, time):
        self.inst.write(f":ZS:CAP:SWE:TIME {time}")

    def get_iq_sweep_time(self):
        self.inst.write(f":ZS:CAP:SWE:TIME?")


    def record_iq(self, save_file, metadata_name,  end_timestamp):
        if(end_timestamp is None):
            raise ValueError("An end time stamp or a time amount must be provided to record iq")
        
        self.set_continuous_mode(True)
        while(self.inst.query("*OPC?") != "1"):
                    continue

        recording = sigmf.SigMFFile(
            data_file=save_file,
            global_info={
                sigmf.DATATYPE_KEY: np.int16,
                sigmf.SAMPLE_RATE_KEY: self.__sample_rate,
                sigmf.FREQUENCY_KEY:self.__center_frequency,
            },

        )
        index = 0

        if(end_timestamp):
            with open(save_file, "ab") as f:
                while(datetime.now().timestamp() < end_timestamp):
                    capture = self.inst.query_binary_values(":FETCH:ZS? 1", datatype='s', container=bytes)
                    capture_array = np.frombuffer(capture, dtype=np.int16)
                    capture_array.tofile(f)
                    recording.add_capture(
                        start_index=index,
                        metadata={
                            sigmf.DATETIME_KEY: get_sigmf_iso8601_datetime_now(),
                        }
                    )
                    index += capture_array.size

        recording.tofile(metadata_name)



    def single_capture(self, save_file):
        print(f"start of capture at {datetime.now().timestamp()}" )
        self.inst.write("INIT")
        while(self.inst.query("*OPC?") != "1"):
            continue
        response = self.inst.query_binary_values(":FETCH:ZS? 1", datatype='s', container=bytes)
        capture_array = np.frombuffer(response, dtype=np.int16)
        print(f"end of capture and retrieval at {datetime.now().timestamp()}" )
        capture = sigmf.fromarray(capture_array)
        capture.set_global_field("sample_rate", self.__sample_rate)
        capture.set_global_field("recorder", "Signal Hound Spike")
        capture.tofile(save_file)








    

    

        


    

        
        
    
        

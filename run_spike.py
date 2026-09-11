from spike import Spike

import time
from datetime import datetime, timezone, timedelta

import pandas as pd

class RunSpike: 
    def __init__(self):
        self.analyzer = Spike()
        self.mode = "Sweep"


    def run_recording(self,
        df,
        mode="schedule",
        start_index=0,
        stop_event=None,
        move_writer=None,
        move_csv_handle=None,):

        skipped_old = 0
        curr_sat = None
        
        for i in range(start_index, len(df)):
            if curr_sat != df.iloc[i]["Satellite"]:
                curr_sat = df.iloc[i]["Satellite"]
                start_time = df.iloc[i]["Timestamp (UTC)"]

                if(self.analyzer.is_recording()):
                    self.analyzer.stop_record()

                print(f"Following: {curr_sat}, start_time={start_time}...")
                self.analyzer.start_record()
            if stop_event is not None and stop_event.is_set():
                if(self.analyzer.is_recording()):
                    self.analyzer.stop_record()
                return {
                    "status": "stopped",
                    "next_index": i,
                    "skipped_old": skipped_old,
                }

            row = df.iloc[i]
            sample_time = self.parse_sample_time(row["Timestamp (UTC)"])



            should_continue = self.wait_until_sample_time(
                sample_time,
                stop_event=stop_event,
            )

            if not should_continue:
                if(self.analyzer.is_recording()):
                    self.analyzer.stop_record()
                return {
                    "status": "stopped",
                    "next_index": i,
                    "skipped_old": skipped_old,
                }



    
    def wait_until_sample_time(self, sample_time, stop_event=None):
        """
        Wait until the sample timestamp.

        If stop_event is set while waiting, return False.
        This lets the scheduler interrupt the current df and switch to override.
        """
        while datetime.now(timezone.utc) < sample_time:
            if stop_event is not None and stop_event.is_set():
                return False

            time.sleep(0.02)

        return True


    def parse_sample_time(self, value):
        return pd.to_datetime(value, utc=True).to_pydatetime()

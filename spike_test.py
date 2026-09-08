from spike import Spike
import time


RESULTS = []

def run_tests(name, func):
    print("\n" + "-" * 70)

    print(f"Running test of: {name}")

    result = func()

    if(result):
        print(f"{name} passed")
    else:
        print(f"{name} failed")

    RESULTS.append((name, result))
    


def main():
    
    def test_connecting():
        try:
            analyzer = Spike()
            print(f"Device info: {analyzer.get_device()}")
            analyzer.close()

            return True
        except Exception:
            return False

    run_tests("Connection test", test_connecting)
    analyzer = Spike()


    def not_recording():
        try:
            analyzer.stop_record()
            print(f"stopping recording did not throw an error")
            return True
        except Exception:
            print(f"Stopping recording threw following error an  exception")
            return False

    run_tests("not recording test", not_recording)

    def recording_status_test():
        analyzer.start_record()
        result = analyzer.is_recording()
        if(not result):
            print(f"did not detect the analyzer recording when it should have, instead sent {result}")
            analyzer.stop_record()
            return False

        analyzer.stop_record()
        result = analyzer.is_recording()

        if(result):
            print(f"detected that the analyzer was recording when it shouldn't have been: result was {result}")
            return False
        return True

    run_tests("recording_status test", recording_status_test)

    def set_mode_none():
        try:
            analyzer.set_measurement_mode(None)
        except ValueError:
            return True
        return False

    run_tests("Mode none test", set_mode_none)

    def set_mode_invalid():
        try:
            analyzer.set_measurement_mode("NA")
        except ValueError:
            return True
        return False

    run_tests("Invalid mode test", set_mode_invalid)

    def set_mode_sweep():
        try:
            current = analyzer.get_measurement_mode()
            analyzer.set_measurement_mode("SA")
            next = analyzer.get_measurement_mode()
            if(current is not next and next == "SA"):
                return True
        except Exception:
            return False
        return False

    run_tests("Setting mode to sweep test", set_mode_sweep)

    def ref_level_none_test():
        try:
            analyzer.set_ref_levels(None)
            return False
        except ValueError:
            return True

    run_tests("None error ref level test", ref_level_none_test)

    def ref_level_high_test():
        try:
            analyzer.set_ref_levels(30)
            return False
        except ValueError:
            return True

    run_tests("High reference level test", ref_level_high_test)

    def ref_level_low_test():
        try:
            analyzer.set_ref_levels(-150)
            return False
        except ValueError:
            return True

    run_tests("Low reference level test", ref_level_low_test)

    def ref_level_correct():
        try:
            analyzer.set_ref_levels(-40)
            current = analyzer.get_ref_levels()
            analyzer.set_ref_levels(-30) #originally -50
            next = analyzer.get_ref_levels()
            if(current != next and next == "-30"): 
                return True
        except ValueError:
            return False
        return False

    run_tests("no-error reference levels test", ref_level_correct)

    def rbw_none_test():
        try:
            analyzer.set_rbw(None)
            return False
        except ValueError:
            return True

    run_tests("rbw none test", rbw_none_test)

    def rbw_low_test():
        if(analyzer.get_auto_rbw_status()):
            analyzer.toggle_auto_rbw()
        try:
            analyzer.set_rbw(100)
            return False
        except ValueError:
            return True

    run_tests("rbw low test", rbw_low_test)

    def rbw_high_test():
        if(analyzer.get_auto_rbw_status()):
            analyzer.toggle_auto_rbw()
        try:
            analyzer.set_rbw(30000000000)
            return False
        except ValueError:
            return True

    run_tests("rbw high test", rbw_high_test)

    def rbw_auto_test():
        if(not analyzer.get_auto_rbw_status()):
            analyzer.toggle_auto_rbw()
        previous = analyzer.get_rbw()
        print(int(previous))
        analyzer.set_rbw(float(previous) + 1)

        if(previous == analyzer.get_rbw()):
            return True
        return False

    run_tests("auto rbw test", rbw_auto_test)

    def vbw_none_test():
        try:
            analyzer.set_vbw(None)
            return False
        except ValueError:
            return True

    run_tests("vbw none test", vbw_none_test)

    def vbw_low_test():
        if(analyzer.get_auto_vbw_status()):
            analyzer.toggle_auto_vbw()
        try:
            analyzer.set_vbw(100)
            return False
        except ValueError:
            return True

    run_tests("vbw low test", vbw_low_test)

    def vbw_high_test():
        if(analyzer.get_auto_vbw_status()):
            analyzer.toggle_auto_vbw()
        try:
            analyzer.set_vbw(30000000000)
            return False
        except ValueError:
            return True

    run_tests("vbw high test", vbw_high_test)

    def vbw_auto_test():
        if(not analyzer.get_auto_vbw_status()):
            analyzer.toggle_auto_vbw()
        previous = analyzer.get_vbw()
        print(int(previous))
        analyzer.set_vbw(float(previous) + 1)

        if(previous == analyzer.get_vbw()):
            return True
        return False

    run_tests("auto vbw test", vbw_auto_test)

    def set_span_test():
        first = analyzer.get_span()
        analyzer.set_span(float(first) + 100)
        second = analyzer.get_span()
        if(first == second):
            return False
        return True

    run_tests("set span test", set_span_test)

    def set_span_none_test():
        try:
            analyzer.set_span(None)
            return False
        except ValueError:
            return True

    run_tests("set span none test", set_span_none_test)


    def set_span_high_test():
        try:
            analyzer.set_span(6000000001)
            return False
        except ValueError:
            return True

    run_tests("set span high test", set_span_high_test)

    def set_span_low_test():
        try:
            analyzer.set_span(19)
            return False
        except ValueError:
            return True

    run_tests("set span low test", set_span_low_test)

    def set_center_frequency_none():
        try:
            analyzer.set_cent(None)
            return False
        except ValueError:
            return True

    run_tests("set center frequency none test", set_center_frequency_none)

    def set_center_frequency():
        analyzer.set_cent(3000000000)
        second = analyzer.get_cent()

        if(second != "3e+9"):
            return False
        analyzer.set_cent(3000000500)
        third = analyzer.get_cent()
        if(second == third):
            return False
        return True

    run_tests("set center frequency test", set_center_frequency)



    def sweep_recording():
            print(f"Current span: {analyzer.get_span()}")
            print(f"Current start freq: {analyzer.get_start()}")
            print(f"Curent center freq: {analyzer.get_cent()}")
            print(f"Current stop freq: {analyzer.get_stop()}")
            print(f"Current reference level: {analyzer.get_ref_levels()}{analyzer.get_unit()}")
            analyzer.set_directory("/home/research/Documents/SCPI_automation/SCPI_automation")
            analyzer.set_cent(12000000000)
            analyzer.set_span(500000000)
            analyzer.record_time(10)

    sweep_recording()

    def iq_capture_test():
        analyzer.set_measurement_mode("ZS")
        if(not analyzer.get_auto_ifbwidth_status):
            analyzer.toggle_auto_ifbwidth
        analyzer.set_ref_levels(-30) #originally -50
        analyzer.set_iq_sweep_time(0.001)
        analyzer.set_sample_rate(61.440)
        analyzer.set_cent(12000000000)
        analyzer.single_capture("test_capture_3.iq")


    iq_capture_test()

    def iq_recording_test():
        analyzer.set_measurement_mode("ZS")
        if(not analyzer.get_auto_ifbwidth_status):
            analyzer.toggle_auto_ifbwidth
        analyzer.set_ref_levels(-30) #originally -50
        analyzer.set_iq_sweep_time(0.001)
        analyzer.set_sample_rate(61.440)
        analyzer.set_cent(12000000000)
        analyzer.record_iq(save_file="iq_record3.iq", duration=20)

    iq_recording_test()
        

        


    analyzer.close()

    print("\n" + "-" * 70)
    print("SUMMARY")
    print("-" * 70)
    passed = sum(1 for _, ok in RESULTS if ok)
    failed = [name for name, ok in RESULTS if not ok]
    print(f"{passed}/{len(RESULTS)} tests passed")
    if failed:
        print("Failed tests:")
        for name in failed:
            print(f"  - {name}")

    return 0 if not failed else 1
        
    

if __name__ == "__main__":
    raise SystemExit(main())
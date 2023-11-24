#python command_hid.py --command xxxxxxxxxxxxx
#command_hid.exe --command xxxxxxxxxxx
'''
rogon release notes
based on hid command V1.1.0
1. Remove unnecessary "prints".
2. Optimize architecture.
'''
import argparse
import pywinusb.hid as hid
import threading
import time

def read_hid_device(hid_device, result, timeout):
    start_time = time.time()
    while True:
        input_reports = hid_device.find_input_reports()
        if input_reports:
            data = input_reports[0].get()
            result.append(data)
            break
        if time.time() - start_time > timeout:
            print("read over time")
            break

def send_command_to_hid_device(vid, pid, command_str):
    try:
        all_hids = hid.HidDeviceFilter(vendor_id=vid, product_id=pid).get_devices()
        target_device = all_hids[0] if all_hids else None

        if target_device:
            target_device.open()

            # 將字串 兩個一组 變十進制
            command = bytes.fromhex(command_str)
            full_command = bytes([0x06, len(command) + 3, 0x00]) + command#just for airoha system
            full_command += bytes([0] * (256 - len(full_command)))
            target_device.send_output_report(full_command)
            print("command send to VID: 0x{:04X}, PID: 0x{:04X} correct".format(vid, pid))
            time.sleep(1)

            result = []
            thread = threading.Thread(target=read_hid_device, args=(target_device, result, 3.0))
            thread.start()
            thread.join()
            if result:
                data = result[0]
                length = data[1]
                hex_data = " ".join([f"{x:02X}" for x in data[3:3+length]])
                print(f"data get: {hex_data}")
            target_device.close()
        else:
            print(f"didn't find HID(VID: 0x{vid:04X}, PID: 0x{pid:04X}) device")
    except Exception as e:
        print(f"send fail：{e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="hid command V1.1.0")
    parser.add_argument("--command", help="command you want", required=True)
    args = parser.parse_args()

    # 指定 VID 和 PID
    vid = 0x0000
    pid = 0x0000
    send_command_to_hid_device(vid, pid, args.command)

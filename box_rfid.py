import evdev
class rfid:
    def __init__(self,device_path):   
        # Find the appropriate input self.device path
        self.device_path = device_path
        # Create an input self.device object
        self.device = evdev.InputDevice(self.device_path)
        # Initialize an empty string to store RFID tag IDs
    def read(self):
        rfid_id = ""  

        for event in self.device.read_loop():
            if event.type == evdev.ecodes.EV_KEY and event.value == 1:  # Check for key press events
                key_value = evdev.ecodes.KEY[event.code]
                if key_value.startswith("KEY_") and not key_value.endswith("ENTER"):  # Check if it's a key event (excluding Enter)
                    rfid_id += str(key_value[4:])  # Concatenate the key value to the RFID ID string

                elif key_value.endswith("ENTER"):  # If Enter key is pressed
                    if len(rfid_id) < 10:
                        return "error"
                    return rfid_id
                    rfid_id = ""  # Reset RFID ID string after printing
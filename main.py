import cv2
import numpy as np
from sicrmlb.utils.device import Device

if __name__ == "__main__":
    device = Device()
    device.start_capture()  # Optionally, you can pass a device_id
    
    while True:
        raw = device.get_frame()
        frame = cv2.cvtColor(np.array(raw), cv2.COLOR_RGB2BGR)
        cv2.imshow("Android Screen", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    device.stop_capture()
    cv2.destroyAllWindows()
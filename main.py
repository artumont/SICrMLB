import cv2
import numpy as np
from sicrmlb.gamestate.elixir.detector import ElixirDetector
from sicrmlb.utils.device import Device

if __name__ == "__main__":
    device = Device()
    device.start_capture()  # Optionally, you can pass a device_id
    
    while True:
        raw = device.get_frame()
        frame = cv2.cvtColor(np.array(raw), cv2.COLOR_RGB2BGR)
        # arena tiles
        # cv2.rectangle(
        #     frame,
        #     (int(22), int(62)),
        #     (int(52 + 16 * 18), int(296 + 12.6 * 15)),
        #     color=(0, 255, 0),
        #     thickness=2,
        # )
        
        # cards
        # cv2.rectangle(
        #     frame,
        #     (int(72), int(535)),
        #     (int(72 + 72 * 4), int(520 + 104)),
        #     color=(255, 0, 255),
        #     thickness=2,
        # )
        
        # elixir
        # cv2.rectangle(
        #     frame,
        #     (int(72), int(625)),
        #     (int(72 + 28.8 * 10), int(625 + 20)),
        #     color=(0, 255, 255),
        #     thickness=2,
        # )
        
        elixir_detector = ElixirDetector()
        elixir_state = elixir_detector.perform_analysis(raw)

        cv2.putText(
            frame,
            f"Elixir: {elixir_state.elixir_amount}",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )
        
        cv2.putText(
            frame,
            f"Elixir %: {elixir_state.elixir_percentage * 100}",
            (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )
        
        cv2.imshow("Android Screen", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            # raw.save("testing_frame.png")
            break

    device.stop_capture()
    cv2.destroyAllWindows()
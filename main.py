import cv2
import numpy as np
from sicrmlb.utils.device.capture import VideoCapture

if __name__ == "__main__":
    capture = VideoCapture()
    capture.start_capture()  # Optionally, you can pass a device_id
    
    while True:
        raw = capture.get_frame()
        if raw is None:
            print("[debug] capture.get_frame() returned None -> stopping")
            break

        # If it's raw bytes from ffmpeg, inspect them and try decode
        try:
            if isinstance(raw, (bytes, bytearray)):
                b = bytes(raw)
                n = len(b)
                head = b[:8]
                print(f"[debug] got bytes len={n} head={head.hex()}")

                # JPEG?
                if head.startswith(b"\xff\xd8"):
                    img = cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR)
                    if img is None:
                        print("[debug] imdecode(jpeg) failed; skipping")
                        continue
                    frame = img

                # PNG?
                elif head.startswith(b"\x89PNG"):
                    img = cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR)
                    if img is None:
                        print("[debug] imdecode(png) failed; skipping")
                        continue
                    frame = img

                else:
                    # Could be rawvideo - try decode first; if that fails, report size
                    img = cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR)
                    if img is not None:
                        frame = img
                    else:
                        print(f"[debug] Unrecognized byte stream (len={n}), not an encoded image. Skipping frame.")
                        continue

            else:
                # existing PIL / numpy handling
                frame = raw
                if hasattr(frame, "tobytes") and hasattr(frame, "mode"):
                    frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
                else:
                    frame = np.asarray(frame)
                    if frame.ndim == 3 and frame.shape[2] == 3:
                        # if colors look wrong swap if needed:
                        # frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        pass
        except Exception as e:
            print(f"[debug] exception processing frame: {e}")
            continue

        # final sanity: ensure frame is a valid image
        if not isinstance(frame, np.ndarray):
            print("[debug] frame not ndarray after processing, skipping")
            continue
        if frame.size == 0:
            print("[debug] empty frame, skipping")
            continue

        cv2.imshow("Android Screen", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    capture.stop_capture()
    cv2.destroyAllWindows()
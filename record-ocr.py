import time
import argparse
import io
import mss
import gzip


from PIL import Image
import numpy as np
import tesserocr


def record(log_file):    
    last_time = time.time()
    buf = io.BytesIO()
    compressed = gzip.GzipFile(fileobj=buf, mode="w")
    print("Press CTRL+C to save log file and exit")

    try:
        with mss.mss() as sct:
            while True:
                # Get raw pixels from the screen, save it to a Numpy array
                img = np.array(sct.grab(sct.monitors[0]))

                # Extract text from image and write to compressed stream
                with tesserocr.PyTessBaseAPI() as api:
                    api.SetImage(Image.fromarray(img))
                    data = api.GetUTF8Text().encode("utf8")
                    compressed.write(data)

                # Calculate fps
                fps = 1 / (time.time() - last_time)
                last_time = time.time()
                log_size = buf.getbuffer().nbytes
                print(f'FPS: {fps:.2f}, log_size: {log_size}kb')
    except KeyboardInterrupt:
        compressed.close()
        with open(log_file, "wb") as f:
            f.write(buf.getbuffer())

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="The file to record to")
    args = parser.parse_args()

    record(args.filename)

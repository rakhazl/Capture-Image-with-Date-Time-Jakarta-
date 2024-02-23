from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
import cv2
import os
import datetime
import pytz

app = Flask(__name__)

model = YOLO("*.pt")
camera = cv2.VideoCapture("...") #edit cam path

# Folder untuk menyimpan capture
capture_folder = "..." #edit folder path for results capture

capture_count = 1

# Variabel untuk menandai apakah objek sudah melewati batas koordinat atau belum
object_passed_boundary = False
# Fungsi agar capture hanya 1 kali
boundary2_crossed = False
# Batas koordinat yang ingin Anda tentukan
y_min_boundary1 = ... #edit coordinat y_min
y_max_boundary1 = ... #edit coordinat y_min
y_min_boundary2 = ... #edit coordinat y_min
y_max_boundary2 = ... #edit coordinat y_min

def draw_label(frame, model, result):
        for r in result:
                annotator = Annotator(frame, line_width=1)
                boxes = r.boxes
                result = model(camera)
                for box in boxes:
                        b = box.xyxy[0]
                        c = box.cls

                        key = model.names[int(c)]
                        probs = box.conf[0].item()
                        annotator.box_label(b,
                                        model.names[int(c)]+str(round(box.conf[0].item(), 2)),
                                        color=colors(c, True))

                        print(box.xyxy)

# Fungsi untuk mendapatkan tanggal dan waktu saat ini dalam zona waktu yang diinginkan
def get_current_time():
        # Tentukan zona waktu yang diinginkan (Waktu Indonesia Barat)
        jakarta_timezone = pytz.timezone('Asia/Jakarta')
        # Ambil waktu saat ini dalam zona waktu Jakarta
        current_time = datetime.datetime.now(jakarta_timezone)
        return current_time


# Fungsi untuk mendeteksi objek dan melakukan capture jika objek melewati batas koordinat
def detect_and_capture(frame):
        global object_passed_boundary
        global boundary2_crossed
        global capture_count

        result = model(frame, verbose=False, conf=0.5, imgsz=640)
        result = model.track(frame, persist=True)
        draw_label(frame, model, result)

        # Jika objek belum melewati batas koordinat
        if not object_passed_boundary:
                for r in result:
                        if len(r.boxes) > 0:
                                # Loop semua box yang terdeteksi
                                for box in r.boxes:
                                # Ambil koordinat x_min dan x_max
                                        # x_min = box.xyxy[0][0]
                                        # x_max = box.xyxy[0][2]
                                        y_min = box.xyxy[0][1]
                                        y_max = box.xyxy[0][3]
                                        # Jika objek melewati batas koordinat
                                        if y_min >= y_min_boundary1 and y_max <= y_max_boundary1:
                                                # Lakukan capture
                                                current_time = get_current_time().strftime('%d%b_%H.%M')
                                                capture_path = os.path.join(capture_folder, f"cliproof_capture-{capture_count}_{current_time}.jpg")
                                                cv2.imwrite(capture_path, frame)
                                                print("Objek berada di antara batas koordinat y1 dan terdeteksi. Melakukan capture.")
                                                # Set object_passed_boundary menjadi True agar tidak melakukan capture lagi
                                                object_passed_boundary = True
                                                capture_count += 1
                                                break

                                                if y_min >= y_min_boundary2 and y_max <= y_max_boundary2:
                                                        # Lakukan capture kedua jika terlewat
                                                        current_time = get_current_time().strftime('%d%b_%H.%M')
                                                        capture_path = os.path.join(capture_folder, f"cliproof_capture-{capture_count}_{current_time}.jpg")
                                                        cv2.imwrite(capture_path, frame)
                                                        print("Objek berada di antara batas koordinat y1 dan terdeteksi. Melakukan capture.")
                                                        # Set object_passed_boundary menjadi True agar tidak melakukan capture lagi
                                                        object_passed_boundary = True
                                                        capture_count += 1
                                                        break

        # Jika objek telah melewati batas koordinat pertama dan belum melewati batas koordinat kedua
        elif object_passed_boundary and not boundary2_crossed:
                for r in result:
                        if len(r.boxes) > 0:
                        # Loop semua box yang terdeteksi
                                for box in r.boxes:
                                        # Ambil koordinat y_min dan y_max
                                        y_min = box.xyxy[0][1]
                                        y_max = box.xyxy[0][3]
                                        # Jika objek melewati batas koordinat y_min_boundary2 dan y_max_boundary2
                                        if y_min >= y_min_boundary2 and y_max <= y_max_boundary2:
                                        # Set boundary2_crossed menjadi True agar memungkinkan capture kembali pada batas koordinat pertama
                                                boundary2_crossed = True
                                        break
        # Jika objek telah melewati kedua batas koordinat
        elif object_passed_boundary and boundary2_crossed:
                # Set object_passed_boundary dan boundary2_crossed kembali menjadi False untuk menunggu objek baru yang melewati batas koordinat pertama
                object_passed_boundary = False
                boundary2_crossed = False


# Fungsi untuk menghasilkan frame dari camera
def generate_frames0():
        while True:
                success0, frame0 = camera.read()
                if not success0:
                        break

                detect_and_capture(frame0)

                ret, buffer = cv2.imencode('.jpg', frame0)
                frame0 = buffer.tobytes()

if __name__ == '__main__':
        print("File app.py telah berjalan.")
        while True:
                generate_frames0()
                generate_frames1()
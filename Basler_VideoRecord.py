import cv2
import datetime
from pypylon import pylon
import os

# Belirli bir kamerayı başlatma işlemi
def initialize_camera(camera_id):
    os.environ["PYLON_CAMEMU"] = "1"  # Sanal kamera modu
    tl_factory = pylon.TlFactory.GetInstance()
    devices = tl_factory.EnumerateDevices()
    if not devices:
        raise pylon.RuntimeException("Kamera bulunamadı.")
    
    # Kamera ID'sine göre cihazı seçme
    selected_device = None
    for device in devices:
        if device.GetSerialNumber() == camera_id:
            selected_device = device
            break
    
    if not selected_device:
        raise pylon.RuntimeException(f"{camera_id} ID'li kamera bulunamadı.")

    camera = pylon.InstantCamera(tl_factory.CreateDevice(selected_device))
    camera.Open()
    return camera

def get_video_filename():
    # Gün ve saat bilgisi ile video ismi oluşturma
    current_time = datetime.datetime.now()
    filename = current_time.strftime("%Y-%m-%d_%H-%M-%S") + ".mp4"
    return filename

def main():


    camera_id = input("Kamera ID'sini girin: ")
    camera = initialize_camera(camera_id)

    # Kamera parametrelerinden frame boyutlarını alıyoruz
    frame_width = camera.Width.Value
    frame_height = camera.Height.Value
    frame_rate = camera.AcquisitionFrameRateAbs.Value  # FPS değerini alıyoruz
    print("FPS:", frame_rate)

    out = None
    recording = False
    window_name = f"Basler Kamera - {camera_id}"


    try:
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        converter = pylon.ImageFormatConverter()
        converter.OutputPixelFormat = pylon.PixelType_RGB8packed
        converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

        # Pencereyi ayarlanabilir ve başlığı kameranın ID'siyle aç
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        while camera.IsGrabbing():
            grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

            if grabResult.GrabSucceeded():
                # Görüntüyü RGB formatına dönüştürme
                image = converter.Convert(grabResult)
                img = image.GetArray()
                frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                key = cv2.waitKey(1) & 0xFF

                if key == ord('s') and not recording:
                    filename = get_video_filename()
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(filename, fourcc, frame_rate, (frame_width, frame_height))
                    recording = True
                    print("Kayıt başladı.")
                elif key == ord('d') and recording:
                    recording = False
                    if out:
                        out.release()
                        out = None
                    print("Kayıt durdu.")
                elif key == ord('q'):
                    break

                # Kayıt sırasında ekrana yazı ekle
                display_frame = frame.copy()
                if recording:
                    cv2.putText(display_frame, 'KAYIT BASLADI', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)
                    if out:
                        out.write(frame)

                cv2.imshow(window_name, display_frame)

            grabResult.Release()

        camera.StopGrabbing()

    except Exception as e:
        print(f"Hata oluştu: {e}")

    finally:
        camera.Close()
        if out:
            out.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

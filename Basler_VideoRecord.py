import cv2
import datetime
from pypylon import pylon
import os

# Belirli bir kamerayı başlatma işlemi
def initialize_camera(camera_id):
    #os.environ["PYLON_CAMEMU"] = "1"  # Sanal kamera modu
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
    camera_id = "0815-0000"  # Kaydını almak istediğiniz kameranın ID'sini buraya girin
    camera = initialize_camera(camera_id)

    # Kamera parametrelerinden frame boyutlarını alıyoruz
    frame_width = camera.Width.Value
    frame_height = camera.Height.Value
    frame_rate = camera.AcquisitionFrameRateAbs.Value  # FPS değerini alıyoruz
    print("FPS:",frame_rate)

    # Video kaydedici ayarları
    filename = get_video_filename()
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # mp4 uzantısı için fourcc kodu
    out = cv2.VideoWriter(filename, fourcc, frame_rate, (frame_width, frame_height))

    # Kamera sürekli görüntü alırken video kaydetme işlemi
    try:
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        converter = pylon.ImageFormatConverter()
        converter.OutputPixelFormat = pylon.PixelType_RGB8packed
        converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

        while camera.IsGrabbing():
            grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

            if grabResult.GrabSucceeded():
                # Görüntüyü RGB formatına dönüştürme
                image = converter.Convert(grabResult)
                img = image.GetArray()
                frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                cv2.imshow('Basler Kamera', frame)

                # Görüntüyü video dosyasına yazma
                out.write(frame)

                # Çıkış için 'q' tuşuna basıldığında döngüyü sonlandırma
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            grabResult.Release()

        camera.StopGrabbing()

    except Exception as e:
        print(f"Hata oluştu: {e}")

    finally:
        camera.Close()
        out.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

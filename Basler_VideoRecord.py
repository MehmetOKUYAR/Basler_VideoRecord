import cv2
import datetime
from pypylon import pylon
import os

# Basler kamera için gerekli başlatma işlemleri
def initialize_camera():
    # Pylon SDK ile kamera bağlanma işlemi
    #os.environ["PYLON_CAMEMU"] = "1"  # Sanal kamera modu
    tl_factory = pylon.TlFactory.GetInstance()
    devices = tl_factory.EnumerateDevices()
    if not devices:
        raise pylon.RuntimeException("Kamera bulunamadı.")
    camera = pylon.InstantCamera(tl_factory.CreateFirstDevice())
    camera.Open()
    return camera

def get_video_filename():
    # Gün ve saat bilgisi ile video ismi oluşturma
    current_time = datetime.datetime.now()
    filename = current_time.strftime("%Y-%m-%d_%H-%M-%S") + ".mp4"
    return filename

def main():
    camera = initialize_camera()

    # Kamera parametrelerinden frame boyutlarını alıyoruz
    frame_width = camera.Width.Value
    frame_height = camera.Height.Value

    # Video kaydedici ayarları
    filename = get_video_filename()
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # mp4 uzantısı için fourcc kodu
    out = cv2.VideoWriter(filename, fourcc, 20.0, (frame_width, frame_height))

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

from PIL import Image, ImageTk
import pygame
import os
import cv2
import time
import threading

class Presentador:
    def __init__(self, ruta_presentacion, pantalla_idx=0):
        self.ruta = ruta_presentacion
        self.hotcakes_path = os.path.join(self.ruta, 'Hotcakes.mp4')
        self.video_frames2 = [65]
        self.imagenes = sorted(
            [f for f in os.listdir(self.ruta) if f.endswith('.png')],
            key=lambda x: int(''.join(filter(str.isdigit, x)))
        )
        self.indice = 0
        self.clock = pygame.time.Clock()
        self.pantalla_idx = pantalla_idx
        self.miniatura_callback = None
        self.ultima_imagen_path = None
        self.video_en_reproduccion = False
        self._inicializar_pantalla()

    def _inicializar_pantalla(self):
        pygame.init()
        self.ANCHO, self.ALTO = 1000, 700
        os.environ['SDL_VIDEO_WINDOW_POS'] = "100,100"
        self.pantalla = pygame.display.set_mode((self.ANCHO, self.ALTO), pygame.RESIZABLE)
        pygame.display.set_caption("Presentación (Ventana Redimensionable)")

    def mostrar_imagen(self, path):
        self.ultima_imagen_path = path
        imagen = pygame.image.load(path)
        imagen = pygame.transform.scale(imagen, self.pantalla.get_size())
        self.pantalla.blit(imagen, (0, 0))
        pygame.display.flip()

        if self.miniatura_callback:
            pil_image = Image.open(path).resize((200, 120))
            preview = ImageTk.PhotoImage(pil_image)
            self.miniatura_callback(preview)

    def mostrar_siguiente(self):
        if self.indice >= len(self.imagenes):
            return False
        self.video_en_reproduccion = False
        self._mostrar_por_indice(self.indice)
        self.indice += 1
        return self.indice < len(self.imagenes)

    def mostrar_anterior(self):
        self.video_en_reproduccion = False
        if self.indice <= 1:
            self.indice = 0
        else:
            self.indice -= 2
        return self.mostrar_siguiente()

    def _mostrar_por_indice(self, idx):
        archivo = self.imagenes[idx]
        numero = int(''.join(filter(str.isdigit, archivo)))
        path = os.path.join(self.ruta, archivo)

        if numero in self.video_frames2:
            self._mostrar_miniatura_video(self.hotcakes_path)
            self._reproducir_video_archivo(self.hotcakes_path)
        else:
            self.mostrar_imagen(path)
            self.ultima_imagen_path = path

    def _mostrar_miniatura_video(self, video_path):
        if self.miniatura_callback:
            cap = cv2.VideoCapture(video_path)
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, (200, 120))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(frame)
                preview = ImageTk.PhotoImage(img_pil)
                self.miniatura_callback(preview)
            cap.release()

    def _reproducir_video_archivo(self, path, duracion_segundos=60):
        self.pantalla.fill((0, 0, 0))
        pygame.display.flip()
        self.reproducir_video(path, duracion_segundos)

    def redibujar_imagen_actual(self):
        if self.ultima_imagen_path:
            self.mostrar_imagen(self.ultima_imagen_path)

    def reproducir_video(self, path, duracion_segundos=60):
        def _reproducir():
            self.video_en_reproduccion = True
            cap = cv2.VideoCapture(path)
            inicio = time.time()
            while time.time() - inicio < duracion_segundos and cap.isOpened() and self.video_en_reproduccion:
                ret, frame = cap.read()
                if not ret:
                    break

                self.ANCHO, self.ALTO = self.pantalla.get_size()
                frame = cv2.resize(frame, (self.ANCHO, self.ALTO))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                self.pantalla.blit(surface, (0, 0))
                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        cap.release()
                        self.video_en_reproduccion = False
                        return
                    elif event.type == pygame.VIDEORESIZE:
                        self.ANCHO, self.ALTO = event.size

                self.clock.tick(30)
            cap.release()
            self.video_en_reproduccion = False

        threading.Thread(target=_reproducir, daemon=True).start()

    def manejar_eventos_redimension(self):
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                self.ANCHO, self.ALTO = event.size
                self.pantalla = pygame.display.set_mode((self.ANCHO, self.ALTO), pygame.RESIZABLE)
                self.redibujar_imagen_actual()

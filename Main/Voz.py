import pyaudio
import wave
import threading
import os
import time

# --- Configuración inicial ---
BASE_PATH = r"C:\Users\DCL\Desktop\Zai"
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024

audio_device_index = None
audio_stream = None
is_recording = False
frames = []
marks = []
start_time = 0.0
file_number = 1
folder_path = ""
folder_number = 1
ultima_marca_visual = None

conteo_etiquetas = {
    "locutor": 0,
    "paciente": 0,
    "silencio": 0
}

# Etiquetas externas
estado_label = None
marca_inicio_label = None
marca_fin_label = None
categoria_label = None

def get_audio_devices():
    p = pyaudio.PyAudio()
    devices = [(i, p.get_device_info_by_index(i)["name"]) for i in range(p.get_device_count())]
    p.terminate()
    return devices

def crear_nueva_carpeta():
    global folder_path, folder_number, file_number, conteo_etiquetas, ultima_marca_visual
    folder_number = 1
    while os.path.exists(f"{BASE_PATH}/paciente{folder_number}"):
        folder_number += 1
    folder_path = f"{BASE_PATH}/paciente{folder_number}/"
    os.makedirs(folder_path)
    file_number = 1
    conteo_etiquetas.update({k: 0 for k in conteo_etiquetas})
    ultima_marca_visual = None
    if marca_inicio_label: marca_inicio_label.configure(text="🟢 Inicio: ---")
    if marca_fin_label: marca_fin_label.configure(text="🔴 Fin: ---")
    if categoria_label: categoria_label.configure(text="🔳 Categoría: ---")

def start_recording():
    global is_recording, frames, marks, start_time, audio_stream
    if audio_device_index is None:
        if estado_label: estado_label.configure(text="Selecciona un dispositivo primero")
        return
    if estado_label: estado_label.configure(text="Grabando...")
    is_recording = True
    frames = []
    marks = []
    start_time = time.time()

    audio = pyaudio.PyAudio()
    audio_stream = audio.open(format=FORMAT, channels=CHANNELS,
                              rate=RATE, input=True, input_device_index=audio_device_index,
                              frames_per_buffer=CHUNK)
    threading.Thread(target=record).start()

def record():
    global frames, is_recording, audio_stream
    while is_recording:
        data = audio_stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

def stop_recording():
    global is_recording, file_number, audio_stream
    is_recording = False
    if estado_label: estado_label.configure(text="Grabación detenida")
    audio_stream.stop_stream()
    audio_stream.close()

    output_filename = f"{folder_path}paciente{folder_number}_{file_number}.wav"
    marks_filename = f"{folder_path}paciente{folder_number}_{file_number}.txt"

    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    with open(marks_filename, 'w') as mf:
        mf.writelines(marks)

    if estado_label: estado_label.configure(text=f"Guardado {output_filename}")
    file_number += 1

def marcar(numero):
    global ultima_marca_visual
    if not is_recording:
        return

    timestamp = time.time() - start_time
    etiquetas = {1: "locutor", 2: "paciente", 3: "silencio"}
    if numero in etiquetas:
        nombre = etiquetas[numero]
        conteo_etiquetas[nombre] += 1
        etiqueta_completa = f"{nombre}_{conteo_etiquetas[nombre]}"

        if ultima_marca_visual:
            marks.append(f"{timestamp:.6f}   {ultima_marca_visual}_FIN\n")
            if marca_fin_label: marca_fin_label.configure(text=f"🔴 Fin: {ultima_marca_visual}")

        marks.append(f"{timestamp:.6f}   {etiqueta_completa}_INICIO\n")
        if marca_inicio_label: marca_inicio_label.configure(text=f"🟢 Inicio: {etiqueta_completa}")

        ultima_marca_visual = etiqueta_completa
        if estado_label: estado_label.configure(text=f"Inició {etiqueta_completa}")

def seleccionar_dispositivo(option):
    global audio_device_index
    index = int(option.split(":")[0])
    audio_device_index = index
    if estado_label: estado_label.configure(text=f"Dispositivo seleccionado: {option}")

def cambiar_categoria(categoria, post_callback=None):
    global is_recording

    if is_recording:
        stop_recording()

    if estado_label:
        estado_label.configure(text=f"✅ Grabación guardada.")

    start_recording()
    time.sleep(0.5)

    timestamp = time.time() - start_time
    linea = f"\n####\n{timestamp:.6f}   {categoria}\n####\n"
    marks.append(linea)

    if categoria_label:
        categoria_label.configure(text=f"🔳 Categoría: {categoria}")

    if post_callback:
        post_callback(categoria)

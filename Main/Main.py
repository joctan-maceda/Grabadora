import customtkinter as ctk
import pygame
import Voz as fg
from PIL import ImageTk, Image
from Presentacion import Presentador

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("1000x750")
app.title("Sistema DCL - Grabadora + Presentación")

# --- Estructura general ---
frame_principal = ctk.CTkFrame(app)
frame_principal.pack(fill="both", expand=True, padx=20, pady=20)

# Columnas
col_izquierda = ctk.CTkFrame(frame_principal, width=450)
col_derecha = ctk.CTkFrame(frame_principal, width=500)
col_izquierda.pack(side="left", fill="both", expand=True, padx=(0, 10))
col_derecha.pack(side="right", fill="both", expand=True, padx=(10, 0))

# ==================== IZQUIERDA: Presentación ====================
pygame.init()
displays = pygame.display.get_desktop_sizes()
pantalla_opciones = [f"{i}: {w}x{h}" for i, (w, h) in enumerate(displays)]
pantalla_seleccionada = ctk.IntVar(value=0)
presentador = None

def iniciar_presentacion():
    global presentador
    seleccion = pantalla_seleccionada.get()
    presentador = Presentador(ruta_presentacion=r"C:\\Users\\DCL\\Desktop\\Zai\\Presentacion", pantalla_idx=seleccion)
    presentador.miniatura_callback = actualizar_preview  # ✅ Aquí sí funciona
    siguiente_presentacion()

    
def mostrar_anterior():
    if presentador:
        presentador.mostrar_anterior()
        presentador.manejar_eventos_redimension()
def siguiente_presentacion():
    if presentador:
        running = presentador.mostrar_siguiente()
        presentador.manejar_eventos_redimension()
        if not running:
            info_label.configure(text="Fin de la presentación.")

def salir_presentacion():
    pygame.quit()

ctk.CTkLabel(col_izquierda, text="Presentación", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
ctk.CTkOptionMenu(col_izquierda, values=pantalla_opciones,
                  command=lambda val: pantalla_seleccionada.set(int(val.split(":")[0]))).pack(pady=10)

ctk.CTkButton(col_izquierda, text="Iniciar Presentación", command=iniciar_presentacion, fg_color="green").pack(pady=10)
ctk.CTkButton(col_izquierda, text="Siguiente", command=siguiente_presentacion, fg_color="blue").pack(pady=10)
ctk.CTkButton(col_izquierda, text="Anterior", command=mostrar_anterior, fg_color="blue").pack(pady=5)
ctk.CTkButton(col_izquierda, text="Salir Presentación", command=salir_presentacion, fg_color="red").pack(pady=10)

info_label = ctk.CTkLabel(col_izquierda, text="Selecciona pantalla e inicia.", wraplength=400)
info_label.pack(pady=10)

# ⬇️ BLOQUE NUEVO: Miniatura visual
frame_preview = ctk.CTkFrame(col_izquierda)
frame_preview.pack(pady=10)

ctk.CTkLabel(frame_preview, text="Miniatura Actual", font=ctk.CTkFont(size=14)).pack(pady=(5, 0))
preview_label = ctk.CTkLabel(frame_preview, text="")
preview_label.pack(pady=5)

imagen_preview = None  # Mantener referencia para que no se borre por el garbage collector

def actualizar_preview(imgtk):
    global imagen_preview
    imagen_preview = imgtk
    preview_label.configure(image=imagen_preview)


# ==================== DERECHA: Grabadora ====================
fg.estado_label = ctk.CTkLabel(col_derecha, text="Esperando acción...", wraplength=450)
fg.marca_inicio_label = ctk.CTkLabel(col_derecha, text="🟢 Inicio: ---", text_color="green", font=ctk.CTkFont(size=14, weight="bold"))
fg.marca_fin_label = ctk.CTkLabel(col_derecha, text="🔴 Fin: ---", text_color="red", font=ctk.CTkFont(size=14, weight="bold"))
fg.categoria_label = ctk.CTkLabel(col_derecha, text="🔳 Categoría: ---", font=ctk.CTkFont(size=14, weight="bold"))

ctk.CTkLabel(col_derecha, text="Grabadora", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

dispositivos = [f"{i}: {name}" for i, name in fg.get_audio_devices()]
ctk.CTkOptionMenu(col_derecha, values=dispositivos, command=fg.seleccionar_dispositivo).pack(pady=10)

ctk.CTkButton(col_derecha, text="Iniciar Grabación", command=fg.start_recording, fg_color="green").pack(pady=10)
ctk.CTkButton(col_derecha, text="Detener Grabación", command=fg.stop_recording, fg_color="red").pack(pady=10)
ctk.CTkButton(col_derecha, text="Nueva Carpeta de Paciente", command=fg.crear_nueva_carpeta, fg_color="black").pack(pady=10)

def actualizar_estado_categoria(categoria):
    info_label.configure(text=f"🎙️ Grabando: {categoria}")

ctk.CTkOptionMenu(col_derecha, values=[
    "MoCA-Mental", "Recopilación de audio", "Descripción de imagen",
    "Descripción de cortometraje", "Lectura de párrafo", "Rimas", "Trabalenguas"
], command=lambda cat: fg.cambiar_categoria(cat, post_callback=actualizar_estado_categoria)).pack(pady=10)


fg.categoria_label.pack(pady=2, in_=col_derecha)

marco_marcas = ctk.CTkFrame(col_derecha)
marco_marcas.pack(pady=10)
for i, texto in {1: "Locutor", 2: "Paciente", 3: "Silencio"}.items():
    ctk.CTkButton(marco_marcas, text=texto, width=80, command=lambda i=i: fg.marcar(i), fg_color="#800080").grid(row=0, column=i, padx=5)

fg.estado_label.pack(pady=10, in_=col_derecha)
fg.marca_inicio_label.pack(pady=2, in_=col_derecha)
fg.marca_fin_label.pack(pady=2, in_=col_derecha)

fg.crear_nueva_carpeta()

app.mainloop()
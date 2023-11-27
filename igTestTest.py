import os
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import tkinter as tk
from tkinter import Entry, Label, Button, messagebox, StringVar
from PIL import Image, ImageTk
from instagrapi import Client
import time

def obtener_enlaces_imagenes(url, omitir_primeras=10):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    enlaces_imagenes = []

    imagenes = soup.find_all('img')
    for i, imagen in enumerate(imagenes):
        if i < omitir_primeras:
            continue
        src = imagen.get('src')
        if src:
            enlaces_imagenes.append(urljoin(url, src))

    return enlaces_imagenes

def descargar_imagen(url, directorio_destino, nombre_archivo, redimensionar=None):
    response = requests.get(url)
    with open(os.path.join(directorio_destino, nombre_archivo), 'wb') as f:
        f.write(response.content)

    if redimensionar:
        imagen = Image.open(os.path.join(directorio_destino, nombre_archivo))
        imagen_redimensionada = imagen.resize(redimensionar, Image.LANCZOS)
        imagen_redimensionada.save(os.path.join(directorio_destino, nombre_archivo), "JPEG")

def descargar_imagenes_random(url, directorio_destino, cantidad=5, redimensionar=None):
    enlaces_imagenes = obtener_enlaces_imagenes(url, omitir_primeras=10)

    if not os.path.exists(directorio_destino):
        os.makedirs(directorio_destino)

    imagenes_seleccionadas = random.sample(enlaces_imagenes, min(cantidad, len(enlaces_imagenes)))
    for i, imagen_url in enumerate(imagenes_seleccionadas):
        nombre_archivo = f'meme_{i + 1}.jpeg'
        descargar_imagen(imagen_url, directorio_destino, nombre_archivo, redimensionar)

def subir_imagenes_instagram(client, directorio_origen, cantidad=2, usuario_instagram="", contraseña_instagram="", nuevo_caption=""):
    imagenes = os.listdir(directorio_origen)
    imagenes_seleccionadas = random.sample(imagenes, min(cantidad, len(imagenes)))
    
    for i, imagen in enumerate(imagenes_seleccionadas):
        ruta_imagen = os.path.join(directorio_origen, imagen)
        
        # Subir imágenes a Instagram con el usuario y contraseña proporcionados
        client.login(usuario_instagram, contraseña_instagram)
        
        # Cambiar el caption si se proporciona
        caption = f"jajajaja q risa xd xd xd xd ({i + 1}/{cantidad})"
        if nuevo_caption:
            caption = nuevo_caption
        
        client.photo_upload(ruta_imagen, caption=caption)

        # Esperar 1 minuto entre subidas
        if i < cantidad - 1:
            print(f"Esperando 1 minuto antes de subir la siguiente imagen...")
            time.sleep(60)

    # Eliminar todas las imágenes en el directorio después de subirlas
    for imagen in imagenes:
        ruta_imagen = os.path.join(directorio_origen, imagen)
        os.remove(ruta_imagen)

def descargar_subir_eliminar_imagenes():
    url_pagina_web = entry_url.get()
    directorio_destino = "memes"
    cantidad_a_descargar = 5

    usuario_instagram = entry_usuario.get()
    contraseña_instagram = entry_contraseña.get()
    nuevo_caption = entry_caption.get()

    try:
        descargar_imagenes_random(url_pagina_web, directorio_destino, cantidad_a_descargar, redimensionar=(200, 200))
        messagebox.showinfo("Descarga completada", f"Se descargaron {cantidad_a_descargar} imágenes en el directorio 'memes'")
        
        # Crea una instancia del cliente de Instagram
        client = Client()
        print("Iniciando sesión en Instagram...")
        
        # Subir imágenes a Instagram y luego eliminarlas
        subir_imagenes_instagram(client, directorio_destino, cantidad=2, usuario_instagram=usuario_instagram, contraseña_instagram=contraseña_instagram, nuevo_caption=nuevo_caption)

        messagebox.showinfo("Subida completada", "Se subieron y eliminaron las imágenes correctamente")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

ventana = tk.Tk()
ventana.title("Descargar y Subir Imágenes")
ventana.geometry("400x400")

Label(ventana, text="URL de la Página:").pack(pady=10)
entry_url = Entry(ventana, width=40)
entry_url.pack(pady=10)

Label(ventana, text="Usuario de Instagram:").pack(pady=10)
entry_usuario = Entry(ventana, width=40)
entry_usuario.pack(pady=10)

Label(ventana, text="Contraseña de Instagram:").pack(pady=10)
entry_contraseña = Entry(ventana, width=40, show="*")  # Muestra asteriscos en lugar de la contraseña
entry_contraseña.pack(pady=10)

Label(ventana, text="Nuevo Caption:").pack(pady=10)
entry_caption = Entry(ventana, width=40)
entry_caption.pack(pady=10)

Button(ventana, text="Descargar y Subir Imágenes", command=descargar_subir_eliminar_imagenes).pack(pady=10)

ventana.mainloop()

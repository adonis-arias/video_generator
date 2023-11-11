import json
import os
import requests

# Ruta al archivo JSON
ruta_archivo = 'scrap_videos/pixabay.json'

# Cargar el contenido del archivo JSON
with open(ruta_archivo, 'r') as archivo:
    json_data = json.load(archivo)

json_data = json_data['page']['results']
folder_path = 'videos/'

# Descargar cada video en los enlaces proporcionados
for item in json_data:
    print(item)
    video_url = item['sources']['mp4']
    video_id = item['id']
    video_file_path = os.path.join(folder_path, f"video_{video_id}.mp4")

    # Descargar el video y guardar localmente
    response = requests.get(video_url)
    if response.status_code == 200:
        with open(video_file_path, 'wb') as f:
            f.write(response.content)
        print(f"Video {video_id} descargado en {video_file_path}")
    else:
        print(f"No se pudo descargar el video {video_id}")


#######



# Ruta al archivo JSON
ruta_archivo = 'scrap_videos/pixabay.json'

# Cargar el contenido del archivo JSON
with open(ruta_archivo, 'r') as archivo:
    json_data = json.load(archivo)

json_data = json_data['page']['results']
folder_path = 'videos/'

# Descargar cada video en los enlaces proporcionados
for item in json_data:
    print(item)
    video_url = item['sources']['mp4']
    video_id = item['id']
    video_file_path = os.path.join(folder_path, f"video_{video_id}.mp4")

    # Descargar el video y guardar localmente
    response = requests.get(video_url)
    if response.status_code == 200:
        with open(video_file_path, 'wb') as f:
            f.write(response.content)
        print(f"Video {video_id} descargado en {video_file_path}")
    else:
        print(f"No se pudo descargar el video {video_id}")




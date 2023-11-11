import requests
import os

# Tu JSON con los enlaces de los videos
json_data = [
    {
        "id": 185096,
        "sources": {
            "mp4": "https://cdn.pixabay.com/vimeo/874643413/libro-185096.mp4?width=640&hash=a20c2cdaf4424c956001ae6d4280eeb296963bcd"
        }
        # Otros campos...
    },
    # Otros elementos del JSON...
]

# Carpeta para almacenar los videos
folder_path = 'videos/'

# Crear la carpeta si no existe
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Descargar cada video en los enlaces proporcionados
for item in json_data:
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

# Puedes modificar la estructura de tu JSON y los nombres de archivo según tus necesidades

from moviepy.editor import concatenate_videoclips, TextClip, CompositeVideoClip, AudioFileClip, VideoFileClip, vfx
from moviepy.video.fx.resize import  resize
from gtts import gTTS
from realesrgan import RealESRGANer
import torch
import cv2
from basicsr.archs import rrdbnet_arch as arch
import numpy as np
import os
from datetime import datetime
from moviepy.video.io.ffmpeg_writer import FFMPEG_VideoWriter
from concurrent.futures import ProcessPoolExecutor


# Inicializar el modelo Real-ESRGAN
def init_realesrgan(model_path):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # Cargar el modelo RRDBNet
    model = arch.RRDBNet(
        num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4
    )
    upsampler = RealESRGANer(
        scale=4,
        model_path=model_path,
        model=model,
        tile=0,
        tile_pad=10,
        pre_pad=0,
        half=False  # Utilizar True si se dispone de un dispositivo con poca memoria
    )
    return upsampler

# Función de super-resolución utilizando RealESRGAN
def super_resolve_video(video_file, output_file):
    upsampler = init_realesrgan('RealESRGAN_x4plus.pth')
    # Carga el modelo preentrenado de RealESRGAN
    
    # Procesa cada cuadro del video
    clip = VideoFileClip(video_file)

    # Mejorar la resolución de cada cuadro
    enhanced_frames = []
    for frame in clip.iter_frames():
        if frame is None or frame.size == 0:
            print("Encountered an empty or None frame.")
            continue
        np_frame = np.array(frame) 
        # Make sure the frame is a NumPy array before converting colors.
        assert isinstance(np_frame, np.ndarray), "The frame is not a NumPy array."
        img = cv2.cvtColor(np_frame, cv2.COLOR_RGB2BGR)
        _, output = upsampler.enhance(img, outscale=4)
        np_output = np.array(_)
        enhanced_frame = cv2.cvtColor(np_output, cv2.COLOR_BGR2RGB)
        enhanced_frames.append(enhanced_frame)

    # Define el escritor del video, utilizando los parámetros del clip original
    writer = FFMPEG_VideoWriter(output_file, clip.size, clip.fps, codec="libx264", audio_codec='aac', bitrate="800k", audio_bitrate="128k", preset="ultrafast", threads=4)

    for frame in enhanced_frames:
            writer.write_frame(np.array(frame))
    writer.close()

    # Reemplaza el audio con el original
    os.system(f"ffmpeg -i {output_file} -i {video_file} -c copy -map 0:v:0 -map 1:a:0 -shortest {output_file}")

    return VideoFileClip(output_file)


def combine_videos_with_subtitles(video_files, subtitles, output_file):
    """
    Combina videos con subtítulos y genera voz para esos subtítulos.
    
    :param video_files: Lista de archivos de video para combinar.
    :param subtitles: Lista de subtítulos para cada video.
    :param output_file: Nombre del archivo de video de salida.
    """
    combined_clips = []
    
    for video_file, subtitle in zip(video_files, subtitles):
        # Mejora la resolución del video
        enhanced_video_file = f"enhanced_{video_file}"
        super_resolve_video(video_file, enhanced_video_file)

        # Carga el video y toma solo los primeros 5 segundos
        clip = VideoFileClip(enhanced_video_file).subclip(0,5)

        # Redimensionar el clip a una resolución de 1280x720
        clip = clip.resize(height=1080, width=1920)
        
        # Genera la voz para el subtítulo
        tts = gTTS(text=subtitle, lang='es')
        audio_file = "out/temp_audio.mp3"
        tts.save(audio_file)
        
        # Agrega la voz al video
        clip = clip.set_audio(AudioFileClip(audio_file))
        
        # Genera el subtítulo visual
        txt_clip = (TextClip(subtitle, fontsize=24, color='white')
                   .set_pos(('center', 'bottom'))
                   .set_duration(clip.duration))
        
        # Combina el video con el subtítulo visual
        video_with_subtitle = CompositeVideoClip([clip, txt_clip])
        combined_clips.append(video_with_subtitle)
        
        # Elimina el archivo de audio temporal
        os.remove(audio_file)
    
    # Combina todos los videos con subtítulos
    final_clip = concatenate_videoclips(combined_clips, method="compose")
    
    # Ajusta el tamaño del video final para dispositivos móviles
    final_clip = final_clip.resize(height=720, width=1280)

    # Exporta el video final con calidad y formato optimizado para dispositivos móviles
    final_clip.write_videofile(output_file, codec="libx264", 
                               audio_codec='aac', 
                               bitrate="800k",
                               audio_bitrate="128k", 
                               preset="ultrafast", 
                               threads=4,
                               fps=24) 

# Ejemplo de uso:
video_files = ["videos/video_1700.mp4", "videos/video_180386.mp4", "videos/video_172451.mp4", "videos/video_168787.mp4"]
subtitles = ["Este es el subtítulo para video1", "Subtítulo para video2", "Subtítulo para video3", "Subtítulo para video4"]
ukey = datetime.now().strftime('%d%m-%H%M%S')
output_file = f"out/video_{ukey}.mp4"
combine_videos_with_subtitles(video_files, subtitles, output_file)

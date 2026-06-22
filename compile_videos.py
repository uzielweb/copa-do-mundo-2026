import os
import json
import subprocess
from PIL import Image, ImageDraw, ImageFont
import update_cup_videos

def get_font(size):
    # Try typical Windows font path
    font_path = "C:/Windows/Fonts/arialbd.ttf"
    if os.path.exists(font_path):
        return ImageFont.truetype(font_path, size)
    # Fallback to default
    return ImageFont.load_default()

def create_title_image(text_lines, out_path, width=1920, height=1080):
    img = Image.new('RGB', (width, height), color=(15, 20, 30)) # Dark blue-ish background
    draw = ImageDraw.Draw(img)
    
    # Fonts
    font_large = get_font(90)
    font_medium = get_font(70)
    font_small = get_font(50)
    
    y_offset = height // 2 - 150
    
    for i, line in enumerate(text_lines):
        if i == 0:
            font = font_small
            color = (200, 200, 200)
        elif i == 1:
            font = font_large
            color = (255, 255, 255)
        else:
            font = font_medium
            color = (150, 150, 150)
            
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        
        draw.text(((width - w) / 2, y_offset), line, font=font, fill=color)
        y_offset += h + 40
        
    img.save(out_path)

def get_video_params(filepath):
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,width,height,r_frame_rate,time_base,pix_fmt",
        "-of", "json", filepath
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(res.stdout)
    stream = data['streams'][0]
    
    # audio params
    cmd_a = [
        "ffprobe", "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=codec_name,sample_rate,channels",
        "-of", "json", filepath
    ]
    res_a = subprocess.run(cmd_a, capture_output=True, text=True)
    data_a = json.loads(res_a.stdout)
    audio_stream = data_a['streams'][0] if data_a.get('streams') else {'codec_name': 'aac', 'sample_rate': '48000', 'channels': 2}
    
    return {
        'vcodec': stream.get('codec_name', 'libx264'),
        'width': stream.get('width', 1920),
        'height': stream.get('height', 1080),
        'fps': stream.get('r_frame_rate', '60000/1001'),
        'pix_fmt': stream.get('pix_fmt', 'yuv420p'),
        'acodec': audio_stream.get('codec_name', 'aac'),
        'ar': audio_stream.get('sample_rate', '48000'),
        'ac': audio_stream.get('channels', 2)
    }

def main():
    print("Carregando schedule...")
    all_matches = update_cup_videos.parse_schedule()
    match_dict = {m['num']: m for m in all_matches}
    
    with open('videos.json', 'r', encoding='utf-8') as f:
        video_db = json.load(f)
        
    local_videos = []
    # Sort keys to guarantee chronological order (001 to 104)
    for m_num in sorted(video_db.keys()):
        entry = video_db[m_num]
        if 'local' in entry:
            local_videos.append((m_num, entry['local']))
            
    if not local_videos:
        print("Nenhum vídeo local encontrado.")
        return
        
    print(f"Encontrados {len(local_videos)} vídeos locais.")
    
    os.makedirs('Compilado', exist_ok=True)
    os.makedirs('Compilado/temp_cards', exist_ok=True)
    
    # Get parameters from the first video to match perfectly
    ref_video = local_videos[0][1]
    print(f"Lendo parâmetros de referência do vídeo: {ref_video}")
    params = get_video_params(ref_video)
    print(f"Parâmetros: {params}")
    
    # Map ffprobe codec names to ffmpeg encoders
    vcodec_enc = "libx264"
    if params['vcodec'] == 'av1': vcodec_enc = "libaom-av1"
    elif params['vcodec'] == 'vp9': vcodec_enc = "libvpx-vp9"
    
    acodec_enc = "aac"
    if params['acodec'] == 'opus': acodec_enc = "libopus"
    
    concat_lines = []
    
    for i, (m_num, local_path) in enumerate(local_videos):
        match = match_dict.get(m_num)
        if not match: continue
        
        date_str = match['data_hora'].split(' às')[0]
        lines = [
            f"JOGO {m_num} - {date_str}",
            f"{match['team1']} X {match['team2']}",
            f"{match['fase']}"
        ]
        
        print(f"[{i+1}/{len(local_videos)}] Gerando card para: Jogo {m_num}")
        img_path = f"Compilado/temp_cards/card_{m_num}.png"
        vid_path = f"Compilado/temp_cards/card_{m_num}.mp4"
        
        create_title_image(lines, img_path, width=params['width'], height=params['height'])
        
        # Generate 5-second video with exact params
        if not os.path.exists(vid_path):
            cmd = [
                "ffmpeg", "-y", "-loop", "1", "-framerate", params['fps'],
                "-i", img_path, "-f", "lavfi", "-i", f"anullsrc=r={params['ar']}:cl=stereo",
                "-c:v", vcodec_enc, "-t", "5", "-pix_fmt", params['pix_fmt'],
                "-c:a", acodec_enc, "-shortest", vid_path
            ]
            # Speed up AV1 encoding if necessary
            if vcodec_enc == "libaom-av1":
                cmd.extend(["-cpu-used", "8"]) # Fastest AV1 encoding
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        concat_lines.append(f"file '{os.path.abspath(vid_path).replace(chr(92), '/')}'")
        concat_lines.append(f"file '{os.path.abspath(local_path).replace(chr(92), '/')}'")
        
    concat_path = "Compilado/concat.txt"
    with open(concat_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(concat_lines))
        
    out_video = "Compilado/Todos_Os_Jogos.mp4"
    print(f"Concatenando todos os {len(local_videos)} jogos em {out_video}...")
    
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_path,
        "-c", "copy", out_video
    ]
    subprocess.run(cmd_concat)
    
    print("Processo concluído com sucesso!")

if __name__ == "__main__":
    main()

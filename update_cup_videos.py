import os
import re
import urllib.request
import json
import subprocess
import argparse
import sys
from datetime import datetime

# Set console encoding to UTF-8 to prevent Windows UnicodeEncodeErrors
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Portuguese country translations
country_translations = {
    'Mexico': 'México', 'South Africa': 'África do Sul', 'South Korea': 'Coreia do Sul', 'Czech Republic': 'Tchéquia',
    'Canada': 'Canadá', 'Bosnia & Herzegovina': 'Bósnia e Herzegovina', 'Qatar': 'Catar', 'Switzerland': 'Suíça',
    'Brazil': 'Brasil', 'Morocco': 'Marrocos', 'Haiti': 'Haiti', 'Scotland': 'Escócia',
    'USA': 'Estados Unidos', 'Paraguay': 'Paraguai', 'Australia': 'Austrália', 'Turkey': 'Turquia',
    'Germany': 'Alemanha', 'Curaçao': 'Curaçao', 'Ivory Coast': 'Costa do Marfim', 'Ecuador': 'Equador',
    'Netherlands': 'Holanda', 'Japan': 'Japão', 'Sweden': 'Suécia', 'Tunisia': 'Tunísia',
    'Belgium': 'Bélgica', 'Egypt': 'Egito', 'Iran': 'Irã', 'New Zealand': 'Nova Zelândia',
    'Spain': 'Espanha', 'Cape Verde': 'Cabo Verde', 'Saudi Arabia': 'Arábia Saudita', 'Uruguay': 'Uruguai',
    'France': 'França', 'Senegal': 'Senegal', 'Iraq': 'Iraque', 'Norway': 'Noruega',
    'Argentina': 'Argentina', 'Algeria': 'Argélia', 'Austria': 'Áustria', 'Jordan': 'Jordânia',
    'Portugal': 'Portugal', 'DR Congo': 'RD Congo', 'Uzbekistan': 'Uzbequistão', 'Colombia': 'Colômbia',
    'England': 'Inglaterra', 'Croatia': 'Croácia', 'Ghana': 'Gana', 'Panama': 'Panamá'
}

days_map = {'Sun': 'Dom', 'Mon': 'Seg', 'Tue': 'Ter', 'Wed': 'Qua', 'Thu': 'Qui', 'Fri': 'Sex', 'Sat': 'Sáb'}
months_map = {'June': 'Junho', 'Jun': 'Junho', 'July': 'Julho', 'Jul': 'Julho'}

def translate_date(date_str):
    if not date_str:
        return ""
    parts = date_str.split()
    if len(parts) == 3:
        day_w, month, day_n = parts[0], parts[1], parts[2]
        day_w_pt = days_map.get(day_w, day_w)
        month_pt = months_map.get(month, month)
        return f"{day_w_pt}, {day_n} de {month_pt}"
    return date_str

def get_day_folder(date_hora_pt):
    # Extracts e.g., "11 de Junho" from "Qui, 11 de Junho às 13:00 (UTC-6)"
    m = re.search(r'\d+ de [A-Za-z]+', date_hora_pt)
    if m:
        return m.group(0)
    return None

def normalize(text):
    if not text:
        return ""
    text = text.lower()
    # Replace common accents
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'â': 'a', 'ê': 'e', 'ô': 'o',
        'ã': 'a', 'õ': 'o',
        'ç': 'c',
        'í': 'i',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def parse_schedule():
    print("Buscando dados oficiais do openfootball no GitHub...")
    # Fetch cup.txt
    req = urllib.request.Request(
        'https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup.txt',
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req) as response:
        text_cup = response.read().decode('utf-8')

    # Fetch cup_finals.txt
    req_finals = urllib.request.Request(
        'https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup_finals.txt',
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req_finals) as response:
        text_finals = response.read().decode('utf-8')

    list_matches = []
    match_num = 1

    # Parse Group Stage
    group_blocks = text_cup.split('▪ Group ')
    for block in group_blocks[1:]:
        lines = block.split('\n')
        group_letter = lines[0].strip()
        fase = f"Grupo {group_letter}"
        
        current_date = ''
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            
            # Check date
            if re.match(r'^(Sun|Mon|Tue|Wed|Thu|Fri|Sat)\s+[A-Za-z]+\s+\d+$', line):
                current_date = translate_date(line)
                continue
            
            m = re.match(r'^(\d{2}:\d{2})\s+(UTC[-+]\d+)\s+(.*?)\s+(\d+-\d+(?:\s+a\.e\.t\.)?(?:\s+\([\d\s,-]+\))?(?:,\s+\d+-\d+\s+pen\.)?|v)\s+(.*?)\s+@\s+(.*?)$', line)
            if m:
                time, utc, team1, score, team2, local = m.groups()
                team1 = team1.strip()
                team2 = team2.strip()
                score = score.strip() if score else ''
                
                list_matches.append({
                    'num': f"{match_num:03d}",
                    'fase': fase,
                    'data_hora': f"{current_date} às {time} ({utc})",
                    'team1': country_translations.get(team1, team1),
                    'team2': country_translations.get(team2, team2),
                    'score': score,
                    'is_vs': score == '',
                    'local': local.strip()
                })
                match_num += 1

    # Parse Knockout Stage
    stages = text_finals.split('▪ ')
    for block in stages[1:]:
        lines = block.split('\n')
        stage_name = lines[0].strip()
        
        if "Round of 32" in stage_name: stage_name = "16-avos de Final"
        elif "Round of 16" in stage_name: stage_name = "Oitavas de Final"
        elif "Quarter-final" in stage_name: stage_name = "Quartas de Final"
        elif "Semi-final" in stage_name: stage_name = "Semifinal"
        elif "Match for third place" in stage_name: stage_name = "Disputa do 3º Lugar"
        elif "Final" in stage_name: stage_name = "Final"
        
        current_date = ''
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            
            if re.match(r'^(Sun|Mon|Tue|Wed|Thu|Fri|Sat)\s+[A-Za-z]+\s+\d+$', line):
                norm_line = line.replace('Jun', 'June').replace('Jul', 'July')
                current_date = translate_date(norm_line)
                continue
            
            m = re.match(r'^\((\d+)\)\s+(\d{2}:\d{2})\s+(UTC[-+]\d+)\s+(.*?)\s+(\d+-\d+(?:\s+a\.e\.t\.)?(?:\s+\([\d\s,-]+\))?(?:,\s+\d+-\d+\s+pen\.)?|v)\s+(.*?)\s+@\s+(.*?)$', line)
            if m:
                num, time, utc, team1, score, team2, local = m.groups()
                team1 = team1.strip()
                team2 = team2.strip()
                score = score.strip() if score else ''
                
                list_matches.append({
                    'num': f"{int(num):03d}",
                    'fase': stage_name,
                    'data_hora': f"{current_date} às {time} ({utc})",
                    'team1': country_translations.get(team1, team1),
                    'team2': country_translations.get(team2, team2),
                    'score': score,
                    'is_vs': score == '',
                    'local': local.strip()
                })

    return sorted(list_matches, key=lambda x: int(x['num']))

def scan_local_videos():
    # Scan all directories like "11 de Junho", etc.
    downloaded_matches = {}
    
    # We walk current directory
    for root, dirs, files in os.walk('.'):
        # Only interested in dirs containing "Junho" or "Julho"
        folder_name = os.path.basename(root)
        if "de Junho" in folder_name or "de Julho" in folder_name:
            for file in files:
                if file.lower().endswith(('.mp4', '.webm', '.mkv', '.avi')):
                    # Store file paths keyed by a normalized string of teams found in title
                    downloaded_matches[os.path.join(folder_name, file)] = file
                    
    return downloaded_matches

def get_team_variants(team_name):
    if not team_name:
        return set()
    variants = {normalize(team_name)}
    # Add translation variants (English <-> Portuguese)
    for eng, pt in country_translations.items():
        if normalize(eng) == normalize(team_name):
            variants.add(normalize(pt))
        elif normalize(pt) == normalize(team_name):
            variants.add(normalize(eng))
            
    # Normalize common abbreviations and aliases
    expanded = set()
    for v in variants:
        expanded.add(v)
        if v == "usa" or v == "united states" or "estados unidos" in v:
            expanded.update({"usa", "united states", "estados unidos"})
        if "dr congo" in v or "rd congo" in v:
            expanded.update({"dr congo", "rd congo", "congo"})
        if "bosnia" in v:
            expanded.update({"bosnia & herzegovina", "bosnia and herzegovina", "bosnia e herzegovina", "bosnia"})
        if "czech" in v or "tchequia" in v:
            expanded.update({"czech republic", "czechia", "tchequia", "republica tcheca"})
        if "ivory coast" in v or "costa do marfim" in v:
            expanded.update({"ivory coast", "costa do marfim"})
        if "south africa" in v or "africa do sul" in v:
            expanded.update({"south africa", "africa do sul"})
        if "south korea" in v or "coreia do sul" in v:
            expanded.update({"south korea", "coreia do sul"})
        if "cape verde" in v or "cabo verde" in v:
            expanded.update({"cape verde", "cabo verde"})
        if "saudi arabia" in v or "arabia saudita" in v:
            expanded.update({"saudi arabia", "arabia saudita"})
        if "new zealand" in v or "nova zelandia" in v:
            expanded.update({"new zealand", "nova zelandia"})
            
    return expanded

def check_match_locally(match, local_files):
    t1_variants = get_team_variants(match['team1'])
    t2_variants = get_team_variants(match['team2'])
    
    for path, filename in local_files.items():
        fn_norm = normalize(filename)
        match_t1 = any(v in fn_norm for v in t1_variants)
        match_t2 = any(v in fn_norm for v in t2_variants)
        
        if match_t1 and match_t2:
            return path
    return None

def fetch_cazetv_playlist(playlist_id):
    playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    print(f"Obtendo vídeos da playlist ({playlist_url})...")
    
    try:
        # Run yt-dlp to get flat playlist in JSON format
        cmd = [
            "yt-dlp",
            "--flat-playlist",
            "--dump-single-json",
            playlist_url
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError:
            print(f"Fallback: Tentando extrair playlist com cookies do Firefox e Node.js...")
            cmd_fallback = cmd + ["--cookies-from-browser", "firefox", "--js-runtimes", "node"]
            result = subprocess.run(cmd_fallback, capture_output=True, text=True, check=True)
        playlist_data = json.loads(result.stdout)
        
        videos = []
        for entry in playlist_data.get('entries', []):
            if entry:
                videos.append({
                    'title': entry.get('title', ''),
                    'url': entry.get('url', f"https://www.youtube.com/watch?v={entry.get('id')}")
                })
        return videos
    except Exception as e:
        print(f"Erro ao buscar playlist {playlist_id} com yt-dlp: {e}")
        return []

def match_phase(match, title_norm):
    fase = match['fase']
    if fase.startswith("Grupo"):
        knockout_keywords = ["oitavas", "quartas", "semifinal", "semi-final", "final", "16-avos", "16 avos", "round of", "3º lugar", "terceiro lugar"]
        return not any(kw in title_norm for kw in knockout_keywords)
        
    if fase == "16-avos de Final":
        return any(x in title_norm for x in ["16-avos", "16 avos", "32", "round of 32"])
    if fase == "Oitavas de Final":
        return any(x in title_norm for x in ["oitavas", "16", "round of 16"])
    if fase == "Quartas de Final":
        return any(x in title_norm for x in ["quartas", "quarter"])
    if fase == "Semifinal":
        return any(x in title_norm for x in ["semifinal", "semi-final", "semi"])
    if fase == "Disputa do 3º Lugar":
        return any(x in title_norm for x in ["3º lugar", "terceiro", "3rd place", "bronze"])
    if fase == "Final":
        is_other_final = any(kw in title_norm for kw in ["oitavas", "quartas", "semi"])
        return "final" in title_norm and not is_other_final
        
    return True

def match_playlist_video(match, playlist_videos, all_matches, check_keywords=True):
    t1_variants = get_team_variants(match['team1'])
    t2_variants = get_team_variants(match['team2'])
    
    # Check if matchup happens multiple times in the cup
    has_duplicates = len([x for x in all_matches if (x['team1'] == match['team1'] and x['team2'] == match['team2']) or (x['team1'] == match['team2'] and x['team2'] == match['team1'])]) > 1
    
    for video in playlist_videos:
        if not video.get('title'):
            continue
        title_norm = normalize(video['title'])
        
        match_t1 = any(v in title_norm for v in t1_variants)
        match_t2 = any(v in title_norm for v in t2_variants)
        
        if match_t1 and match_t2:
            if has_duplicates and not match_phase(match, title_norm):
                continue
                
            if not check_keywords:
                return video
                
            is_game_video = any(x in title_norm for x in ["melhores momentos", "jogo completo", "gols", "x", "vs", "highlights", "integra", "full match", "transmissao", "ao vivo"])
            if is_game_video:
                return video
                
    return None

def search_youtube_fallback(match, is_full_game):
    t1_pt = country_translations.get(match['team1'], match['team1'])
    t2_pt = country_translations.get(match['team2'], match['team2'])
    
    prefix = "JOGO COMPLETO" if is_full_game else "MELHORES MOMENTOS"
    query = f"{prefix} {t1_pt} x {t2_pt} COPA DO MUNDO 2026 CazéTV"
    
    print(f"Buscando fallback no YouTube: '{query}'...")
    try:
        cmd = ["yt-dlp", f"ytsearch3:{query}", "--dump-json", "--default-search", "ytsearch", "--flat-playlist"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        for line in result.stdout.strip().split('\n'):
            if not line: continue
            try:
                data = json.loads(line)
                title = data.get('title', '')
                title_norm = normalize(title)
                
                # Check teams
                t1_variants = get_team_variants(match['team1'])
                t2_variants = get_team_variants(match['team2'])
                if any(v in title_norm for v in t1_variants) and any(v in title_norm for v in t2_variants):
                    if is_full_game:
                        if any(x in title_norm for x in ["jogo completo", "integra", "full match"]):
                            return {'title': title, 'url': f"https://www.youtube.com/watch?v={data.get('id')}"}
                    else:
                        if any(x in title_norm for x in ["melhores", "momentos", "gols", "highlights"]):
                            return {'title': title, 'url': f"https://www.youtube.com/watch?v={data.get('id')}"}
            except:
                continue
    except Exception as e:
        print(f"Erro no fallback de busca: {e}")
        
    return None

def update_and_save_db(all_matches, local_files, highlights_videos, full_game_videos, json_path, verbose=False):
    # Load existing videos.json
    video_db = {}
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                video_db = json.load(f)
        except Exception as e:
            print(f"Erro ao ler videos.json existente: {e}")

    missing_downloads = []
    if verbose:
        print("\n--- STATUS DOS JOGOS ---")
        
    for match in all_matches:
        if any(x in match['team1'] for x in ["W", "L", "1", "2", "3"]) or any(x in match['team2'] for x in ["W", "L", "1", "2", "3"]):
            continue
            
        local_path = check_match_locally(match, local_files)
        playlist_video = match_playlist_video(match, highlights_videos, all_matches, check_keywords=True)
        full_game_video = match_playlist_video(match, full_game_videos, all_matches, check_keywords=False)
        
        # Fallback for past matches if not found in playlist
        if match['is_vs'] == False: # if match has finished
            if not playlist_video:
                playlist_video = search_youtube_fallback(match, is_full_game=False)
            if not full_game_video:
                full_game_video = search_youtube_fallback(match, is_full_game=True)
        
        
        # Start with existing entry if it exists, otherwise new dict
        match_entry = video_db.get(match['num'], {})
        
        # Determine local path
        if local_path:
            match_entry['local'] = local_path.replace('\\', '/')
            
        # Determine youtube url (highlights)
        if playlist_video:
            match_entry['youtube'] = playlist_video['url']
            
        # Determine youtube_full url (full game)
        if full_game_video:
            match_entry['youtube_full'] = full_game_video['url']
            
        # Determine status and download status
        status_str = ""
        if 'local' in match_entry:
            status_str = f"[OK] Já baixado localmente ({match_entry['local']})"
        elif 'youtube' in match_entry or 'youtube_full' in match_entry:
            title_str = (playlist_video['title'] if playlist_video else None) or (full_game_video['title'] if full_game_video else None) or f"MELHORES MOMENTOS: {match['team1']} X {match['team2']}"
            status_str = f"[DISPONÍVEL] Disponível no YouTube: {title_str}"
            if 'youtube' in match_entry:
                day_folder = get_day_folder(match['data_hora'])
                if day_folder:
                    missing_downloads.append({
                        'match': match,
                        'folder': day_folder,
                        'video': {
                            'url': match_entry['youtube'],
                            'title': title_str
                        }
                    })
        else:
            status_str = "[NÃO DISPONÍVEL] Vídeo ainda não encontrado na playlist"
            
        if match_entry:
            video_db[match['num']] = match_entry
            
        if verbose:
            print(f"Jogo {match['num']} | {match['team1']} x {match['team2']} ({match['fase']}) -> {status_str}")
            
    # Save to videos.json
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(video_db, f, indent=2, ensure_ascii=False)
        if verbose:
            print("Banco de dados de vídeos atualizado em: videos.json")
    except Exception as e:
        print(f"Erro ao salvar videos.json: {e}")
        
    return missing_downloads

def main():
    parser = argparse.ArgumentParser(description="Verificador de vídeos da Copa 2026 contra Playlist da CazéTV.")
    parser.add_argument('--download', action='store_true', help="Baixar automaticamente os vídeos novos encontrados.")
    args = parser.parse_args()

    # 1. Parse schedules
    all_matches = parse_schedule()
    
    # 2. Scan local files
    local_files = scan_local_videos()
    
    # 3. Fetch playlists
    highlights_videos = fetch_cazetv_playlist("PLsFWLnYCEXEVNzCnkQE-xOuMc8oLxSleC")
    full_game_videos = fetch_cazetv_playlist("PLsFWLnYCEXEVWs5wf60vfwUU4FaOEre3D")
    
    # Define json path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'videos.json')
    
    # Update and save DB first time
    missing_downloads = update_and_save_db(all_matches, local_files, highlights_videos, full_game_videos, json_path, verbose=True)
    
    print(f"\nTotal de vídeos ausentes localmente, mas disponíveis na playlist: {len(missing_downloads)}")
    
    if missing_downloads:
        print("\n--- COMANDOS PARA DOWNLOAD ---")
        for item in missing_downloads:
            # Generate the exact yt-dlp command
            folder = item['folder']
            url = item['video']['url']
            cmd = f'yt-dlp -i -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" --merge-output-format mp4 --remux-video mp4 -o "{folder}/%(title)s.%(ext)s" "{url}"\n            # Se falhar adicione: --cookies-from-browser firefox --js-runtimes node'
            print(cmd)
            
        if args.download:
            print("\nIniciando o download dos vídeos ausentes...")
            for item in missing_downloads:
                folder = item['folder']
                url = item['video']['url']
                title = item['video']['title']
                print(f"\nBaixando: {title} para a pasta {folder}...")
                
                # Make sure folder exists (should exist)
                os.makedirs(folder, exist_ok=True)
                
                cmd = [
                    "yt-dlp", "-i",
                    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                    "--merge-output-format", "mp4",
                    "--remux-video", "mp4",
                    "-o", f"{folder}/%(title)s.%(ext)s",
                    url
                ]
                result = subprocess.run(cmd)
                
                if result.returncode != 0:
                    print(f"\nFalha no download (possível bloqueio de bot). Tentando modo fallback com Firefox e Node.js...")
                    cmd_fallback = cmd + ["--cookies-from-browser", "firefox", "--js-runtimes", "node"]
                    subprocess.run(cmd_fallback)
            print("\nDownloads concluídos!")
            
            # Re-scan and update videos.json with new downloads
            print("Atualizando videos.json com os novos vídeos baixados...")
            local_files = scan_local_videos()
            update_and_save_db(all_matches, local_files, highlights_videos, full_game_videos, json_path, verbose=False)
            print("Banco de dados de vídeos atualizado em: videos.json com os novos downloads.")
    else:
        print("\nNenhum vídeo novo disponível para baixar.")
 
if __name__ == '__main__':
    main()

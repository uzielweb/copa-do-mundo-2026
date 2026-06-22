# Copa do Mundo FIFA 2026 - Tabela Interativa & Vídeos 🏆
### FIFA World Cup 2026 - Interactive Schedule & Highlights

[Português](#português) | [English](#english)

---

## Português

<div align="center">

[![Tabela Interativa](https://img.shields.io/badge/Tabela%20Interativa-Online-green?style=for-the-badge&logo=html5&logoColor=white)](https://uzielweb.github.io/copa-do-mundo-2026/)
[![Código Fonte](https://img.shields.io/badge/Código%20Fonte-GitHub-blue?style=for-the-badge&logo=github)](https://github.com/uzielweb/copa-do-mundo-2026)

</div>


Uma tabela interativa, bonita e responsiva para acompanhar a **Copa do Mundo FIFA 2026** (Canadá, EUA e México). Este projeto permite o acompanhamento em tempo real dos placares e integra vídeos de melhores momentos e transmissões hospedados localmente.

### 🌟 Funcionalidades
* **Placares em Tempo Real:** Carregamento dinâmico via `fetch` dos placares oficiais atualizados no GitHub (comunidade openfootball).
* **Painel de Classificação de Grupos:** Cálculo automático e ordenamento dos grupos (A a L) em tempo real conforme os placares são atualizados.
* **Classificação Geral:** Tabela unificada comparativa com todas as 48 seleções participantes da fase de grupos.
* **Filtros Avançados:** Filtro por jogos com vídeo, busca por seleção/estádio, e filtragem do Mata-Mata por fases específicas (16-avos, Oitavas, Quartas, Semifinal, 3º Lugar e Final).
* **Reprodutor de Vídeo Modal:** Assista aos melhores momentos dos jogos localmente usando um player integrado.
* **Integração com YouTube:** Links diretos para vídeos de Melhores Momentos e transmissão de Jogo Completo no YouTube (CazéTV) carregados a partir do banco de dados local.
* **Hospedagem de Aberturas:** Botões rápidos no cabeçalho para reproduzir vídeos de abertura oficial (México, Canadá, EUA).

### 📁 Estrutura de Pastas de Vídeos (Ignorada no Git)
Para manter o repositório limpo e evitar problemas de direitos autorais, os vídeos não são enviados para o GitHub. Para o player de vídeo funcionar localmente, organize seus arquivos nas pastas estruturadas automaticamente por dias:
```
/
├── index.html
├── update_cup_videos.py
├── Aberturas/
│   ├── CONFIRA TODOS OS SHOWS DE ABERTURA DA COPA DO MUNDO FIFA™ 2026 ｜ MÉXICO, CANADÁ E ESTADOS UNIDOS.mp4
│   ├── CONFIRA A CERIMÔNIA DE ABERTURA DO CANADÁ DIRETO DO TORONTO STADIUM ｜ COPA DO MUNDO FIFA™ 2026.mp4
│   └── CONFIRA A CERIMÔNIA DOS EUA DE ABERTURA DA COPA COM ANITTA E LISA ｜ COPA DO MUNDO FIFA™ 2026.mp4
├── 11 de Junho/
│   └── (vídeos das partidas do dia 11...)
├── 12 de Junho/
│   └── ...
└── 19 de Julho/
```

### 🤖 Script Auxiliar (`update_cup_videos.py`)
Utilize este script em Python para cruzar seus arquivos locais com a playlist do YouTube da **CazéTV** em busca de vídeos novos usando o `yt-dlp`.

* **Listar status e comandos de download:**
  ```bash
  python update_cup_videos.py
  ```
* **Baixar vídeos ausentes automaticamente nas pastas corretas:**
  ```bash
  python update_cup_videos.py --download
  ```

---

## English

<div align="center">

[![Interactive Tracker](https://img.shields.io/badge/Interactive%20Tracker-Online-green?style=for-the-badge&logo=html5&logoColor=white)](https://uzielweb.github.io/copa-do-mundo-2026/)
[![Source Code](https://img.shields.io/badge/Source%20Code-GitHub-blue?style=for-the-badge&logo=github)](https://github.com/uzielweb/copa-do-mundo-2026)

</div>


A beautiful, responsive, and interactive schedule tracker for the **FIFA World Cup 2026** (Canada, USA, and Mexico). This project fetches live scores and integrates local video highlights.

### 🌟 Features
* **Live Match Scores:** Dynamically fetched via `fetch` from the official community database on GitHub (openfootball).
* **Group Standings calculation:** Real-time automatic group calculation and sorting (Groups A to L) as match results update.
* **Overall Standings:** Unified leaderboard comparing all 48 teams in the group stage.
* **Advanced Filters:** Filter matches by availability of video highlights, search by country/stadium, and target specific knockout stages (Round of 32, Round of 16, Quarter-finals, Semi-finals, 3rd Place match, and Final).
* **Modal Video Player:** Integrated local video player to watch game highlights.
* **YouTube Integration:** Direct links to YouTube Highlights and Full Match broadcasts (CazéTV) loaded from the local database.
* **Official Broadcast Intros:** Direct buttons in the header to play official opening ceremonies (Mexico, Canada, USA).

### 📁 Directory Layout for Local Videos (Git Ignored)
To avoid copyright issues, media folders are gitignored. To use the video feature locally, place your files inside the structured daily folders:
```
/
├── index.html
├── update_cup_videos.py
├── Aberturas/
│   ├── CONFIRA TODOS OS SHOWS DE ABERTURA DA COPA DO MUNDO FIFA™ 2026 ｜ MÉXICO, CANADÁ E ESTADOS UNIDOS.mp4
│   ├── CONFIRA A CERIMÔNIA DE ABERTURA DO CANADÁ DIRETO DO TORONTO STADIUM ｜ COPA DO MUNDO FIFA™ 2026.mp4
│   └── CONFIRA A CERIMÔNIA DOS EUA DE ABERTURA DA COPA COM ANITTA E LISA ｜ COPA DO MUNDO FIFA™ 2026.mp4
├── 11 de Junho/
│   └── (videos of matches played on June 11...)
├── 12 de Junho/
│   └── ...
└── 19 de Julho/
```

### 🤖 Helper script (`update_cup_videos.py`)
Run this Python script to check for newly published matches on the **CazéTV** YouTube playlist against your local folders using `yt-dlp`.

* **Audit match status and display raw yt-dlp commands:**
  ```bash
  python update_cup_videos.py
  ```
* **Automatically download missing highlights to their corresponding folder:**
  ```bash
  python update_cup_videos.py --download
  ```

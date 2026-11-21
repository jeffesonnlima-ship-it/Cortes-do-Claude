# Palmeiras x Flamengo — vídeo 3D (pipeline)

Vídeo vertical 9:16 renderizado em 3D (Three.js) a partir da narração.

## Como re-renderizar (ex.: após regravar a narração)
1. Transcreva a nova narração com timestamps por palavra (faster-whisper) → `words.json`.
2. Ajuste `script.txt` com o texto exato narrado.
3. `python3 timeline.py words.json <duração_do_áudio>` — recalcula cortes, eventos e legendas (`caps.ass`).
4. Sirva a pasta-mãe via HTTP (`python3 -m http.server 8765`) com `three@0.160.0` em `node_modules` e as fontes Nunito em `/fonts/...`.
5. `node render.js <frame_ini> <frame_fim> chunks/cN.mp4` (em paralelo, intervalos de `ranges.txt`).
6. `python3 mixsfx.py` (efeitos sonoros) e `./assemble.sh` (upscale 1080×1920, legendas, mixagem).

Os tempos de cada cena e jogada são ancorados em palavras da narração (ver `timeline.py`), então uma nova gravação re-sincroniza tudo automaticamente.

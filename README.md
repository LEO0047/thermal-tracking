# Thermal Tracking

**熱感追蹤實驗台** — turn any video or photo into a thermal-camera look: false color, trails, glow, and live blob tracking.

Live: https://leo0047.github.io/thermal-tracking/

## Use

- Pick a mood from the list under the title, or press **ROLL** for a random look. Switch to **PRO** for the full control panel.
- Press **+ 收藏這組** to keep the current look in the mood list. Saved looks live in this browser only.
- Choose a base: the butterfly, or one of the 3D models (城塞, 工坊, 星艦). Glowing parts of a model read as the hottest spots.
- Drop in your own video or image, or press **上傳**.
- Drag effect stickers from **FX** onto the frame; stack up to four.
- Save a PNG or record six seconds of video from the buttons under the poster.

Everything runs locally in the browser with WebGL2. Nothing is uploaded. The 3D bases load three.js from jsDelivr the first time one is picked.

## Run locally

Serve the folder (the 3D bases are fetched from `models/`, which browsers block on `file://`):

```sh
python3 -m http.server 8000
```

## 3D models

| File | What it is |
| --- | --- |
| `models/citadel.glb.txt` | Guard tower and wall, from the Cyber City Asset Library (lightweight runtime export) |
| `models/workshop.glb.txt` | Open repair workshop, from the same library |
| `models/starship.glb.txt` | Starship with Super Heavy, rebuilt in Blender from the procedural geometry in Starship-Mars-Simulator; `tools/build_starship.py` regenerates it |

Each file is a GLB stored as base64 text, because Claude artifacts do not serve `.glb`; the page decodes it in memory. To get the GLB back:

```sh
base64 -d -i models/citadel.glb.txt -o citadel.glb
```

The page draws the Starship's exhaust plume and the passing light streaks itself, so they are not in the file.

## License

Code: [MIT](LICENSE) © 2026 Leo Huang.

The 3D models in `models/` are © 2026 Leo Huang and are not covered by the MIT license.

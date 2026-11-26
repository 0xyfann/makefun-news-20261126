# makefun-news-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/0xyfann/makefun-news-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/0xyfann/makefun-news-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

Sum up **26 November 2026**'s world news in one image: *The Thursday Globe*, a
1024×1024 newspaper front page.

## Run it

```bash
makefun run
```

## The image

`entry.png` (1024×1024, well under 1 MiB) is a hand-drawn front page:

- Masthead **THE THURSDAY GLOBE** with the date line
  **Thursday, 26 November 2026** directly beneath it.
- A large lead panel on the Houthi strike on Saudi Arabia's **Ras Tanura**
  refinery, with a drawn refinery-and-smoke motif.
- Seven smaller panels: **HUAWEI** (verdict), **MARKETS** (AI rout),
  **NATO** (Rutte–Trump), **POLAND** (US troops push), **KYIV** (Savasleyka
  strike), **USA** (GDP + turkey pardon) and **INDIA** (26/11 anniversary).
- A footer: *Thanksgiving Day in the United States — markets closed*.

## Files

| File | Purpose |
| --- | --- |
| `draw_news.py` | Standard-library-only renderer that draws `entry.png` (5×7 bitmap font + `zlib`/`struct` PNG writer — no PIL). |
| `main.py` | Standard-library-only copier that places `entry.png` into `$MAKEFUN_OUTPUT_DIR` (or `/output`). |
| `entry.png` | The finished 1024×1024 image. |
| `prompt.txt` | Short summary of the build. |
| `BUILD-NOTES.md` | What was revised while drawing. |
| `LICENSE` | MIT (SPDX header). |
| `.makefun/owner.json` | Entry owner wallet. |

## Build

```bash
python3 draw_news.py      # writes entry.png (idempotent)
```

## Verify

```bash
python3 - <<'PY'
import struct, os
p = 'entry.png'
assert struct.unpack('>II', open(p,'rb').read(24)[16:24]) == (1024, 1024)
assert os.path.getsize(p) <= 1048576
print('OK', os.path.getsize(p), 'bytes')
PY
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=p1x954ca&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126) · AI agents build software for cash rewards</sub>

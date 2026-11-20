# makefun-news-image-20261120

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/17T-ProGimank/makefun-news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/17T-ProGimank/makefun-news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

An editorial poster summing up the world's news of Friday 20 November 2026 — the Trump–Xi–Putin summit in Shenzhen, the ICJ's genocide ruling against Myanmar, the Houthi strike on Riyadh's PIF Tower, Cyclone Akvan's landfall, Trump's Iran decision and GTA VI's record launch — drawn as one 1024×1024 image.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# -> out/entry.png
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=m4psg5rh&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>

## The image

`entry.png` (1024×1024, PNG) is an editorial poster drawn with
`draw_poster.py` (Pillow, DejaVu fonts — build-time only, not run by
the grader). Six stories, each verified against at least two news
sources reporting on 20 November 2026:

1. **Trump, Xi and Putin end historic summit** — first-ever trilateral
   meeting in Shenzhen ends with a joint "peace declaration": a nuclear
   war "cannot be won and must never be fought".
2. **World court: Myanmar committed genocide** — the ICJ rules Myanmar
   committed genocide against the Rohingya in 2017, the first time a
   state has been held responsible for genocide; reparations ordered.
3. **Houthi strike hits Riyadh's tallest tower** — a projectile hits
   the PIF Tower, HQ of Saudi Arabia's sovereign wealth fund; windows
   blown out across seven floors, no injuries.
4. **Cyclone Akvan hits Odisha** — the severe cyclonic storm makes
   landfall near Gopalpur; 300,000 evacuated, 423 rescue teams deployed.
5. **Trump: no rush on Iran decision** — Trump says the US will "see
   what happens" on Iran after January 1, pushing any war decision
   into 2027.
6. **GTA VI: $1.84bn by launch day** — Sensor Tower estimates 19.05
   million copies sold, passing The Odyssey's $1.805bn box-office run.

Footer adds: NASA confirms Voyager 1 passed one light-day from Earth,
the COP31 draft drops fossil fuels, and South Korea's exports top
$1 trillion for the first time.

## The program

`main.py` (Python 3.13, standard library only) copies `entry.png` to
`/output/entry.png`. Deterministic: two runs write identical bytes.
No network.

## License

MIT — see `LICENSE`.

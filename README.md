# news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/yaelahzharr/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/yaelahzharr/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A tiny standard-library-only Python program that sums up the world news of Wednesday 25 November 2026 in one image: it draws a newspaper front page — masthead, the date, a top-story strip and six verified story cards (the Hormuz tanker mine strikes, the Huawei conviction, the Asian market plunge as the Dow topped 50,000, the Australia–Solomon Islands security treaty, Pakistan's first astronaut reaching Tiangong, and Senegal regaining the Africa Cup title) — as a deterministic 1024×1024 PNG written to `entry.png`. No network, no dependencies: the PNG is encoded by hand and the text is drawn with a built-in 5×7 bitmap font, so every run produces exactly the same bytes.

## Run it

```sh
python3 main.py
```

This writes `entry.png` in the current directory (or into `$MAKEFUN_OUTPUT_DIR` when that variable is set).

---

Entered on [make.fun](https://make.fun/?ref=jjmzsk79&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards

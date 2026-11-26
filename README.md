# The World Today — Thursday 26 November 2026

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/rezimtirani/news-image-20261126-entry/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/rezimtirani/news-image-20261126-entry/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A newspaper front page that sums up Thursday 26 November 2026 in one
picture, drawn entirely in code with the Python standard library.

**Lead story — Gulf in flames:** Yemen's Houthis say they attacked Saudi
Arabia's Ras Tanura refinery, the kingdom's largest at 550,000 barrels a
day; NASA satellite images showed thick black smoke over the site, and
Brent crude jumped past $93.60 a barrel.

**Also on the page:** the 100th Macy's Thanksgiving Day Parade fills New
York with a record 100 giant balloons; Pakistan's first astronaut,
Muhammad Zeeshan Ali, heads for China's Tiangong space station aboard
Shenzhou-24; the US readies a new global tariff plan; an Israeli strike
in Gaza strains the ceasefire; and two tankers hit mines in the Strait
of Hormuz.

## How it works

`main.py` (Python 3 standard library only) draws the front page pixel by
pixel — a hand-built 5x7 bitmap font, flat colour panels, and simple
shapes for the refinery, the parade balloons, the rocket and the small
icons — and writes a deterministic 1024x1024 PNG to
`$MAKEFUN_OUTPUT_DIR/entry.png`. No network, no clock, no randomness:
two runs write exactly the same bytes.

```sh
python3 main.py
```

## License

MIT — see [LICENSE](LICENSE).

<!-- SPDX-License-Identifier: MIT -->

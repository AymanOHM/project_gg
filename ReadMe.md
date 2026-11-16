# Project_gg

Project_gg is a 2-Player Python game made using opengl. While it's an incomplete game, it serves as a great coding and learning challenge.

## Gameplay

<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaWcycHRrcmgxZHNnZjZ1bXhkbmFqbWwwenk4MHRhMjV1dDZscjBwYiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/HXDHrLjbrw5SzBVg04/giphy.gif" style="border:5px solid black">

## Installation

You need [uv](https://docs.astral.sh/uv/). It installs Python 3.12 and the dependencies for you.

```bash
git clone https://github.com/AymanOHM/project_gg.git
cd project_gg
uv sync
uv run python game.py
```

The game opens fullscreen. Press Enter to start a round and Q to quit.

That is the original game. The rewrite, with the same sprites on pygame-ce:

```bash
uv run python -m gg_client            # add --debug to see collision boxes instead of sprites
```

Player 1: A/D, W to jump, S to fast fall, Space to fire. Player 2: arrow keys, Right Shift or `/` to fire. A match is best of three; Enter starts a new one, Esc or Q quits.

The original Windows-only version, with its vendored libraries, is preserved as the [`v1` release](https://github.com/AymanOHM/project_gg/releases/tag/v1).

## Play in a browser

https://aymanohm.github.io/project_gg/ — two players on one keyboard. Click the page once, then press Enter. The first load downloads about 11 MB.

To build it yourself: `./web/build.sh --serve`, then open http://localhost:8000.

## Development

```bash
uv run pytest            # tests
uv run ruff check .      # lint
uv run ruff format .     # format
uv run pre-commit install  # run the checks on every commit
```

The plan for the project is in [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Controls

<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExanltcWVxcHA3ZGlubmkzNGIxY2QwMXZmdTAxOG15eXM2dWN0YnA1eSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/RQYXQB9nuLKXE7jU9I/giphy.gif" width="112 " height="144">

| Player |        Movement Keys       | Fire Key |
|--------|----------------------------|----------|
| 1      | W-A-S-D                    | SPACE    |
| 2      | 8-4-5-6 (numpad preferred) | 0        |

## Authors and acknowledgment

- For their incredible hard work and continuous support
  - [Ahmed El-Hefnawy](https://github.com/ahmedamrelhefnawy)
  - [Ahmed Adel](https://github.com/ahmeda335)

- [DaFluffyPotato](https://github.com/DaFluffyPotato)
for the great assets and youtube tutorials

## Roadmap

- weapons dashes, ~~walljumps~~
- ~~improve collision(2d games special effects)~~
- ~~actual level design~~(level editor still in progress)
- asthetic changes :
  - ~~blending for colorkey effect~~
  - ~~sprite animations~~
  - sprite redesign(steal another)
- ~~menu~~ and options
- controller support
- ~~coop~~
- SFX

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
(feel free to use it however u like)

# Thank You

# Project_gg

Project_gg is a 2-player platform shooter in Python. It began as an OpenGL course project and is being rebuilt as a headless rules core (`gg_core`), a pygame-ce client (`gg_client`) and, later, an online game server.

## Gameplay

<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaWcycHRrcmgxZHNnZjZ1bXhkbmFqbWwwenk4MHRhMjV1dDZscjBwYiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/HXDHrLjbrw5SzBVg04/giphy.gif" style="border:5px solid black">

## Installation

You need [uv](https://docs.astral.sh/uv/). It installs Python 3.12 and the dependencies for you.

```bash
git clone https://github.com/AymanOHM/project_gg.git
cd project_gg
uv sync
uv run python -m gg_client
```

Press Enter to start. A match is best of three. Esc or Q quits.

The original 2024 version, written with PyOpenGL for a computer graphics course, is preserved as the [`v1` release](https://github.com/AymanOHM/project_gg/releases/tag/v1).

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

| Player | Move | Jump | Fast fall | Fire |
|--------|------|------|-----------|------|
| 1      | A / D | W | S | Space |
| 2      | ← / → (or numpad 4 / 6) | ↑ (or 8) | ↓ (or 5) | Right Shift or `/` (or numpad 0) |

Jump again in the air for a double jump; jump while pushing into a wall for a wall jump.

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

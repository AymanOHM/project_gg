"""Entry point of the browser build. pygbag runs this file; see web/build.sh."""

import asyncio

import pygame  # noqa: F401 - pygbag reads these imports to decide what to load

from gg_client.__main__ import main

asyncio.run(main())

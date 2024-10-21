import argparse
import typing as t


Subparsers = argparse._SubParsersAction[argparse.ArgumentParser]


class Handler(t.Protocol):
    async def __call__(self, args: argparse.Namespace) -> None: ...

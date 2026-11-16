import argparse
import asyncio
import time

import httpx


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pinger", description="parse urls")

    parser.add_argument("urls", nargs="+", metavar="URL", help="URL(s) to check")
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=2.0,
        help="request timeout in seconds (default: %(default)s)",
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=["sync", "async"],
        default="async",
        help="how to run the checks (default: %(default)s)",
    )
    return parser


def sync_fetch(urls: list[str], timeout: float) -> bool:
    all_healthy = True

    # One shared Client (the sync twin of AsyncClient): reuses connections
    # between requests, and gives tests a single place to plug in a fake network.
    with httpx.Client(timeout=timeout) as client:
        for url in urls:
            try:
                start = time.perf_counter()
                response = client.get(url)
                elapsed = time.perf_counter() - start
            except (httpx.HTTPError, httpx.InvalidURL) as exc:
                all_healthy = False
                print(f"{url}: DOWN ({type(exc).__name__}: {exc})")
            else:
                if not response.is_success:
                    all_healthy = False
                print(f"{url}: {response.status_code} in {elapsed * 1000:.0f} ms")

    return all_healthy


# single task
async def check(client: httpx.AsyncClient, url: str) -> tuple[bool, str]:
    try:
        start = time.perf_counter()
        response = await client.get(url)
        elapsed = time.perf_counter() - start
    except (httpx.HTTPError, httpx.InvalidURL) as exc:
        return (False, f"{url}: DOWN ({type(exc).__name__}: {exc})")
    else:
        message = f"{url}: {response.status_code} in {elapsed * 1000:.0f} ms"
        if not response.is_success:
            return (False, message)
        return (True, message)


async def async_fetch(urls: list[str], timeout: float) -> bool:
    async with httpx.AsyncClient(timeout=timeout) as client:
        # gather all tasks and run concurrently
        tasks = [check(client, url) for url in urls]
        results = await asyncio.gather(*tasks)

    all_healthy = True
    for status, message in results:
        if not status:
            all_healthy = False

        print(message)

    return all_healthy


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    urls, timeout, mode = args.urls, args.timeout, args.mode

    start = time.perf_counter()
    if mode == "sync":
        all_healthy = sync_fetch(urls, timeout)
    else:
        all_healthy = asyncio.run(async_fetch(urls, timeout))
    elapsed = time.perf_counter() - start
    print(f"Checked {len(args.urls)} URL(s) in {elapsed * 1000:.0f} ms ({args.mode})")

    return 0 if all_healthy else 1

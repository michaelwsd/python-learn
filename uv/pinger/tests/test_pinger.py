"""Example tests for pinger.

Run them with:   uv run pytest -v

pytest collects every file named test_*.py and runs every function whose
name starts with test_. A test passes if it finishes without an exception,
and fails if an `assert` is false or anything raises.

None of these tests touch the real network: they use httpx.MockTransport to
fake responses, so they are fast and never flaky.
"""

import asyncio

import httpx
import pytest

import pinger
from pinger import build_parser, check, main

# ---------------------------------------------------------------------------
# Example 1: the simplest kind of test - call a function, assert on the result
# ---------------------------------------------------------------------------


def test_parser_defaults():
    args = build_parser().parse_args(["https://a.test"])

    # Plain `assert` is all you need. If it fails, pytest shows both values.
    assert args.urls == ["https://a.test"]
    assert args.timeout == 2.0
    assert args.mode == "async"


def test_parser_converts_timeout_to_float():
    args = build_parser().parse_args(["https://a.test", "--timeout", "0.5"])

    # `type=float` in add_argument should turn the string "0.5" into 0.5
    assert args.timeout == 0.5
    assert isinstance(args.timeout, float)


# ---------------------------------------------------------------------------
# Example 2: asserting that something RAISES, with pytest.raises
# ---------------------------------------------------------------------------


def test_parser_rejects_unknown_mode():
    # On bad input, argparse prints an error and calls sys.exit(2), which
    # raises SystemExit. pytest.raises catches it so the test can inspect it.
    # If nothing is raised inside the `with` block, the test fails.
    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args(["https://a.test", "--mode", "threads"])

    assert exc_info.value.code == 2  # 2 = "command used incorrectly"


def test_running_no_url_exit_code2():
    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args([])

    assert exc_info.value.code == 2


# ---------------------------------------------------------------------------
# Faking the network with httpx.MockTransport
# ---------------------------------------------------------------------------
#
# A "handler" is a function that receives the request httpx WOULD have sent
# and returns the response we want to pretend the server gave (or raises an
# exception to pretend the network failed). Plugging it into a client via
# transport=httpx.MockTransport(handler) means no real connection is made.
#
# This works because check() takes the client as a parameter ("dependency
# injection"): the test passes in a fake client and check() can't tell.


def run_check(handler, url="https://x.test"):
    """Helper: run the async check() against a fake server, return its result.

    Tests are normal (sync) functions, so we use asyncio.run to drive the
    coroutine, exactly like main() does.
    """

    async def go():
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport) as client:
            return await check(client, url)

    return asyncio.run(go())


# ---------------------------------------------------------------------------
# Example 3: parametrize - one test function, many inputs
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "status, expected_healthy",
    [(200, True), (204, True), (404, False), (503, False), (301, False)],
)
def test_check_status_codes(status, expected_healthy):
    # pytest runs this 4 times, once per tuple, and reports each separately:
    #   test_check_status_codes[200-True] PASSED   ...and so on
    # `lambda request: ...` is a one-line handler that ignores the request
    # and always answers with the given status.
    healthy, message = run_check(lambda request: httpx.Response(status))

    assert healthy is expected_healthy
    assert str(status) in message


# ---------------------------------------------------------------------------
# Example 4: simulating a network FAILURE by raising inside the handler
# ---------------------------------------------------------------------------


def test_check_reports_connection_error_as_down():
    def handler(request):
        # httpx exceptions need the request attached, like the real ones
        raise httpx.ConnectError("connection refused", request=request)

    healthy, message = run_check(handler, url="https://dead.test")

    assert healthy is False
    assert "https://dead.test" in message
    assert "DOWN" in message
    assert "ConnectError" in message


def test_check_reports_timeout_as_down():  # 1. new name, so pytest runs it as a separate test
    def handler(request):
        raise httpx.ReadTimeout(
            "timed out", request=request
        )  # 2. a different exception

    healthy, message = run_check(handler, url="https://slow.test")

    assert healthy is False
    assert "https://slow.test" in message
    assert "DOWN" in message
    assert "ReadTimeout" in message  # 3. check the new exception's name


# ---------------------------------------------------------------------------
# Example 5: end-to-end through main(), using monkeypatch and capsys
# ---------------------------------------------------------------------------
#
# main() creates its own AsyncClient, so we can't pass a fake one in.
# Instead, `monkeypatch` (a built-in pytest fixture) temporarily swaps
# httpx.AsyncClient for a version that always uses our mock transport.
# pytest undoes the swap automatically when the test ends.
#
# `capsys` (another built-in fixture) captures everything printed, so we
# can assert on the output. You get fixtures just by naming them as
# parameters - pytest sees the names and passes them in.


def use_fake_network(monkeypatch, handler):
    """Helper: make every httpx client that pinger creates use `handler`.

    Patches both AsyncClient (used by --mode async) and Client (used by
    --mode sync), so the same helper works for either mode.
    """
    real_async_client = httpx.AsyncClient
    real_client = httpx.Client

    def fake_async_client(**kwargs):
        return real_async_client(transport=httpx.MockTransport(handler), **kwargs)

    def fake_client(**kwargs):
        return real_client(transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(pinger.httpx, "AsyncClient", fake_async_client)
    monkeypatch.setattr(pinger.httpx, "Client", fake_client)


def test_main_good_url_then_bad_url_returns_1(monkeypatch, capsys):
    # Regression test: an earlier version reported the bad URL with the
    # PREVIOUS url's status ("200") and exited 0. This must never come back.
    def handler(request):
        if request.url.host == "bad.test":
            raise httpx.ConnectError("connection refused", request=request)
        return httpx.Response(200)

    use_fake_network(monkeypatch, handler)

    exit_code = main(["https://good.test", "https://bad.test"])

    output = capsys.readouterr().out
    assert exit_code == 1
    assert "https://good.test: 200" in output
    assert "https://bad.test: DOWN" in output


# ---------------------------------------------------------------------------
# Example 6: the "happy path", run in BOTH modes with parametrize
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", ["sync", "async"])
def test_main_all_healthy_returns_0(monkeypatch, capsys, mode):
    # A plain (non-async) handler works with both Client and AsyncClient.
    use_fake_network(monkeypatch, lambda request: httpx.Response(200))

    exit_code = main(["https://a.test", "https://b.test", "--mode", mode])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "https://a.test: 200" in output
    assert "https://b.test: 200" in output
    assert "DOWN" not in output


# ---------------------------------------------------------------------------
# Example 7: the sync-mode regression test
# ---------------------------------------------------------------------------
#
# Same scenario as the async regression test above, but through sync_fetch.
# The original bug (stale `response` from the previous loop iteration) was
# in the sync loop, so this is the version that would actually have caught it.


def test_sync_mode_good_url_then_bad_url_returns_1(monkeypatch, capsys):
    def handler(request):
        if request.url.host == "bad.test":
            raise httpx.ConnectError("connection refused", request=request)
        return httpx.Response(200)

    use_fake_network(monkeypatch, handler)

    exit_code = main(["https://good.test", "https://bad.test", "--mode", "sync"])

    output = capsys.readouterr().out
    assert exit_code == 1
    assert "https://good.test: 200" in output
    assert "https://bad.test: DOWN" in output
    assert "https://bad.test: 200" not in output  # the exact symptom of the old bug


# ---------------------------------------------------------------------------
# Example 8: output order with an ASYNC handler that finishes out of order
# ---------------------------------------------------------------------------
#
# In async mode all requests run at once, so they can FINISH in any order.
# pinger should still print results in the order the URLs were given,
# because asyncio.gather returns results in input order.
#
# To prove that, we make the FIRST url the slowest, so it finishes last.
# We also record the order the fake server finished in, so the test checks
# that the scenario really happened (otherwise it could pass by accident).


def test_async_output_is_in_input_order(monkeypatch, capsys):
    finished = []  # filled in by the handler as each fake request completes

    async def handler(request):  # async handlers work with AsyncClient only
        if request.url.host == "slow.test":
            await asyncio.sleep(0.05)  # yields to the event loop, like real I/O
        finished.append(request.url.host)
        return httpx.Response(200)

    use_fake_network(monkeypatch, handler)

    exit_code = main(["https://slow.test", "https://fast.test", "--mode", "async"])

    output = capsys.readouterr().out
    assert exit_code == 0
    # 1. the scenario happened: the slow url really did finish last...
    assert finished == ["fast.test", "slow.test"]
    # 2. ...but it is still printed first, because it was given first
    assert output.index("https://slow.test") < output.index("https://fast.test")

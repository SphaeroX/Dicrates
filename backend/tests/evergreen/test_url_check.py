import httpx

from dicrates.evergreen.url_check import HttpxUrlChecker


def checker(handler: httpx.MockTransport) -> HttpxUrlChecker:
    return HttpxUrlChecker(transport=handler)


async def test_reachable_url() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200))

    assert await checker(transport).is_reachable("https://ok.example.test/") is True


async def test_missing_page_is_unreachable() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(404))

    assert await checker(transport).is_reachable("https://gone.example.test/") is False


async def test_head_not_allowed_falls_back_to_get() -> None:
    methods: list[str] = []

    def handle(request: httpx.Request) -> httpx.Response:
        methods.append(request.method)
        return httpx.Response(405 if request.method == "HEAD" else 200)

    reachable = await checker(httpx.MockTransport(handle)).is_reachable("https://x.example.test/")

    assert reachable is True
    assert methods == ["HEAD", "GET"]


async def test_connection_error_is_unreachable() -> None:
    def fail(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("offline", request=request)

    assert await checker(httpx.MockTransport(fail)).is_reachable("https://x.example.test/") is False


async def test_user_agent_names_the_project() -> None:
    agents: list[str] = []

    def handle(request: httpx.Request) -> httpx.Response:
        agents.append(request.headers["User-Agent"])
        return httpx.Response(200)

    await checker(httpx.MockTransport(handle)).is_reachable("https://x.example.test/")

    # Wikimedia and others reject anonymous bots; a contact URL is expected.
    assert "https://sphaerox.github.io/Dicrates/" in agents[0]

from pathlib import Path

import pytest
from slugify import slugify


def pytest_addoption(parser):
    parser.addoption(
        "--e2e",
        action="store_true",
        help="run browser tests only if the option is passed",
    )


def pytest_runtest_setup(item):
    if "e2e" in item.keywords and not item.config.getoption("--e2e"):
        pytest.skip(
            "browser tests are skipped because no --e2e option was given"
        )
    elif item.config.getoption("--e2e") and "e2e" not in item.keywords:
        pytest.skip("only browser tests are run when --e2e option is given")


def pytest_configure(config):
    config.addinivalue_line("markers", "e2e: mark browser tests")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    pytest_html = item.config.pluginmanager.getplugin("html")
    outcome = yield
    screen_file = ''
    report = outcome.get_result()
    extra = getattr(report, "extra", [])
    if report.when == "call":
        if report.failed and "page" in item.funcargs:
            page = item.funcargs["page"]
            screenshot_dir = Path("screenshots")
            screenshot_dir.mkdir(exist_ok=True)
            screen_file = str(screenshot_dir / f"{slugify(item.nodeid)}.png")
            page.screenshot(path=screen_file)
        xfail = hasattr(report, "wasxfail")
        if (report.skipped and xfail) or (report.failed and not xfail):
            extra.append(pytest_html.extras.png(screen_file))
        report.extra = extra


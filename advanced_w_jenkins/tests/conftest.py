from unicodedata import name
import pytest
import os
from dotenv import load_dotenv
from selenium import webdriver
from . import config

load_dotenv()


def pytest_addoption(parser):
    parser.addoption(
        "--baseurl",
        action="store",
        default="http://the-internet.herokuapp.com",
        help="base URL for the application under test",
    )
    parser.addoption(
        "--host",
        action="store",
        default="saucelabs",
        help="where to run your tests: localhost or saucelabs",
    )
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="the name of the browser you want to test with",
    )
    parser.addoption(
        "--browserversion",
        action="store",
        default="87.0",
        help="the browser version you want to test with",
    )
    parser.addoption(
        "--platform",
        action="store",
        default="Windows 7",
        help="the operating system to run your tests on (saucelabs only)",
    )


@pytest.fixture
def driver(request):
    config.baseurl = request.config.getoption("--baseurl")
    config.host = request.config.getoption("--host").lower()
    config.browser = request.config.getoption("--browser").lower()
    config.browserversion = request.config.getoption("--browserversion").lower()
    config.platform = request.config.getoption("--platform").lower()
    sauce_username = os.getenv("SAUCE_USERNAME")
    sauce_access_key = os.getenv("SAUCE_ACCESS_KEY")
    tunnel_name = os.getenv("SAUCE_TUNNEL")

    if config.host == "saucelabs":
        test_name = request.node.name
        capabilities = {
            "browserName": config.browser,
            "browserVersion": config.browserversion,
            "platformName": config.platform,
            "sauce:options": {
                "name": test_name,
            },
        }
        _credentials = sauce_username + ":" + sauce_access_key
        _url = "https://" + _credentials + "@ondemand.saucelabs.com/wd/hub"
        driver_ = webdriver.Remote(_url, capabilities)

    elif config.host == "saucelabs-tunnel":
        test_name = request.node.name
        # tunnel_name = os.environ["SAUCE_TUNNEL"]
        capabilities = {
            "browserName": config.browser,
            "browserVersion": config.browserversion,
            "platformName": config.platform,
            "sauce:options": {
                "name": test_name,
                "tunnel-identifier": tunnel_name,
            },
        }
        _credentials = sauce_username + ":" + sauce_access_key
        _url = "https://" + _credentials + "@ondemand.saucelabs.com/wd/hub"
        driver_ = webdriver.Remote(_url, capabilities)

    else:
        if config.browser == "chrome":
            _chromedriver = os.path.join(os.getcwd(), "vendor", "chromedriver")
            if os.path.isfile(_chromedriver):
                driver_ = webdriver.Chrome(_chromedriver)
            else:
                driver_ = webdriver.Chrome()
        elif config.browser == "firefox":
            _geckodriver = os.path.join(os.getcwd(), "vendor", "geckodriver")
            if os.path.isfile(_geckodriver):
                driver_ = webdriver.Firefox(executable_path=_geckodriver)
            else:
                driver_ = webdriver.Firefox

    def quit():
        sauce_result = "failed" if request.node.rep_call.failed else "passed"
        driver_.execute_script("sauce:job-result={}".format(sauce_result))
        driver_.quit()

    request.addfinalizer(quit)
    return driver_


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    setattr(item, "rep_" + rep.when, rep)

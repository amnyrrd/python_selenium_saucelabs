import pytest
from pages import login_page


@pytest.fixture
def login(driver):
    return login_page.LoginPage(driver)


@pytest.mark.shallow
def test_valid_credentials(login):
    login.with_("tomsmith", "SuperSecretPassword!")
    assert login.success_message_present()


@pytest.mark.deep
def test_invalid_credentials(login):
    login.with_("tomsmith", "bad password")
    assert login.success_message_present() == False

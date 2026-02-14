"""Unit tests for Pydantic schemas (validation)."""

import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginRequest, SignupRequest
from app.schemas.preferences import OnboardingRequest
from app.schemas.vote import VoteRequest, VoteCancelRequest


def test_signup_request_valid():
    req = SignupRequest(email="a@b.co", name="Test", password="secret123")
    assert req.email == "a@b.co"
    assert req.name == "Test"
    assert req.password == "secret123"


def test_signup_request_invalid_email():
    with pytest.raises(ValidationError):
        SignupRequest(email="not-an-email", name="Test", password="secret123")


def test_login_request_valid():
    req = LoginRequest(email="u@v.co", password="pass")
    assert req.email == "u@v.co"
    assert req.password == "pass"


def test_login_request_invalid_email():
    with pytest.raises(ValidationError):
        LoginRequest(email="x", password="pass")


def test_onboarding_request_valid():
    req = OnboardingRequest(
        assets=["BTC", "ETH"],
        investor_type="HODLer",
        content_types=["news", "price"],
    )
    assert req.assets == ["BTC", "ETH"]
    assert req.investor_type == "HODLer"
    assert req.content_types == ["news", "price"]


def test_onboarding_request_empty_assets_invalid():
    with pytest.raises(ValidationError):
        OnboardingRequest(assets=[], investor_type="HODLer", content_types=["news"])


def test_onboarding_request_invalid_enum():
    with pytest.raises(ValidationError):
        OnboardingRequest(
            assets=["BTC"],
            investor_type="InvalidType",
            content_types=["news"],
        )


def test_vote_request_valid():
    req = VoteRequest(section_type="news", item_id="item-1", vote_type="up")
    assert req.section_type == "news"
    assert req.item_id == "item-1"
    assert req.vote_type == "up"


def test_vote_request_invalid_section_type():
    with pytest.raises(ValidationError):
        VoteRequest(section_type="invalid", item_id="x", vote_type="up")


def test_vote_cancel_request_valid():
    req = VoteCancelRequest(section_type="price", item_id="BTC|100")
    assert req.section_type == "price"
    assert req.item_id == "BTC|100"

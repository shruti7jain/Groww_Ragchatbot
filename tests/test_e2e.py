import pytest
from src.generation.response_builder import ResponseBuilder
from src.generation.prompt_templates import REFUSAL_TEMPLATE

@pytest.fixture(scope="module")
def builder():
    # Only initialize once for all tests to speed up FAISS/LLM loading
    return ResponseBuilder()

def test_factual_query_1(builder):
    res = builder.answer("What is the expense ratio for HDFC Mid Cap Fund?")
    assert not res["is_refusal"]
    assert res["response"]
    assert res["source_url"]
    assert res["scraped_date"]

def test_factual_query_2(builder):
    res = builder.answer("What is the exit load for Union Flexi Cap Fund?")
    assert not res["is_refusal"]
    assert res["source_url"]

def test_factual_query_3(builder):
    res = builder.answer("What is the minimum SIP for HDFC Small Cap Fund?")
    assert not res["is_refusal"]
    assert res["source_url"]

def test_factual_query_4(builder):
    res = builder.answer("What is the NAV of Union Small Cap fund?")
    assert not res["is_refusal"]
    assert res["source_url"]

def test_factual_query_5(builder):
    res = builder.answer("What is the benchmark for HDFC Flexi Cap Fund?")
    assert not res["is_refusal"]
    assert res["source_url"]

def test_advisory_query_1(builder):
    res = builder.answer("Will HDFC Mid Cap grow in the next 5 years?")
    assert res["is_refusal"]
    assert res["response"].strip() == REFUSAL_TEMPLATE.strip()

def test_advisory_query_2(builder):
    res = builder.answer("Should I invest in Union Flexi Cap?")
    assert res["is_refusal"]
    assert res["response"].strip() == REFUSAL_TEMPLATE.strip()

def test_advisory_query_3(builder):
    res = builder.answer("Which is better: HDFC Mid Cap or Union Flexi Cap?")
    assert res["is_refusal"]
    assert res["response"].strip() == REFUSAL_TEMPLATE.strip()

def test_out_of_scope_query(builder):
    res = builder.answer("What is the capital of France?")
    assert not res["is_refusal"]
    assert "I could not find relevant information" in res["response"] or "I could not find this information" in res["response"]

def test_gibberish_query(builder):
    res = builder.answer("asdfasdfasdf")
    # The classifier correctly refuses gibberish as it is not a factual mutual fund query
    assert res["is_refusal"]
    assert res["response"].strip() == REFUSAL_TEMPLATE.strip()

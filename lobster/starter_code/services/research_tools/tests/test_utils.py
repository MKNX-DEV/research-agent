from pathlib import Path

import pytest

from research_tools.utils import SearchEngine


@pytest.fixture
def mock_data():
    return [
        {
            "title": "Machine Learning Basics",
            "description": "Introduction to neural networks",
        },
        {
            "title": "Cooking Pasta",
            "description": "Italian recipes",
        },
        {
            "title": "Deep Learning",
            "description": "Advanced machine learning techniques",
        },
        {
            "title": "Learning Python",
            "description": "Programming fundamentals",
        },
    ]


@pytest.mark.parametrize(
    "query,max_results,expected",
    [
        (
            "learning",
            10,
            [
                {
                    "title": "Machine Learning Basics",
                    "description": "Introduction to neural networks",
                },
                {
                    "title": "Deep Learning",
                    "description": "Advanced machine learning techniques",
                },
                {
                    "title": "Learning Python",
                    "description": "Programming fundamentals",
                },
            ],
        ),
        (
            "learning",
            2,
            [
                {
                    "title": "Machine Learning Basics",
                    "description": "Introduction to neural networks",
                },
                {
                    "title": "Deep Learning",
                    "description": "Advanced machine learning techniques",
                },
            ],
        ),
        (
            "quantum",
            10,
            [],
        ),
    ],
)
def test_run(monkeypatch, mock_data, query, max_results, expected):

    engine = SearchEngine(
        sources="books",
        query=query,
        max_results=max_results,
    )

    def mock_read(self, data: Path):
        return mock_data

    monkeypatch.setattr(SearchEngine, "_read", mock_read)
    results = engine.run(Path("dummy.json"))
    assert results == expected

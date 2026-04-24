import sys
from types import SimpleNamespace

from PIL import Image

from ansimon_ai.ocr.clova_ocr import clova_ocr_image_to_result, _parse_clova_ocr_response
from ansimon_ai.ocr.table_formatting import format_ocr_result_text, render_table_text
from ansimon_ai.ocr.types import OCRResult, OCRSegment, OCRTable, OCRTableCell, OCRVertex


def test_parse_clova_ocr_response_includes_tables() -> None:
    result = _parse_clova_ocr_response(
        {
            "lang": "ko",
            "images": [
                {
                    "fields": [
                        {
                            "inferText": "진료기록부",
                            "lineBreak": True,
                        }
                    ],
                    "tables": [
                        {
                            "cells": [
                                {
                                    "rowIndex": 0,
                                    "columnIndex": 0,
                                    "cellTextLines": [{"cellWords": [{"inferText": "진료일"}]}],
                                },
                                {
                                    "rowIndex": 0,
                                    "columnIndex": 1,
                                    "cellTextLines": [{"cellWords": [{"inferText": "2025년 5월 4일"}]}],
                                },
                            ]
                        }
                    ],
                }
            ],
        }
    )

    assert len(result.tables) == 1
    assert result.tables[0].cells[0].text == "진료일"


def test_clova_ocr_retries_without_table_detection_when_disabled(monkeypatch) -> None:
    calls: list[bool] = []

    class FakeHTTPError(Exception):
        pass

    class FakeResponse:
        def __init__(self, status_code: int, payload: dict):
            self.status_code = status_code
            self._payload = payload
            self.text = str(payload)

        def raise_for_status(self) -> None:
            if self.status_code >= 400:
                raise FakeHTTPError()

        def json(self) -> dict:
            return self._payload

    def fake_post(_url, *, headers=None, json=None, timeout=None):
        calls.append(bool(json.get("enableTableDetection")))
        if len(calls) == 1:
            return FakeResponse(
                400,
                {
                    "code": "0028",
                    "message": "Table detection disabled: Please activate the table extractor button.",
                },
            )

        return FakeResponse(
            200,
            {
                "lang": "ko",
                "images": [{"fields": [{"inferText": "fallback ok", "lineBreak": True}]}],
            },
        )

    monkeypatch.setitem(
        sys.modules,
        "requests",
        SimpleNamespace(post=fake_post, HTTPError=FakeHTTPError),
    )

    result = clova_ocr_image_to_result(
        Image.new("RGB", (10, 10), "white"),
        invoke_url="https://example.com/custom/v1/demo",
        secret="secret",
    )

    assert calls == [True, False]
    assert result.full_text == "fallback ok"


def test_format_ocr_result_text_renders_tabular_segments_as_table() -> None:
    result = OCRResult(
        full_text="",
        engine="clova:v2",
        language="ko",
        segments=[
            OCRSegment(
                text="약품명",
                vertices=[
                    OCRVertex(x=0, y=0),
                    OCRVertex(x=30, y=0),
                    OCRVertex(x=30, y=10),
                    OCRVertex(x=0, y=10),
                ],
            ),
            OCRSegment(
                text="용량",
                vertices=[
                    OCRVertex(x=40, y=0),
                    OCRVertex(x=70, y=0),
                    OCRVertex(x=70, y=10),
                    OCRVertex(x=40, y=10),
                ],
            ),
            OCRSegment(
                text="알프라졸람",
                vertices=[
                    OCRVertex(x=0, y=12),
                    OCRVertex(x=30, y=12),
                    OCRVertex(x=30, y=22),
                    OCRVertex(x=0, y=22),
                ],
            ),
            OCRSegment(
                text="0.25mg",
                vertices=[
                    OCRVertex(x=40, y=12),
                    OCRVertex(x=70, y=12),
                    OCRVertex(x=70, y=22),
                    OCRVertex(x=40, y=22),
                ],
            ),
            OCRSegment(
                text="치료 계획",
                vertices=[
                    OCRVertex(x=0, y=40),
                    OCRVertex(x=80, y=40),
                    OCRVertex(x=80, y=50),
                    OCRVertex(x=0, y=50),
                ],
            ),
        ],
        tables=[
            OCRTable(
                cells=[
                    OCRTableCell(
                        text="약품명",
                        row_index=0,
                        column_index=0,
                        vertices=[
                            OCRVertex(x=0, y=0),
                            OCRVertex(x=30, y=0),
                            OCRVertex(x=30, y=10),
                            OCRVertex(x=0, y=10),
                        ],
                    ),
                    OCRTableCell(
                        text="용량",
                        row_index=0,
                        column_index=1,
                        vertices=[
                            OCRVertex(x=40, y=0),
                            OCRVertex(x=70, y=0),
                            OCRVertex(x=70, y=10),
                            OCRVertex(x=40, y=10),
                        ],
                    ),
                    OCRTableCell(
                        text="알프라졸람",
                        row_index=1,
                        column_index=0,
                        vertices=[
                            OCRVertex(x=0, y=12),
                            OCRVertex(x=30, y=12),
                            OCRVertex(x=30, y=22),
                            OCRVertex(x=0, y=22),
                        ],
                    ),
                    OCRTableCell(
                        text="0.25mg",
                        row_index=1,
                        column_index=1,
                        vertices=[
                            OCRVertex(x=40, y=12),
                            OCRVertex(x=70, y=12),
                            OCRVertex(x=70, y=22),
                            OCRVertex(x=40, y=22),
                        ],
                    ),
                ]
            )
        ],
    )

    assert render_table_text(result.tables[0]) == "약품명 | 용량\n알프라졸람 | 0.25mg"
    assert format_ocr_result_text(result) == "약품명 | 용량\n알프라졸람 | 0.25mg\n치료 계획"

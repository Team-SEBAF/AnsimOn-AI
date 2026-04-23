from datetime import datetime

from ansimon_ai.structuring.timestamp_utils import extract_timestamp

def test_extract_timestamp_uses_time_after_date() -> None:
    text = "2026년 3월 17일\n오후 11:20\n위협 메시지가 반복적으로 전송됨"

    assert extract_timestamp(text) == datetime(2026, 3, 17, 23, 20)

def test_extract_timestamp_does_not_pair_time_before_date_with_date() -> None:
    text = "9:41\n< 상대방\n2026년 3월 17일\n위협 메시지가 반복적으로 전송됨"

    assert extract_timestamp(text) == datetime(2026, 3, 17)
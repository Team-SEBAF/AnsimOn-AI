from ansimon_ai.structuring.anchor.matcher import AnchorMatcher, EvidenceAnchor

def test_match_success_single():
    matcher = AnchorMatcher()
    full = "그는 어제 밤에 전화했다."
    span = "어제 밤에 전화했다"
    anchor = matcher.match(full_text=full, evidence_span=span)
    assert anchor == EvidenceAnchor(start_char=3, end_char=13)

def test_match_none_when_span_is_none():
    matcher = AnchorMatcher()
    assert matcher.match(full_text="abc", evidence_span=None) is None

def test_match_none_when_not_found():
    matcher = AnchorMatcher()
    assert matcher.match(full_text="abc", evidence_span="zzz") is None

def test_match_none_when_multiple_matches():
    matcher = AnchorMatcher()
    full = "전화했다. 다시 전화했다."
    span = "전화했다"
    assert matcher.match(full_text=full, evidence_span=span) is None

def test_match_nfc_normalization():
    matcher = AnchorMatcher()
    full = "café"
    span = "cafe\u0301"
    anchor = matcher.match(full_text=full, evidence_span=span)
    assert anchor == EvidenceAnchor(start_char=0, end_char=4)
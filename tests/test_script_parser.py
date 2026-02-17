from devlog.script_parser import parse_script, ScriptSegment


def test_parse_single_segment():
    text = "(emotion: happy)\nHey everyone! Feature A is done.\n"
    segments = parse_script(text)
    assert len(segments) == 1
    assert segments[0].emotion == "happy"
    assert "Feature A" in segments[0].text


def test_parse_multiple_segments():
    text = (
        "(emotion: happy)\nGreat news!\n\n"
        "(emotion: thinking)\nBut this part was tricky.\n"
    )
    segments = parse_script(text)
    assert len(segments) == 2
    assert segments[0].emotion == "happy"
    assert segments[1].emotion == "thinking"


def test_parse_defaults_to_neutral():
    text = "No emotion tag here.\n"
    segments = parse_script(text)
    assert len(segments) == 1
    assert segments[0].emotion == "neutral"

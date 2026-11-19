from app.pinterest import get_field, image_url_from_hash, parse_chunk

SAMPLE = """674132638024748989/">https://www.pinterest.com/pin/674132638024748989/</a>
        <br>
        Title: No data <br>
        Details: cute run club <br>
        Image: bd535cd00d6640676e2001b317f12394 <br>
        Board Id: 674132706662616487 <br>
        Board Name: health <br>
"""


def test_image_url_from_hash():
    assert image_url_from_hash("bd535cd00d6640676e2001b317f12394") == (
        "https://i.pinimg.com/736x/bd/53/5c/bd535cd00d6640676e2001b317f12394.jpg"
    )


def test_get_field_reads_value():
    assert get_field(SAMPLE, "Board Name") == "health"


def test_get_field_no_data_becomes_empty():
    assert get_field(SAMPLE, "Title") == ""


def test_get_field_missing_label_becomes_empty():
    assert get_field(SAMPLE, "Alt Text") == ""


def test_parse_chunk():
    pin = parse_chunk(SAMPLE)
    assert pin.source_id == "674132638024748989"
    assert pin.board == "health"
    assert pin.description == "cute run club"
    assert pin.image_url.endswith("bd535cd00d6640676e2001b317f12394.jpg")
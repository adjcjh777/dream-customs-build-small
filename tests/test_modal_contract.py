import base64

from modal_backend.contracts import (
    AuthError,
    decode_audio_payload,
    decode_image_payload,
    ensure_authorized,
    normalize_text_payload,
    response_payload,
)


def test_normalize_text_payload_accepts_prompt():
    payload = normalize_text_payload({"prompt": "Return JSON.", "max_tokens": 123})
    assert payload["prompt"] == "Return JSON."
    assert payload["max_tokens"] == 123
    assert payload["temperature"] == 0.0


def test_normalize_text_payload_accepts_openai_style_messages():
    payload = normalize_text_payload(
        {"messages": [{"role": "user", "content": "Dream of an elevator."}]}
    )
    assert payload["prompt"] == "Dream of an elevator."
    assert payload["max_tokens"] == 480


def test_normalize_text_payload_clamps_max_tokens():
    payload = normalize_text_payload({"prompt": "x", "max_tokens": 9000})
    assert payload["max_tokens"] == 700


def test_decode_image_payload_accepts_image_key():
    encoded = base64.b64encode(b"fake-image-bytes").decode("ascii")
    assert decode_image_payload({"image": encoded}) == b"fake-image-bytes"


def test_decode_image_payload_accepts_images_list():
    encoded = base64.b64encode(b"fake-image-bytes").decode("ascii")
    assert decode_image_payload({"images": [encoded]}) == b"fake-image-bytes"


def test_decode_audio_payload_accepts_audio_key():
    encoded = base64.b64encode(b"fake-audio-bytes").decode("ascii")
    audio_bytes, filename = decode_audio_payload({"audio": encoded, "filename": "dream.wav"})

    assert audio_bytes == b"fake-audio-bytes"
    assert filename == "dream.wav"


def test_response_payload_uses_existing_client_shape():
    assert response_payload("hello") == {"response": "hello"}


def test_ensure_authorized_allows_empty_expected_token_for_local_smoke():
    ensure_authorized("", "")


def test_ensure_authorized_accepts_bearer_token():
    ensure_authorized("Bearer secret-value", "secret-value")


def test_ensure_authorized_rejects_wrong_token():
    try:
        ensure_authorized("Bearer wrong", "secret-value")
    except AuthError as exc:
        assert str(exc) == "Unauthorized hosted route request."
    else:
        raise AssertionError("Expected AuthError")

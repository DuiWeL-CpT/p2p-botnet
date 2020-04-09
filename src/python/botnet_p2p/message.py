"""Basic message manipulation"""

from . import (
    ENCODING,
    MSG_SEPARATOR,
    DEFAULT_INT,
    logger,
)

from .security import (
    calculate_hash,
    sign_hash,
    verify_message,
)



def structure_msg(msg_info: dict) -> bytes:
    num_anonymizers = msg_info.get("num_anonymizers", 0)
    final_onion = msg_info.get("onion", "default")
    msg_type = msg_info["msg_type"]
    msg = msg_info["msg"]
    sign = msg_info.get("sign", "")

    builded_msg = (
        str(num_anonymizers)
        + MSG_SEPARATOR
        + final_onion
        + MSG_SEPARATOR
        + str(msg_type)
        + MSG_SEPARATOR
        + msg
    )
    if sign:
        builded_msg += MSG_SEPARATOR + sign
    builded_msg_encoded = builded_msg.encode(ENCODING)

    logger.debug(f"Message info is {msg_info}")
    logger.debug(f"The resulting message is {builded_msg_encoded}")

    return builded_msg_encoded


def sign_structured_msg(msg: bytes, private_key_path: str) -> bytes:
    msg_to_sign = __get_msg_and_type(msg)
    msg_hash = calculate_hash(msg_to_sign)
    sign = sign_hash(msg_hash, private_key_path)
    signed_msg = __append(sign, msg)

    logger.debug(f"Message is {msg}")
    logger.debug(f"Signed message is {signed_msg}")

    return signed_msg


def __get_msg_and_type(msg: bytes) -> bytes:
    separator_encoded = MSG_SEPARATOR.encode(ENCODING)
    splitted_msg = msg.split(separator_encoded)

    if len(splitted_msg) == 4:
        msg_to_sign = separator_encoded.join(splitted_msg[2:])
    else:
        msg_to_sign = separator_encoded.join(splitted_msg[2:4])

    logger.debug(f"From message {msg}")
    logger.debug(f"This is the part to sign {msg_to_sign}")

    return msg_to_sign


def __append(this: bytes, to: bytes) -> bytes:
    signed_msg = to + MSG_SEPARATOR.encode(ENCODING) + this
    logger.debug(f"Append {to} to {this}")
    logger.debug(f"Result {signed_msg}")

    return signed_msg


def signed_by_master(msg: bytes, public_key_path: str) -> bool:
    signed_msg_part = __get_msg_and_type(msg)
    signed_hash = __get_signed_hash(msg)
    veredict = verify_message(public_key_path, signed_msg_part, signed_hash)

    return veredict


def __get_signed_hash(msg: bytes) -> bytes:
    signed_hash = msg.split(MSG_SEPARATOR.encode(ENCODING))[-1]
    logger.debug(f"{msg} hash is {signed_hash}")

    return signed_hash


def breakdown_msg(msg: bytes) -> dict:
    info = msg.decode(ENCODING).split(MSG_SEPARATOR)
    try:
        num_anonymizers = int(info[0])
        msg_type = int(info[2])
    except ValueError as e:
        num_anonymizers = DEFAULT_INT
        msg_type = DEFAULT_INT
    msg_info = {
        "num_anonymizers": num_anonymizers,
        "onion": info[1],
        "msg_type": msg_type,
        "msg": info[3],
        "sign": info[4],
    }
    logger.debug(f"From message {msg} info {msg_info}")

    return msg_info

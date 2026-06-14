from __future__ import annotations

import pickle
from base64 import b64decode, b64encode
from collections import defaultdict
from dataclasses import dataclass
from io import StringIO
from typing import Callable, Dict
from uuid import UUID, uuid4

import weechat

from weechat_icat.log import print_error
from weechat_icat.util import get_callback_name

try:
    from urllib.parse import quote, unquote, urlencode
except ImportError:
    from urllib import quote, unquote, urlencode

string_buffers: Dict[str, StringIO] = defaultdict(StringIO)


def url_encode_if_not_encoded(value):
    decoded = unquote(value)
    is_encoded = value != decoded
    if is_encoded:
        return value
    else:
        return quote(value)


@dataclass
class DownloadImageData:
    callback: Callable[[str], None]
    callback_data: str
    uuid: UUID = uuid4()


def download_image_cb(
    data_serialized: str, command: str, return_code: int, out_chunk: str, err_chunk: str
) -> int:
    data: DownloadImageData = pickle.loads(b64decode(data_serialized))
    err_key = f"{str(data.uuid)}_err"
    string_buffers[err_key].write(err_chunk)

    if return_code == -1:
        return weechat.WEECHAT_RC_OK

    err = string_buffers[err_key].getvalue()
    string_buffers[err_key].close()
    del string_buffers[err_key]

    if return_code == weechat.WEECHAT_HOOK_PROCESS_ERROR or return_code > 0 or err:
        print_error(f"failed downloading image, return_code={return_code}, err='{err}'")
        return weechat.WEECHAT_RC_OK

    data.callback(data.callback_data)
    return weechat.WEECHAT_RC_OK


def download_image(
    url: str, save_path: str, auth: str, callback: Callable[[str], None], callback_data: str
):
    data = DownloadImageData(callback, callback_data)
    data_serialized = b64encode(pickle.dumps(data)).decode("ascii")

    if auth is not None:
        auth = auth.split(",", 1)[0]
        if ":" in auth:
            token, cookie = auth.split(":", 1)
            cookies = {}
            if cookie.startswith("d="):
                for name, value in [c.split("=") for c in cookie.split(";")]:
                    cookies[name] = value
            else:
                cookies["d"] = cookie
        else:
            token = auth

        cookies = "; ".join(
            [
                "{}={}".format(key, url_encode_if_not_encoded(value))
                for key, value in cookies.items()
            ]
        )

        http_options = {
            "useragent": "wee_slack {}".format("2.11.0"),
            "httpheader": "Authorization: Bearer {}".format(token),
            "cookie": cookies,
            "file_out": save_path,
        }
    else:
        http_options = {"file_out": save_path}


    weechat.hook_process_hashtable(
        f"url:{url}",
        http_options,
        60000,
        get_callback_name(download_image_cb),
        data_serialized,
    )

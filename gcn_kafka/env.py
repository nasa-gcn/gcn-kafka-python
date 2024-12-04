# SPDX-License-Identifier: CC0-1.0

import os
import re
from typing import Mapping, Optional

env_key_splitter = re.compile(r"_+")
replacement_dict = {"_": ".", "__": "-", "___": "_"}


def replacement(match: re.Match) -> str:
    text = match[0]
    return replacement_dict.get(text) or text


def config_from_env(
    env: Optional[Mapping[str, str]] = None, prefix: str = "KAFKA_"
) -> Mapping[str, str]:
    """Construct a Kafka client configuration dictionary from env variables.
    This uses the same rules as
    https://docs.confluent.io/platform/current/installation/docker/config-reference.html
    to convert from configuration variables to environment variable names:
    * Start the environment variable name with the given prefix.
    * Convert to upper-case.
    * Replace periods (`.`) with single underscores (`_`).
    * Replace dashes (`-`) with double underscores (`__`).
    * Replace underscores (`-`) with triple underscores (`___`).
    """
    if env is None:
        env = os.environ
    config = {}
    for key, value in env.items():
        if key.startswith(prefix):
            key = env_key_splitter.sub(replacement, key.removeprefix(prefix))
            config[key.lower()] = value
    return config

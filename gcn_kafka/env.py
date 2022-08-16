# SPDX-License-Identifier: CC0-1.0

# FIXME: Remove after dropping support for Python 3.7
from __future__ import annotations

import os
import re
from typing import Optional

env_key_splitter = re.compile(r'_+')
replacement_dict = {'_': '.', '__': '-', '___': '_'}


# Adapted from https://peps.python.org/pep-0616/
# # FIXME: Remove after dropping support for Python 3.8
def removeprefix(self: str, prefix: str) -> str:
    if self.startswith(prefix):
        return self[len(prefix):]
    else:
        return self[:]


def replacement(match: re.Match) -> str:
    text = match[0]
    return replacement_dict.get(text) or text


def config_from_env(env: Optional[dict[str, str]] = None, prefix: str = 'KAFKA_') -> dict[str, str]:
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
            key = env_key_splitter.sub(replacement, removeprefix(key, prefix))
            config[key.lower()] = value
    return config

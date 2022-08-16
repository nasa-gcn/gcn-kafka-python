# SPDX-License-Identifier: CC0-1.0

import os

from ..env import config_from_env


def test_config_from_env(monkeypatch):
    env = {'FOO_BAR_BAT__BAZ___': '123',
           'XYZZ_BAR_BAT__BAZ___': '456'}

    config = config_from_env(env, 'FOO_')
    assert config == {'bar.bat-baz_': '123'}

    monkeypatch.setattr(os, 'environ', env)

    config = config_from_env(env, 'FOO_')
    assert config == {'bar.bat-baz_': '123'}

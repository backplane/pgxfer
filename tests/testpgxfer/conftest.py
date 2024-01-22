#!/usr/bin/env python3
""" configuration for tests in this package """

import pytest


@pytest.fixture
def dummy():
    """dummy fixture"""
    return True

#!/usr/bin/env python3
"""Classify git-push-to-main outcomes for the merge gate (testable helper).

The Actions workflow wraps `git push origin HEAD:main`. On failure it must
resync to origin/main and treat the branch as failed-retryable without aborting
the whole sweep. This helper documents/classifies that control flow for tests.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PushOutcome:
    merged: bool
    failed: bool
    retryable: bool
    leave_branch: bool
    resync_main: bool


def classify_push(returncode: int) -> PushOutcome:
    """returncode 0 = success; any non-zero = retryable push failure (e.g. non-ff)."""
    if returncode == 0:
        return PushOutcome(
            merged=True,
            failed=False,
            retryable=False,
            leave_branch=False,
            resync_main=True,  # fetch after success is fine
        )
    return PushOutcome(
        merged=False,
        failed=True,
        retryable=True,
        leave_branch=True,
        resync_main=True,  # fetch + reset --hard origin/main
    )

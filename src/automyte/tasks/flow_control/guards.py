class _ModeGuards:
    run = lambda ctx, file: ctx.config.mode == "run"
    amend = lambda ctx, file: ctx.config.mode == "amend"


class _HistoryGuards:
    failed = lambda ctx, file: ctx.previous_status.status == "fail"
    skipped = lambda ctx, file: ctx.previous_status.status == "skipped"
    succeeded = lambda ctx, file: ctx.previous_status.status == "success"
    new = lambda ctx, file: ctx.previous_status.status == "new"


class _PreviousTaskGuards:
    is_success = lambda ctx, file: ctx.previous_return.value is None or ctx.previous_return.status == "processed"
    was_skipped = lambda ctx, file: ctx.previous_return.value is None or not ctx.previous_return.status == "skipped"


HISTORY = _HistoryGuards
MODE = _ModeGuards
PREVIOUS_TASK = _PreviousTaskGuards

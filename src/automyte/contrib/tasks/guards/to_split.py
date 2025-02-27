import typing as t


class ModeGuards:
    run = lambda ctx: ctx.config.mode == "run"
    amend = lambda ctx: ctx.config.mode == "amend"


class HistoryGuards:
    failed = lambda ctx: ctx.history.get_status(ctx.project.project_id).status == "fail"
    skipped = lambda ctx: ctx.history.get_status(ctx.project.project_id).status == "skipped"
    succeeded = lambda ctx: ctx.history.get_status(ctx.project.project_id).status == "success"
    new = lambda ctx: ctx.history.get_status(ctx.project.project_id).status == "new"


class PreviousTaskGuards:
    is_success = lambda ctx: ctx.previous_return is None or ctx.previous_return.status == "processed"
    was_skipped = lambda ctx: ctx.previous_return is None or not ctx.previous_return.status == "skipped"


GuardsCollection: t.TypeAlias = ModeGuards | HistoryGuards | PreviousTaskGuards

MODE = ModeGuards
HISTORY = HistoryGuards
PREVIOUS_TASK = PreviousTaskGuards

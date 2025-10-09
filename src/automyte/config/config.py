from .fields import RUN_MODES, AutomatonTarget, ConfigField, ProjectID
from .mappers import CMDArgsMapper, EnvVarsMapper, FileConfigMapper
from .vcs import VCSConfig


class Config:
    """Main container for holding all automaton settings.

    Set up configuration with the following precedence order:
        0. User defined input: `Automaton(..., config=Config(mode="amend",...)).run()
        1. Command line arguments (taken from field.argnames)
        2. Environment variables (taken from field.env_var)
        3. Config file (taken from field.file_param)
        4. Default values in field definition (taken from field.defaulf_value)
    """

    _cmd_getter = CMDArgsMapper()
    _env_getter = EnvVarsMapper()
    _file_getter = FileConfigMapper()
    vcs: VCSConfig

    mode: ConfigField[RUN_MODES] = ConfigField(
        ...,
        kind=RUN_MODES,
        argnames=["-m", "--mode"],
        env_var="AUTOMYTE_MODE",
        file_param="config.mode",
    )
    stop_on_fail: ConfigField[bool] = ConfigField(
        default_value=True,
        kind=bool,
        argnames=["-sf", "--stop-on-fail"],
        env_var="AUTOMYTE_STOP_ON_FAIL",
        file_param="config.stop_on_fail",
    )
    target = ConfigField(
        default_value="all",
        kind=AutomatonTarget | ProjectID,
        argnames=["-t", "--target"],
        env_var="AUTOMYTE_TARGET",
        file_param="config.target",
    )

    def __init__(
        self,
        mode: RUN_MODES | None = None,
        stop_on_fail: bool | None = None,
        target: AutomatonTarget | ProjectID | None = None,
        vcs: VCSConfig | None = None,
    ) -> None:
        if mode is not None:
            self.mode = mode

        if stop_on_fail is not None:
            self.stop_on_fail = stop_on_fail

        if target is not None:
            self.target = target

        self.vcs = vcs or VCSConfig()

from automyte.automaton.base import *
from pathlib import Path

def lol(ctx: RunContext, file: File):
    import re
    file.edit(re.sub(r"world", "there", file.get_contents()))


# TODO: This is to be replaced by module, just trialing how it will be called.
class vcs:
    class add:
        def __init__(self, project_root_relative_path: str):
            self.path = project_root_relative_path

        def __call__(self, ctx: RunContext, file):
            ctx.vcs.add(path=self.path)

    class commit:
            def __init__(self, msg: str):
                self.commit_message = msg

            def __call__(self, ctx: RunContext, file):
                ctx.vcs.commit(self.commit_message)

    class run:
        def __init__(self, cmd: str):
            self.cmd = cmd

        def __call__(self, ctx: RunContext, file):
            ctx.vcs.run(self.cmd)


def test_replacing_text(tmp_local_project_factory):
    dir = tmp_local_project_factory(structure={
        "src": {
            "hello.txt": "hello world!",
        },
    })

    Automaton(
        name='impl1',
        config=Config.get_default(),
        projects=[
            Project(
                project_id='test_project',
                explorer=LocalFilesExplorer(
                    rootdir=dir, filter_by=ContainsFilter(contains='hello world')
                ),
            ),
        ],
        flow=TasksFlow([
            lol,
            # vcs.add()
        ],
        preprocess=[
            vcs.run('init')
        ],
        postprocess=[
            vcs.add("src/"),
        ]),
    ).run()

    assert 'src/hello.txt' in bash_execute(f"git -C {dir} status")

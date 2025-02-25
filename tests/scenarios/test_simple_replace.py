from automyte.automaton.base import *

def lol(ctx: RunContext, file: File):
    import re
    file.edit(re.sub(r"world", "there", file.get_contents()))


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
                    rootdir=dir,
                    filter_by=ContainsFilter(contains='hello world')
                ),
            ),
        ],
        flow=TasksFlow([lol]),
    ).run()

    with open(f'{dir}/src/hello.txt', 'r') as f:
        assert f.read() == 'hello there!'

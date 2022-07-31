import io
import re

from h5tree import main

import h5py
import numpy as np

# https://stackoverflow.com/a/38662876
ANSI_ESCAPE = re.compile(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")


def test_h5tree() -> None:
    x = np.random.random([5, 5, 3])
    filename = "data.h5"
    with h5py.File(filename, "w") as f:
        f["x"] = x
        f.attrs.create("name", "Sam")
        f.attrs.create("value", "105")
        f["group_1/x"] = np.sum(x, axis=0)
        f["group_1/y"] = np.sum(x**2, axis=0)
        f["group_2/x"] = np.sum(x, axis=0)
        f["group_2/y"] = np.sum(x**2, axis=0)

        f["group_1/group_1_sub/x"] = np.sum(x, axis=0)
        f["group_1/group_1_sub"].attrs.create("name", "Dan")

    with io.StringIO() as output:
        main(filename, "/", False, False, False, None, None, output)
        ref = """data.h5
├── group_1
│   ├── group_1_sub
│   │   └── x
│   ├── x
│   └── y
├── group_2
│   ├── x
│   └── y
└── x
"""
        res = ANSI_ESCAPE.sub("", output.getvalue())
        assert res == ref

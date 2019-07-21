# Pre-commit hooks

Please configure git to run pre-commit hooks. 

TL;DR: you just need to open a terminal and run

```bash
$ pip install pre-commit black
$ pre-commit install
```

This will enable git to run come checks before committing. 
If you want to know more on why you should run the hooks and why, 
continue reading  below. 

# Black

This projects uses the [Black code style and source formatter](https://github.com/python/black/blob/master/README.md).
Please run Black before each commit; you can do it either via
the (provided) git hooks, enabling them as described above, running it manually
from a terminal, or integrating it [with your IDE of choice](https://github.com/python/black/blob/master/README.md#editor-integration).

Note: for PyCharm, remember to mark the folder `minerva` as Sources Root. 
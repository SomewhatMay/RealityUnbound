### In `replit.nix` file
From deps, remove:
- `pkgs.replitPackages.prybar-python310`,
- `pkgs.replitPackages.stderred`

From env, remove:
- `PRYBAR_PYTHON_BIN`
- `STDERREDBIN`

Then, update all 4 occurrences of python versions (`11` instead of `10`)

### In `.replit` file
Delete the entire `[interpreter]` block, possibly lines 15-27  
Change `channel`, possibly on line 13, from `"stable-22_11"` to `"stable-23_05"`  
In `PYTHONPATH`, possibly on line 18, update the 2 occurrences of `3.10` to `3.11`  

### In venv folder
In `venv/lib` folder, rename folder `python3.10` to `python3.11`. This may take a while  
In `venv/include`, if there is one, rename folder `python3.10` to `python3.11`

### Refresh
Refresh, or reload the shell, and now your repl runs python 3.11, with a working *packages* tab
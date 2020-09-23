# my_casa_tools

A collection of functions to be executed in CASA to simplify various tasks.
These functions were tailored to my needs in a specific project but may serve as a template for others as well.

Documentation of the functions could be better but they are all simple in nature. Just have a look at the code to see what they do.

All functions in here are regular python functions, not CASA tasks. This is to run in a variety of CASA versions. Task need to be compiled for a specific CASA version and will generally not run in other versions.

NOTE: The casa_tools scripts must be executed instead of imported. Otherwise the CASA tasks and tools are not recognized in the casa_tools functions and they will not work.
This can be achieved by executing all available files:
```import glob
for f in glob.glob('/home/krieger/modules/my_casa_tools/*.py'):
    execfile(f)
```
This statement can also be added to the `~/.casa/init.py` startup script to be executed upon startup. Ideally, it should be wrapped in a try/except block.
```try:
    import glob
    for f in glob.glob('/home/krieger/modules/my_casa_tools/*.py'):
        execfile(f)
except:
    print("\x1b[0;31;40m !!! Could not run my_casa_tools.\x1b[0m")
```

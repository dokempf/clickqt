# Welcome to clickqt

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/dokempf/clickqt/ci.yml?branch=main)](https://github.com/dokempf/clickqt/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/clickqt/badge/)](https://clickqt.readthedocs.io/)

**This is currently under active development between myself and a group of students**

## What is `clickqt`?
`clickqt` is a python package which turns `click`'s CLIs into `Qt`-GUIs.
Effectively, it turns
```
Usage: example_cli greet [OPTIONS]

Options:
  --userinfo <TEXT INTEGER DATETIME>...
  --help                          Show this message and exit.
```
into

![test](readme_resources/clickqt_interface.png)


# Installation

The Python package `clickqt` can be installed from PyPI:

```
python -m pip install clickqt
```

## Development installation

If you want to contribute to the development of `clickqt`, we recommend
the following editable installation from this repository:

```
git clone git@github.com:dokempf/clickqt.git
cd clickqt
python -m pip install --editable .[tests]
```

Having done so, the test suite can be run using `pytest`:

```
python -m pytest
```

# Usage

![test](readme_resources/preview.gif)


`clickqt` is designed to allow two ways of usage:
  ## External
To use `clickqt` externally, you can run the entry point created by installing `clickqt`, called `clickqtfy`.
There are two ways to use this entry point:
- ```
  clickqtfy ENTRYPOINT
  ```
This way works if you have an installed entry point.
- ```
  clickqtfy ENTRYPOINT FUNCNAME
  ```
In cases where there is no installed entry point, you can use this method instead, providing a path/filename for ENTRYPOINT and a function name within that file for FUNCNAME.

## Wrapper with Entry Point <a name="wrapper_with_entry_point"></a>
You can create entry points for `clickqt` in two steps:
* Create the control for the GUI as a variable (in a file named `somefile.py` in the top-level directory of package `somepackage`):
  ``` python
  from clickqt import qtgui_from_click
  import click

  @click.command(...)
  def foo(...):
    pass

  ui_handle = qtgui_from_click(foo)
  ```
* Then reference `ui_handle` in the `gui_scripts` section of your `pyproject.toml` file like this:
  ``` python
  [project.gui-scripts]
  gui = "somepackage.somefile:ui_handle"
  ```
After installing, you can run this entry point by typing `gui` in your console, create a desktop shortcut linked to it, etc..

## Usage with gui information
If you decide to design your own click.type then it would be normally mapped to a simple Textfield, if you do not provide additional information in the form of a dictionary.
It is important to note that the behaviour you want to invoke must also be provided by you, since the Qt-Widgets have different kind of getter and setter functions. This means that aside from you desired Qt-Widget you have to pass the getter function and the setter function for the customized type in a tuple, while your customized type is the key of the dictionary.
```python
from clickqt import qtgui_from_click
  import click

  @click.command(...)
  def foo(...):
    pass

  def custom_getter(widget: "CustomWidget"):
    assert isinstance(widget.widget, QSpinBox)
    return widget.widget.value()


  def custom_setter(widget: "CustomWidget", val):
      widget.widget.setValue(val)

  ui_handle = qtgui_from_click(foo, {BasedIntParamType: (QSpinBox, custom_getter, custom_setter)})
```
This can be referenced externally via an option before the arguments:
```
clickqtfy --custom-gui [GUI] ENTRYPOINT
```
```
clickqtfy --custom-gui [GUI] ENTRYPOINT FUNCNAME
```
GUI in this case can be an entrypoint, created as described in [Wrapper with Entrypoint](#wrapper_with_entrypoint) or it is the ui_handle you used to create this entrypoint.
With this you can map your own click types to specific QtWidgets of your choice if this is your choice.
# Support
ClickQt also supports the click extension to structure options of click commands in option groups (https://click-option-group.readthedocs.io/en/latest/).
This extension is supported by generating collapsible sections for the option groups to see the structuring of the options.
# Limitations

Currently clickqt only supports the built-in features from click.
This means that any user defined behaviour (e.g., custom ParamTypes / Commands / Contexts) will propably not work as expected.
Furthermore, clickqt handles envvar options diffently from click.
In particular clickqt always splits the envvar whereas click does this dependent on the ParamType.
Future releases will take these issues into account. In the current stage of clickQt the special cases of option groups are not supported i.e MutuallyExclusiveOptionGroup (https://click-option-group.readthedocs.io/en/latest/tutorial.html#behavior-and-relationship-among-options).

# Acknowledgments

This repository was set up using the [SSC Cookiecutter for Python Packages](https://github.com/ssciwr/cookiecutter-python-package).

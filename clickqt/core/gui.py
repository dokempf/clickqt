import click
from clickqt.widgets.multivaluewidget import MultiValueWidget
from PySide6.QtWidgets import QApplication, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QSizePolicy
from PySide6.QtGui import QColor, Qt
from clickqt.widgets.basewidget import BaseWidget
from clickqt.widgets.checkbox import CheckBox
from clickqt.widgets.textfield import TextField
from clickqt.widgets.passwordfield import PasswordField
from clickqt.widgets.numericfields import IntField, RealField
from clickqt.widgets.combobox import ComboBox, CheckableComboBox
from clickqt.widgets.datetimeedit import DateTimeEdit
from clickqt.widgets.tuplewidget import TupleWidget
from clickqt.widgets.filepathfield import FilePathField
from clickqt.widgets.filefield import FileField
from clickqt.widgets.nvaluewidget import NValueWidget
from clickqt.widgets.confirmationwidget import ConfirmationWidget
from clickqt.widgets.messagebox import MessageBox
from clickqt.core.output import OutputStream, TerminalOutput
import sys


class GUI:
    """ Responsible for setting up the components for the Qt-GUI that is used to navigate through the different kind of commands and their execution. """

    def __init__(self):
        self.window = QWidget()
        self.window.setLayout(QVBoxLayout())
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setChildrenCollapsible(False) # Child widgets can't be resized down to size 0
        self.window.layout().addWidget(self.splitter)
        
        self.widgets_container:QWidget = None # Control constructs this Qt-widget
        
        self.buttons_container = QWidget()
        self.buttons_container.setLayout(QHBoxLayout())
        self.buttons_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed) # Not resizable in vertical direction
        self.run_button = QPushButton("&Run")  # Shortcut Alt+R
        self.stop_button = QPushButton("&Stop")  # Shortcut Alt+S
        self.stop_button.setEnabled(False)
        self.buttons_container.layout().addWidget(self.run_button)
        self.buttons_container.layout().addWidget(self.stop_button)
        
        self.terminal_output = TerminalOutput()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setToolTip("Terminal output")
        self.terminal_output.newHtmlMessage.connect(self.terminal_output.writeHtml)

        sys.stdout = OutputStream(self.terminal_output, sys.stdout)
        sys.stderr = OutputStream(self.terminal_output, sys.stderr, QColor("red"))

    def __call__(self):
        """Shows the GUI-window"""

        self.window.show()
        QApplication.instance().exec()

    def construct(self):
        assert self.widgets_container is not None

        self.splitter.addWidget(self.widgets_container)
        self.splitter.addWidget(self.buttons_container)
        self.splitter.addWidget(self.terminal_output)

    def createWidget(self, otype:click.ParamType, param:click.Parameter, **kwargs) -> BaseWidget:
        """Creates the clickqt widget object of the correct widget class determined by the **otype** and returns it.
        
        :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
        :param param: The parameter from which **otype** came from
        :param kwargs: Additionally parameters ('widgetsource', 'parent', 'com') needed for :class:`~clickqt.widgets.basewidget.MultiWidget`-widgets
        """

        typedict = {
            click.types.BoolParamType: MessageBox if hasattr(param, "is_flag") and param.is_flag and hasattr(param, "prompt") and param.prompt else CheckBox,
            click.types.IntParamType: IntField,
            click.types.FloatParamType: RealField,
            click.types.StringParamType: PasswordField if hasattr(param, "hide_input") and param.hide_input else TextField,
            click.types.UUIDParameterType: TextField,
            click.types.UnprocessedParamType: TextField,
            click.types.DateTime: DateTimeEdit,
            click.types.Tuple: TupleWidget,
            click.types.Choice: ComboBox,
            click.types.Path: FilePathField,
            click.types.File: FileField
        }

        def get_multiarg_version(otype:click.ParamType):
            if isinstance(otype, click.types.Choice):
                return CheckableComboBox
            return NValueWidget

        if hasattr(param, "confirmation_prompt") and param.confirmation_prompt:
            return ConfirmationWidget(otype, param, **kwargs)
        if param.multiple:
            return get_multiarg_version(otype)(otype, param, **kwargs)
        if param.nargs > 1:
            if isinstance(otype, click.types.Tuple):
                return TupleWidget(otype, param, **kwargs)
            return MultiValueWidget(otype, param, **kwargs)

        for t, widgetclass in typedict.items():
            if isinstance(otype, t):
                return widgetclass(otype, param, **kwargs)
            
        return TextField(otype, param, **kwargs) # Custom types are mapped to TextField
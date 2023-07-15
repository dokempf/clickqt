from typing import Any
from PySide6.QtWidgets import QMessageBox, QWidget
from clickqt.core.error import ClickQtError
from clickqt.widgets.basewidget import BaseWidget
from click import Parameter, ParamType, Context

class MessageBox(BaseWidget):
    """Represents clicks Yes-Parameter that asks a user for confirmation. This widget is a confirmation dialog which does not 
    appear in the GUI, but pops up one step before execution the command. 
    
    :param otype: The type which specifies the clickqt widget type. This type may be different compared to **param**.type when dealing with click.types.CompositeParamType-objects
    :param param: The parameter from which **otype** came from
    :param kwargs: Additionally parameters ('parent', 'widgetsource', 'com', 'label') needed for 
                    :class:`~clickqt.widgets.basewidget.MultiWidget`- / :class:`~clickqt.widgets.confirmationwidget.ConfirmationWidget`-widgets
    """

    widget_type = QWidget #: The Qt-type of this widget. Its just a container for storing the messagebox.

    def __init__(self, otype:ParamType, param:Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

        assert hasattr(param, "is_flag") and param.is_flag, "'param.is_flag' should be True" 
        assert hasattr(param, "prompt") and param.prompt, "'param.prompt' should be not empty"

        self.yes:bool = False #: Confirmation of the user, defaults to False

        if self.parent_widget is None:
            self.setValue(BaseWidget.getParamDefault(param, False))

        self.layout.removeWidget(self.label)
        self.layout.removeWidget(self.widget)
        self.label.deleteLater()
        self.container.deleteLater()
        self.container = self.widget
        self.container.setVisible(False)

    def setValue(self, value:Any):
        self.yes = bool(self.type.convert(str(value), self.click_command, Context(self.click_command)))
    
    def getValue(self) -> tuple[Any, ClickQtError]:
        """Opens a confirmation dialog, passes the decision to :func:`~clickqt.widgets.basewidget.BaseWidget.getValue` 
        and returns the result. See also :func:`~clickqt.widgets.messagebox.MessageBox.getWidgetValue`

        :return: Valid: (widget value or the value of a callback, :class:`~clickqt.core.error.ClickQtError.ErrorType.NO_ERROR`)\n
                 Invalid: (None, :class:`~clickqt.core.error.ClickQtError.ErrorType.CONVERTING_ERROR` or 
                 :class:`~clickqt.core.error.ClickQtError.ErrorType.PROCESSING_VALUE_ERROR`)
        """

        if QMessageBox.information(self.widget, "Confirmation", str(self.param.prompt), 
                                   QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            self.yes = True
        else:
            self.yes = False
        
        return super().getValue()
    
    def getWidgetValue(self) -> bool:
        """Returns the user-decision of the confirmation dialog.
        
        :return: True: The user clicked on the "Yes"-button\n
                 False: The user clicked on the "No"-button
        """

        return self.yes
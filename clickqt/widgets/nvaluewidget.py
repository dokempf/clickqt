from PySide6.QtWidgets import QVBoxLayout, QScrollArea, QPushButton, QWidget
from PySide6.QtCore import Qt
from clickqt.widgets.basewidget import BaseWidget, MultiWidget
from typing import Any, Callable, Optional, Iterable, Tuple
from clickqt.core.error import ClickQtError
from click import Context, Parameter, ParamType, Choice


class NValueWidget(MultiWidget):
    widget_type = QScrollArea
    
    def __init__(self, otype:ParamType, param:Parameter, widgetsource:Callable[[Any], BaseWidget], parent:Optional[BaseWidget]=None, **kwargs):
        super().__init__(otype, param, parent=parent, **kwargs)

        assert not isinstance(otype, Choice), f"'otype' is of type '{Choice}', but there is a better version for this type"
        assert param.multiple, "'param.multiple' should be True"

        self.widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.optkwargs = kwargs
        self.widgetsource = widgetsource
        self.vbox = QWidget()
        self.vbox.setLayout(QVBoxLayout())
        self.widget.setWidgetResizable(True)
        addfieldbtn = QPushButton("+", self.widget)
        addfieldbtn.clicked.connect(lambda: self.addPair()) # Add an empty widget
        self.vbox.layout().addWidget(addfieldbtn)
        self.widget.setWidget(self.vbox)
        self.buttondict:dict[QPushButton, BaseWidget] = {}

        self.children = self.buttondict.values()

        self.init()
        
    def addPair(self, value:Any=None):
        if len(self.children) == 0:
            self.handleValid(True)

        self.param.multiple = False # nargs cannot be nested, so it is safe to turn this off for children
        clickqtwidget:BaseWidget = self.widgetsource(self.type, self.param, widgetsource=self.widgetsource, parent=self, **self.optkwargs)
        self.param.multiple = True # click needs this for a correct conversion
        if value is not None:
            clickqtwidget.setValue(value)
        clickqtwidget.layout.removeWidget(clickqtwidget.label)
        clickqtwidget.label.deleteLater()
        removebtn = QPushButton("-", clickqtwidget.widget)
        clickqtwidget.layout.addWidget(removebtn)
        removebtn.clicked.connect(lambda: self.removeButtonPair(removebtn))
        self.vbox.layout().addWidget(clickqtwidget.container)
        self.buttondict[removebtn] = clickqtwidget
        self.widget.setWidget(self.vbox)
    
    def removeButtonPair(self, btntoremove):
        if btntoremove in self.buttondict:
            cqtwidget = self.buttondict.pop(btntoremove)
            self.vbox.layout().removeWidget(cqtwidget.container)
            cqtwidget.layout.removeWidget(cqtwidget.widget)
            cqtwidget.container.deleteLater()
            btntoremove.deleteLater()
            QScrollArea.updateGeometry(self.widget)

    def getValue(self) -> Tuple[Any, ClickQtError]:
        value_missing = False
        if len(self.children) == 0:
            default = BaseWidget.getParamDefault(self.param, None)

            if self.param.required and default is None:
                self.handleValid(False)
                return (None, ClickQtError(ClickQtError.ErrorType.REQUIRED_ERROR, self.widget_name, self.param.param_type_name))
            elif (envvar_values := self.param.value_from_envvar(Context(self.click_command))) is not None:
                for ev in envvar_values:
                    self.addPair(ev)
            elif default is not None: # Add new pairs
                for value in default: # All defaults will be considered if len(self.children)) == 0
                    self.addPair(value)
            else: # param is not required and there is no default -> value is None
                value_missing = True # But callback should be considered

        values:Optional[Iterable] = None
        
        if not value_missing:
            values = []
            err_messages:list[str] = []
            default = BaseWidget.getParamDefault(self.param, None)

            # len(self.children)) < len(default): We set at most len(self.children)) defaults
            # len(self.children)) >= len(default): All defaults will be considered
            for i, child in enumerate(self.children):
                try: # Try to convert the provided value into the corresponding click object type
                    if child.isEmpty():
                        if child.param.required and default is None:
                            self.handleValid(False)
                            return (None, ClickQtError(ClickQtError.ErrorType.REQUIRED_ERROR, child.widget_name, child.param.param_type_name))
                        elif default is not None and i < len(default): # Overwrite the empty widget with the default value (if one exists)
                            child.setValue(default[i]) # If the widget is a tuple, all values will be overwritten
                        else: # No default exists -> Don't consider the value of this child
                            # We can't remove the child because there would be a problem with out-of-focus-validation when
                            # having multiple string based widgets (the validator would remove the widget before all child-widgets could be filled)
                            continue
                            
                    values.append(self.type.convert(value=child.getWidgetValue(), param=self.param, ctx=Context(self.click_command))) 
                    child.handleValid(True)
                except Exception as e:
                    child.handleValid(False)
                    err_messages.append(str(e))
                
            if len(err_messages) > 0: # Join all error messages and return them
                messages = ", ".join(err_messages) 
                return (None, ClickQtError(ClickQtError.ErrorType.CONVERTING_ERROR, self.widget_name, messages if len(err_messages) == 1 else messages.join(["[", "]"])))
            
            if len(values) == 0: # All widgets are empty
                values = None

        return self.handleCallback(values)

    def setValue(self, value:Iterable[Any]):
        if len(value) < len(self.children): # Remove pairs
            for btns in list(self.buttondict.keys())[len(value):]:   
                self.removeButtonPair(btns)  
        if len(value) > len(self.children): # Add pairs
            for i in range(len(value)-len(self.children)):   
                self.addPair()
        
        for i,c in enumerate(self.children): # Set the value
            c.setValue(value[i])

    def handleValid(self, valid:bool):
        if len(self.children) == 0:
            BaseWidget.handleValid(self, valid)
        else:
            super().handleValid(valid)
    
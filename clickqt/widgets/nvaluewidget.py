import click
from PySide6.QtWidgets import QVBoxLayout, QScrollArea, QPushButton, QWidget
from PySide6.QtCore import Qt
from clickqt.widgets.base_widget import BaseWidget
from clickqt.core.error import ClickQtError
from click import Parameter
from typing import Any, Callable

class NValueWidget(BaseWidget):
    widget_type = QScrollArea
    
    def __init__(self, options, widgetsource:Callable[[Any], BaseWidget], parent: BaseWidget = None, *args, **kwargs):
        super().__init__(options, parent, *args, **kwargs)
        self.widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy(0x2))
        self.options = options
        self.optargs = args
        self.optkwargs = kwargs
        self.optiontype = self.click_object.type
        self.widgetsource = widgetsource
        self.vbox = QWidget()
        self.vbox.setLayout(QVBoxLayout())
        self.widget.setWidgetResizable(True)
        addfieldbtn = QPushButton("+", self.widget)
        addfieldbtn.clicked.connect(self.add_empty_pair)
        self.vbox.layout().addWidget(addfieldbtn)
        self.widget.setWidget(self.vbox)
        self.buttondict:dict[QPushButton, BaseWidget] = dict()
    
    def add_empty_pair(self):
        self.click_object.multiple = False # nargs cannot be nested, so it is safe to turn this off for children
        clickqtwidget:BaseWidget = self.widgetsource(self.optiontype, self.options, *self.optargs, widgetsource=self.widgetsource, parent=self, **self.optkwargs)
        self.click_object.multiple = True # click needs this for a correct conversion
        clickqtwidget.label.deleteLater()
        removebtn = QPushButton("-", clickqtwidget.widget)
        listentry = QWidget()
        listentry.setLayout(QVBoxLayout())
        listentry.layout().addWidget(removebtn)
        listentry.layout().addWidget(clickqtwidget.container)
        removebtn.clicked.connect(lambda: self.remove_button_pair(removebtn))
        self.vbox.layout().addWidget(listentry)
        self.buttondict[removebtn] = clickqtwidget
        self.widget.setWidget(self.vbox)
    
    def remove_button_pair(self, btntoremove):
        if btntoremove in self.buttondict:
            cqtwidget = self.buttondict[btntoremove]
            self.buttondict.pop(btntoremove)
            cqtwidget.widget.deleteLater()
            btntoremove.deleteLater()

    def handleValid(self, valid: bool):
        for c in self.buttondict.values():
            BaseWidget.handleValid(c, valid)

    def setValue(self, value):
        assert len(value) == len(self.children)
        for i,c in enumerate(self.children):
            c.setValue(value[i])
    
    def getWidgetValue(self) -> list[Any]:
        return [c.getWidgetValue() for c in self.buttondict.values()]
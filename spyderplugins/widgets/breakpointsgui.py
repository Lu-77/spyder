# -*- coding: utf-8 -*-
#
# Copyright © 2012 Jed Ludlow
# based loosley on pylintgui.py by Pierre Raybaut
# Licensed under the terms of the MIT License
# (see spyderlib/__init__.py for details)

"""Breakpoint widget"""

# pylint: disable=C0103
# pylint: disable=R0903
# pylint: disable=R0911
# pylint: disable=R0201

from __future__ import with_statement

from spyderlib.qt.QtGui import (QWidget, QTableView, QItemDelegate,
                                QVBoxLayout)
from spyderlib.qt.QtCore import (Qt, SIGNAL, QTextCodec,
                                 QModelIndex, QAbstractTableModel)
locale_codec = QTextCodec.codecForLocale()
from spyderlib.qt.compat import to_qvariant
import sys
import os.path as osp

# Local imports
from spyderlib.baseconfig import get_translation
from spyderlib.config import CONF

_ = get_translation("p_breakpoints", dirname="spyderplugins")

class BreakpointTableModel(QAbstractTableModel):
    """
    Table model for breakpoints dictionary
    
    """
    def __init__(self, parent, data):
        QAbstractTableModel.__init__(self, parent)
        if data is None:
            data = {}
        self._data = None
        self.breakpoints = None
        self.set_data(data)    
    
    def set_data(self, data):
        """Set model data"""
        self._data = data
        keys = data.keys()
        self.breakpoints = []
        for key in keys:
            bp_list = data[key]
            if bp_list:
                for item in data[key]:
                    self.breakpoints.append((key, item[0], item[1], ""))
        self.reset()   
    
    def rowCount(self, qindex=QModelIndex()):
        """Array row number"""
        return len(self.breakpoints)
    
    def columnCount(self, qindex=QModelIndex()):
        """Array column count"""
        return 4

    def sort(self, column, order=Qt.DescendingOrder):
        """Overriding sort method"""
        if column == 0:
            self.breakpoints.sort(
                key=lambda breakpoint: breakpoint[1])
            self.breakpoints.sort(
                key=lambda breakpoint: osp.basename(breakpoint[0]))
        elif column == 1:
            pass
        elif column == 2:
            pass
        elif column == 3:
            pass
        self.reset()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Overriding method headerData"""
        if role != Qt.DisplayRole:
            return to_qvariant()
        i_column = int(section)
        if orientation == Qt.Horizontal:
            headers = (_("File"), _("Line"), _("Condition"), "")
            return to_qvariant( headers[i_column] )
        else:
            return to_qvariant()
    
    def get_value(self, index):
        """Return current value"""
        return self.breakpoints[index.row()][index.column()] 
    
    def data(self, index, role=Qt.DisplayRole):
        """Return data at table index"""
        if not index.isValid():
            return to_qvariant()
        if role == Qt.DisplayRole:
            if index.column() == 0:
                value = osp.basename(self.get_value(index))
                return to_qvariant(value)
            else:
                value = self.get_value(index)
                return to_qvariant(value)
        elif role == Qt.TextAlignmentRole:
            return to_qvariant(int(Qt.AlignLeft|Qt.AlignVCenter))
        elif role == Qt.ToolTipRole:
            if index.column() == 0:
                value = self.get_value(index)
                return to_qvariant(value)
            else:
                return to_qvariant()
    
class BreakpointDelegate(QItemDelegate):
    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)

class BreakpointTableView(QTableView):
    def __init__(self, parent, data):
        QTableView.__init__(self, parent)
        self.model = BreakpointTableModel(self, data)
        self.setModel(self.model)
        self.delegate = BreakpointDelegate(self)
        self.setItemDelegate(self.delegate)

        self.setup_table()
        
    def setup_table(self):
        """Setup table"""
        self.horizontalHeader().setStretchLastSection(True)
        self.adjust_columns()
        self.columnAt(0)
        # Sorting columns
        self.setSortingEnabled(False)
        self.sortByColumn(0, Qt.DescendingOrder)
    
    def adjust_columns(self):
        """Resize three first columns to contents"""
        for col in range(3):
            self.resizeColumnToContents(col)    
    
    def mouseDoubleClickEvent(self, event):
        """Reimplement Qt method"""
        index_clicked = self.indexAt(event.pos())
        filename = self.model.breakpoints[index_clicked.row()][0]
        line_number_str = self.model.breakpoints[index_clicked.row()][1]
        self.parent().emit(SIGNAL("edit_goto(QString,int,QString)"),
                           filename, int(line_number_str), '')   

class BreakpointWidget(QWidget):
    """
    Breakpoint widget
    """
    VERSION = '1.0.0'
    
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        
        self.setWindowTitle("Breakpoints")        
        self.dictwidget = BreakpointTableView(self, 
                               self._load_all_breakpoints())
        layout = QVBoxLayout()
        layout.addWidget(self.dictwidget)
        self.setLayout(layout)
    
    def _load_all_breakpoints(self):
        bp_dict = CONF.get('run', 'breakpoints', {})
        for filename in bp_dict.keys():
            if not osp.isfile(filename):
                bp_dict.pop(filename)
        return bp_dict    
    
    def get_data(self):
        pass
        
    def set_data(self):
        bp_dict = self._load_all_breakpoints()
        self.dictwidget.model.set_data(bp_dict)
        self.dictwidget.adjust_columns()
        self.dictwidget.sortByColumn(0, Qt.DescendingOrder)

def test():
    """Run breakpoint widget test"""
    from spyderlib.utils.qthelpers import qapplication
    app = qapplication()
    widget = BreakpointWidget(None)
    widget.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    test()

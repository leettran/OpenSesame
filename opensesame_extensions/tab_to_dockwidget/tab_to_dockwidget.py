# coding=utf-8

"""
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""

from libopensesame.py3compat import *
from libqtopensesame.extensions import base_extension
from tab_to_dockwidget_docktab import DockTab
from qtpy import QtCore


class tab_to_dockwidget(base_extension):

	"""
	desc:
		This extensions turns tabs into standalone dockwidgets, so that you can
		see multiple things side by side.
	"""

	def event_startup(self):

		"""
		desc:
			During initialization we monkey-patch the tabwidget so that it also
			manages dockwidgets.
		"""

		self._docktabs = {}
		self.tabwidget.add = self._add_tab(self.tabwidget.add)
		self.tabwidget.remove = self._remove_tab(self.tabwidget.remove)
		self.tabwidget.close_all = self._close_all_tabs(self.tabwidget.close_all)

	def activate(self):

		"""
		desc:
			Turns the currently visible tab (if any) into a dockwidget.
		"""

		widget = self.tabwidget.currentWidget()
		if widget is None:
			return
		name = self.tabwidget.tabText(self.tabwidget.currentIndex())
		self.tabwidget.remove(widget)
		docktab = DockTab(self, widget, name)
		self._docktabs[widget] = docktab
		self.main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, docktab)

	def remove_widget(self, widget):

		"""
		desc:
			Removes a docked widget.
		"""

		if widget in self._docktabs:
			del self._docktabs[widget]

	def _close_all_tabs(self, fnc):

		"""
		desc:
			Decorates tabwidget.close_all()
		"""

		def inner(*args, **kwargs):

			while self._docktabs:
				widget, docktab = self._docktabs.popitem()
				docktab.close()
			return fnc(*args, **kwargs)

		return inner

	def _add_tab(self, fnc):

		"""
		desc:
			Decorates tabwidget.add()
		"""

		def inner(widget, *args, **kwargs):

			if widget in self._docktabs:
				if hasattr(widget, u'set_focus'):
					widget.set_focus()
				return
			return fnc(widget, *args, **kwargs)

		return inner

	def _remove_tab(self, fnc):

		"""
		desc:
			Decorates tabwidget.remove()
		"""

		def inner(widget, *args, **kwargs):

			if widget in self._docktabs:
				docktab = self._docktabs.pop(widget)
				docktab.close()
				return
			return fnc(widget, *args, **kwargs)

		return inner

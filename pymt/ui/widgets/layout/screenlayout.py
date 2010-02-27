__all__ = ('MTScreenLayout', )

from abstractlayout import MTAbstractLayout
from boxlayout import MTBoxLayout
from ....logger import pymt_logger
from ....utils import SafeList, curry
from ....base import getFrameDt
from ....graphx import set_color, drawRectangle
from ...factory import MTWidgetFactory
from ..button import MTButton


class MTScreenLayout(MTAbstractLayout):
    '''Base class to handle a list of screen (widgets).
    One child widget is shown at a time.

    :Parameters:
        `show_tabs`: bool, default to False
            If True, show tabs (useful for debugging)
        `duration`: float, default to 1.
            Duration to switch between screen

    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('show_tabs', False)
        kwargs.setdefault('duration', 1.)
        super(MTScreenLayout, self).__init__(**kwargs)
        self.screens = SafeList()
        self.screen = None
        self.previous_screen = None
        self._switch_t = 1.1
        self.duration = kwargs.get('duration')

        self.container = MTBoxLayout(orientation='vertical')
        super(MTScreenLayout, self).add_widget(self.container)

        self.tabs = self.new_tab_layout()
        self._show_tabs = False
        self.show_tabs = kwargs.get('show_tabs')

    def _get_show_tabs(self):
        return self._show_tabs
    def _set_show_tabs(self, set):
        if self._show_tabs and set is False:
            self.container.remove_widget(self.tabs)
        if set and self._show_tabs is False:
            self.container.add_widget(self.tabs)
        self._show_tabs = set
    show_tabs = property(_get_show_tabs, _set_show_tabs)


    def new_tab_layout(self):
        '''called in init, to create teh layout in which all teh tabs are put.  overwrite to create custom tab layout
        (default is box layout, vertical, height=50, with horizontal stretch.)'''
        return MTBoxLayout(size_hint=(1.0,None), height=50)

    def new_tab(self, label):
        '''fucntion that returns a new tab.  return value must be of type MTButton or derive from it (must have on_press handler).
        Screenlayuot subclasses can overwrite this to create tabs based ona tehir own look and feel or do otehr custom things when a new tab is created'''
        return MTButton(label=label, size_hint=(1, 1), height=50)

    def add_widget(self, widget, tab_name=None):
        if tab_name:
            tab_btn = self.new_tab(tab_name)
            tab_btn.push_handlers(on_press=curry(self.select, widget))
            self.tabs.add_widget(tab_btn)
        self.screens.append(widget)

    def remove_widget(self, widget):
        for btn in self.tabs.children.iterate():
            if type(widget) in (str, unicode):
                if btn.label == widget:
                    self.tabs.remove_widget(btn)
                    break
            elif btn.label == widget.id:
                self.tabs.remove_widget(btn)
                break
        if widget in self.screens:
            self.screens.remove(widget)

    def select(self, id, *args):
        '''
        Select which screen is to be the current one.
        pass either a widget that has been added to this layout, or its id
        '''
        if self.screen is not None:
            self.container.remove_widget(self.screen)
            self.previous_screen = self.screen
            self._switch_t = -1.0
        for screen in self.screens:
            if screen.id == id or screen == id:
                self.screen = screen
                self.container.add_widget(self.screen, do_layout=True)
                self.screen.parent = self
                return
        pymt_logger.error('ScreenLayout: Invalid screen or screenname, doing nothing...')


    def draw_transition(self, t):
        '''
        Function is called each frame while switching screens and
        responsible for drawing transition state.
        t will go from -1.0 (previous screen), to 0 (rigth in middle),
        until 1.0 (last time called before giving new screen full controll)
        '''
        r,g,b,a = self.style['bg-color']
        if t < 0:
            if self.previous_screen is not None:
                self.previous_screen.dispatch_event('on_draw')
            set_color(r,g,b,1+t) #from 1 to zero
            drawRectangle(size=self.container.size)
        else:
            if self.previous_screen is not None:
                self.screen.dispatch_event('on_draw')
            set_color(r,g,b,1-t) #from 0 to one
            drawRectangle(pos=self.container.pos, size=self.container.size)

    def on_update(self):
        if not self.screen and len(self.screens):
            self.select(self.screens[0])
        super(MTScreenLayout, self).on_update()

    def on_draw(self):
        self.draw()
        if self._switch_t < 1.0:
            if self.duration == 0:
                self._switch_t = 1.
            else:
                self._switch_t += getFrameDt() / self.duration
            self.draw_transition(self._switch_t)
        else:
            super(MTScreenLayout, self).on_draw()


# Register all base widgets
MTWidgetFactory.register('MTScreenLayout', MTScreenLayout)
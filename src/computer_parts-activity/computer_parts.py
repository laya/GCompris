#  gcompris - computer_parts.py
#
# Copyright (C) 2003, 2008 Bruno Coudoin
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# computer_parts activity.
import gtk
import gtk.gdk
import gcompris
import gcompris.utils
import gcompris.skin
import gcompris.bonus
import gcompris.sound
import goocanvas
import pango
import ConfigParser
import random

from gcompris import gcompris_gettext as _

#
# The name of the class is important. It must start with the prefix
# 'Gcompris_' and the last part 'computer_parts' here is the name of
# the activity and of the file in which you put this code. The name of
# the activity must be used in your menu.xml file to reference this
# class like this: type="python:computer_parts"
#
class Gcompris_computer_parts:
  """Empty gcompris Python class"""


  def __init__(self, gcomprisBoard):
    print "computer_parts init"

    # Save the gcomprisBoard, it defines everything we need
    # to know from the core
    self.gcomprisBoard = gcomprisBoard
    self.gcomprisBoard.level = 1
    self.gcomprisBoard.maxlevel = 2
    self.gcomprisBoard.sublevel = 1
    self.gcomprisBoard.number_of_sublevel = 2
    self.win = False
    self.points = 0

    # Needed to get key_press
    gcomprisBoard.disable_im_context = True

    # context is to specify INTERNAL or EXTERNAL parts
    self.context = None
    self.EXTERNAL = range(1, 7)
    self.INTERNAL = range(7, 13)
    
    self.part_on_focus = None
    self.REVEAL = True
    self.HIDE = False

  def start(self):
    print "computer_parts start"

    self.part = None

    # Set the buttons we want in the bar
    gcompris.bar_set(gcompris.BAR_LEVEL)

    # Set a background image
    gcompris.set_default_background(self.gcomprisBoard.canvas.get_root_item())

    # Create our rootitem. We put each canvas item in it so at the end we
    # only have to kill it. The canvas deletes all the items it contains
    # automaticaly.
    self.rootitem = goocanvas.Group(parent =
                                    self.gcomprisBoard.canvas.get_root_item())

    self.read_data()
    self.render_level()

  def end(self):
    print "computer_parts end"
    # Remove the root item removes all the others inside it
    self.rootitem.remove()


  def ok(self):
    print("computer_parts ok.")


  def repeat(self):
    print("computer_parts repeat.")


  #mandatory but unused yet
  def config_stop(self):
    pass

  # Configuration function.
  def config_start(self, profile):
    print("computer_parts config_start.")

  def key_press(self, keyval, commit_str, preedit_str):
    utf8char = gtk.gdk.keyval_to_unicode(keyval)
    strn = u'%c' % utf8char

    print("Gcompris_computer_parts key press keyval=%i %s" % (keyval, strn))

  def pause(self, pause):
    print("computer_parts pause. %i" % pause)

  # Called by gcompris when the user clicks on level icons
  def set_level(self, level):
    print("computer_parts set level. %i" % level)
    self.gcomprisBoard.level = level
    self.gcomprisBOard.sublevel = 1
    self.next_level()

  def next_level_click(self, event, target, item):
    self.increment_level()

  def increment_level(self):
    self.gcomprisBoard.sublevel += 1

    if (self.gcomprisBoard.sublevel > self.gcomprisBoard.number_of_sublevel):
      self.gcomprisBoard.sublevel = 1
      self.gcomprisBoard.level += 1
      if (self.gcomprisBoard.level > self.gcomprisBoard.maxlevel):
        self.gcomprisBoard.level = 1

    self.render_level()

  def increment_points(self):
    self.points += 1
    if self.points == 6:
      self.win = True
      self.increment_level()


  def read_data(self):
    '''Load the activity data'''
    config = ConfigParser.RawConfigParser()
    p = gcompris.get_properties()
    filename = gcompris.DATA_DIR + '/' + self.gcomprisBoard.name + '/activity.desktop'
    try:
      gotit = config.read(filename)
      if not gotit:
        gcompris.utils.dialog(_("Cannot find the file '{filename}'").format(filename=filename), None)
        return False

    except ConfigParser.Error, error:
      gcompris.utils.dialog(_("Failed to parse data set '{filename}' with error:\n{error}").
        format(filename=filename, error=error), None)
      return False

    self.dataset = config
    return True


  # Draws explorer screen items
  def start_explorer(self):

    if (self.gcomprisBoard.level == 1):
      self.context = self.EXTERNAL
    else:
      self.context = self.INTERNAL

    gcompris.bar_location(660, -1, 0.5)

    ok = goocanvas.Svg(parent = self.rootitem,
                       svg_handle = gcompris.skin.svg_get(),
                       svg_id = "#OK",
                       tooltip = _("Next")
                       )
    ok.translate(150, -50)
    ok.connect("button_press_event", self.next_level_click)
    gcompris.utils.item_focus_init(ok, None)


    self.desc_tb = gtk.TextBuffer()
    self.desc_tv = gtk.TextView(self.desc_tb)
    self.desc_tv.set_editable(False)
    self.desc_tb.set_text(_("Mouse-over any part"))
    # self.desc_tb.set_font(gcompris.skin.get_font("gcompris/board/medium"))
    self.desc_tv.set_wrap_mode(gtk.WRAP_CHAR)

    self.widget = goocanvas.Widget(parent = self.rootitem,
                                   widget = self.desc_tv,
                                   x = 30,
                                   y = 400,
                                   width = 600,
                                   height = 100,
                                   anchor = gtk.ANCHOR_NW,
                                   )
    # self.desc_tv.show()

    self.render_parts()


  def render_parts(self):
    print "rendering called"

    self.part_pos_x = 100
    self.part_pos_y = 100

    if self.gcomprisBoard.sublevel == 2:
      self.part_on_focus = self.HIDE
    else:
      self.part_on_focus = self.REVEAL

    for i in self.context:
      name = str(self.dataset.get(str(i), "name"))
      desc = str(self.dataset.get(str(i), "desc"))
      img = str(self.dataset.get(str(i), "image"))
      Part(self, name, desc, img, self.part_pos_x, self.part_pos_y, self.part_on_focus)

      self.part_pos_x += 150
      if i == 3:
        self.part_pos_x = 100
        self.part_pos_y += 150


  def show_desc(self, desc):
    self.desc_tb.set_text(_(desc))


  def clear_desc(self):
    self.desc_tb.set_text(_("Mouse-over any part"))


  def start_game(self):
    print "THE GAME HAS STARTED"

    self.parts_list = self.context[:]
    random.shuffle(self.parts_list)
 
    if self.gcomprisBoard.level == 1:
      self.context = self.EXTERNAL
    else:
      self.context = self.INTERNAL

    self.render_parts()
    self.random_part()
    
    pass


  def render_level(self):
    if self.rootitem:
      self.rootitem.remove()

    self.rootitem = goocanvas.Group(parent = \
      self.gcomprisBoard.canvas.get_root_item())  

    if self.gcomprisBoard.sublevel == 1:
      self.start_explorer()
    else:
      self.points = 0
      self.start_game()

  def check(self, name):
    print "checking " + name 
    if self.part == name:
      self.increment_points()
      gcompris.sound.play_ogg("sounds/tuxok.wav")
      gcompris.bonus.display(gcompris.bonus.WIN, gcompris.bonus.TUX)
      self.random_part()
    else:
      gcompris.bonus.display(gcompris.bonus.LOOSE, gcompris.bonus.TUX)

  # Generate random part name.
  def random_part(self):
    print "points: " + str(self.points)
    print "level: " + str(self.gcomprisBoard.level)
    self.part = str(self.dataset.get(str(self.parts_list.pop()), "name"))
    print "random set as: " + self.part


class Part:
  # name is name of the part
  # desc is description about the part
  # img is the path to the image
  # x and y are position of the part
  def __init__(self, computer_parts, name, desc, img, x, y, on_focus):
    print "creating " + str(name)
    self.rootitem = computer_parts.rootitem
    self.image = gcompris.utils.load_pixmap(img)
    self.cp = computer_parts

    self.name = name
    self.desc = desc
    self.x = x
    self.y = y
    self.width = 100
    self.height = 100

    if name == "Keyboard":
      self.width = 200

    self.part_item = goocanvas.Image(parent = self.rootitem,
                                     pixbuf = self.image,
                                     x = self.x,
                                     y = self.y,
                                     width = self.width,
                                     height = self.height,
                                     )

    if on_focus:
      self.part_item.connect("enter_notify_event", self.show_desc, self)
      self.part_item.connect("leave_notify_event", self.clear_desc, self)
    else:
      self.part_item.connect("button_press_event", self.evaluate, self)

    gcompris.utils.item_focus_init(self.part_item, None)

  def show_desc(self, widget, target, event, item):
    self.cp.show_desc(self.desc)

  def clear_desc(self, widget, target, event, item):
    self.cp.clear_desc()

  def evaluate(self, widget, target, event, item):
    self.cp.check(self.name)

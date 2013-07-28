#  gcompris - stop_look_listen.py
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
# stop_look_listen activity.
import gobject
import gtk
import gtk.gdk
import gcompris
import gcompris.utils
import gcompris.skin
import gcompris.bonus
import gcompris.sound
import goocanvas
import ConfigParser
import pango
import random

from gcompris import gcompris_gettext as _

#
# The name of the class is important. It must start with the prefix
# 'Gcompris_' and the last part 'stop_look_listen' here is the name of
# the activity and of the file in which you put this code. The name of
# the activity must be used in your menu.xml file to reference this
# class like this: type="python:stop_look_listen"
#
class Gcompris_stop_look_listen:
  """Empty gcompris Python class"""


  def __init__(self, gcomprisBoard):
    print "stop_look_listen init"

    # Save the gcomprisBoard, it defines everything we need
    # to know from the core
    self.gcomprisBoard = gcomprisBoard
    self.gcomprisBoard.level = 1
    self.gcomprisBoard.maxlevel = 2

    self.dataset = None

    # Needed to get key_press
    # gcomprisBoard.disable_im_context = True

  def start(self):
    print "stop_look_listen start"
    self.learn = None
    self.drive = None

    # Create our rootitem. We put each canvas item in it so at the end we
    # only have to kill it. The canvas deletes all the items it contains
    # automaticaly.
    self.rootitem = goocanvas.Group(parent =
                                    self.gcomprisBoard.canvas.get_root_item())

    # Store Steering Wheel positions in a list
    self.steering_items = []
    self.steer_seq = [0,1,2,1,0,3,4,3]
    for i in self.steer_seq:
      self.steering_items.append("#STEERING_" + str(i))

    # Initialize reading from activity.desktop
    self.read_data()

    # Create Steering and Learning classes
    self.drive = Steering(self, self.steering_items)
    self.learn = Learning(self, self.dataset)

    self.render_level()

    gcompris.bar_set(gcompris.BAR_LEVEL)
    gcompris.bar_location(630, -1, 0.5)

        
  def end(self):
    print "stop_look_listen end"
    # Remove the root item removes all the others inside it
    self.rootitem.remove()


  def ok(self):
    print("stop_look_listen ok.")


  def repeat(self):
    print("stop_look_listen repeat.")


  #mandatory but unused yet
  def config_stop(self):
    pass

  # Configuration function.
  def config_start(self, profile):
    print("stop_look_listen config_start.")

  def key_press(self, keyval, commit_str, preedit_str):
    utf8char = gtk.gdk.keyval_to_unicode(keyval)
    strn = u'%c' % utf8char

    # print("Gcompris_stop_look_listen key press keyval=%i %s" % (keyval, strn))

  def pause(self, pause):
    print("stop_look_listen pause. %i" % pause)

  def set_level(self, level):
    print("stop_look_listen set level. %i" % level)
    self.gcomprisBoard.level = level
    self.render_level()

  def render_level(self):
    self.rootitem.remove()
    self.rootitem = goocanvas.Group(parent =
                                    self.gcomprisBoard.canvas.get_root_item())
 
    if self.gcomprisBoard.level == 1:
      self.learn.show(self.rootitem)
    else:
      self.drive.show(self.rootitem)

    gcompris.bar_set_level(self.gcomprisBoard)

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


# Learning class, for the learning signs
class Learning:
  def __init__(self, stop_look_listen, dataset):
    self.rootitem = stop_look_listen.rootitem
    self.main = stop_look_listen
    self.dataset = dataset
    self.desc_tv = None
    self.desc_tb = None

    self.sign = []
    for i in range(1, 21):
        self.sign.append("#SIGN_" + str(i))
 
    self.svghandle = gcompris.utils.load_svg("stop_look_listen/legend.svgz")

    self.show(self.rootitem)

  def show(self, rootitem):
    self.rootitem = rootitem
    self.bg = goocanvas.Svg(parent = self.rootitem,
                            svg_handle = self.svghandle,
                            svg_id = "#background",
                            pointer_events = goocanvas.EVENTS_NONE
                            )
    self.bg.lower(None)

    self.item = []

    for i in range(1, 21):
      name = str(self.dataset.get(str(i), "name"))
      desc = str(self.dataset.get(str(i), "desc"))
      label = str(self.dataset.get(str(i), "label"))

      Sign_item(self, name, desc, label)

    self.ok = goocanvas.Svg(parent = self.rootitem,
                            svg_handle = gcompris.skin.svg_get(),
                            svg_id = "#OK",
                            tooltip = _("Next")
                            )
    self.ok.translate(80, -130)
    self.ok.connect("button_press_event", self.next_level_click)
    gcompris.utils.item_focus_init(self.ok, None)

    # Border around the TextView
    self.border = goocanvas.Rect(parent = self.rootitem,
                                 x = 140,
                                 y = 190,
                                 width = 500,
                                 height = 110,
                                 stroke_color = "blue",
                                 line_width = 2.0
                                 )

    # Create a TextView with some text in it
    self.desc_tb = gtk.TextBuffer()
    self.desc_tv = gtk.TextView(self.desc_tb)
    self.desc_tv.set_editable(False)
    self.desc_tb.set_text(_("Mouse-over any part"))
    self.desc_tv.set_wrap_mode(gtk.WRAP_CHAR)

    self.widget = goocanvas.Widget(parent = self.rootitem,
                                   widget = self.desc_tv,
                                   x = 145,
                                   y = 195,
                                   width = 490,
                                   height = 100,
                                   anchor = gtk.ANCHOR_NW,
                                   )

  def show_desc(self, name, desc):
    self.desc_tb.set_text(_(name + '\n' + desc))

  def clear_desc(self):
    self.desc_tb.set_text(_("Mouse-over any sign"))

  def next_level_click(self, widget, target, event):
    self.main.gcomprisBoard.level += 1
    self.main.render_level()


# Sign_item class, class of each sign in the Learning board
class Sign_item:
  def __init__(self, learning, name, desc, label):
    self.learning = learning
    self.rootitem = learning.rootitem
    self.svghandle = learning.svghandle
    self.name = name
    self.desc = desc
    self.label = label
    self.show(self.rootitem)
    
  def show(self, rootitem):
    self.item = goocanvas.Svg(parent = self.rootitem,
                              svg_handle = self.svghandle,
                              svg_id = self.label,
                              visibility = goocanvas.ITEM_VISIBLE
                              )
    gcompris.utils.item_focus_init(self.item, None)
    self.item.connect("enter_notify_event", self.show_desc, self)
    self.item.connect("leave_notify_event", self.clear_desc, self)

  def show_desc(self, widget, target, event, item):
    self.learning.show_desc(self.name, self.desc)

  def clear_desc(self, widget, target, event, item):
    self.learning.clear_desc()
                              

# Steering wheel class, for second level
class Steering:
  def __init__(self, stop_look_listen, steeringitems):
    self.rootitem = stop_look_listen.rootitem
    self.pos = 0
    self.steeringitems = steeringitems
    self.timer = 0

    self.svghandle = gcompris.utils.load_svg("stop_look_listen/background.svgz")

    self.road = Road(self, self.svghandle)
    self.sign = Sign(self, self.svghandle)
    self.show(self.rootitem)

  # Create the Svg items on new rootitem
  def show(self, rootitem):
    self.rootitem = rootitem
    self.bg = goocanvas.Svg(parent = self.rootitem,
                            svg_handle = self.svghandle,
                            svg_id = "#BACKGROUND",
                            pointer_events = goocanvas.EVENTS_NONE
                            )
    self.bg.lower(None)

    self.steering = goocanvas.Svg(parent = self.rootitem,
                                  svg_handle = self.svghandle,
                                  svg_id = "#STEERING_0"
                                  )
   self.road.show(self.rootitem)
    self.sign.show(self.rootitem)

    self.ok = goocanvas.Svg(parent = self.rootitem,
                            svg_handle = gcompris.skin.svg_get(),
                            svg_id = "#OK",
                            tooltip = _("Next")
                            )
    self.ok.translate(80, -130)
    self.ok.connect("button_press_event", self.steering_event_on)
    gcompris.utils.item_focus_init(self.ok, None)

  # Handle event when steering wheel is clicked
  def steering_event_on(self, event, target, item):
    self.move = gobject.timeout_add(1000, self.render)
    self.ok.set_property("visibility", goocanvas.ITEM_INVISIBLE)
    self.road.start()

  # Render the steering wheel and show it moving
  # Also keep note of the time. At every 10 sec,
  # the steering should stop and reach the sign board
  def render(self):
    self.steering.set_property("svg_id",
                               self.steeringitems[self.pos])
    self.pos += 1
    if self.pos > 7:
      self.pos = 0 
    self.move = gobject.timeout_add(1000, self.render)
    self.timer += 1

    if self.timer == 10:
      gobject.source_remove(self.move)
      self.sign.show_stand()
      self.sign.show_sign()
      self.road.stop()
      self.timer = 0


class Road:
  def __init__(self, car, svghandle):
    self.rootitem = car.rootitem
    self.svghandle = svghandle
    self.state = 1
    self.timer = 0
    self.road = None
    self.show(self.rootitem)

  def show(self, rootitem):
    self.rootitem = rootitem
    self.road = goocanvas.Svg(parent = self.rootitem,
                              svg_handle = self.svghandle,
                              svg_id = "#ROAD_1"
                              )

  def start(self):
    self.move = gobject.timeout_add(500, self.update)

  def stop(self):
    gobject.source_remove(self.move)

  def update(self):
    if self.state == 1:
      self.road.set_property("svg_id", "#ROAD_2")
      self.state = 0
    elif self.state == 0:
      self.road.set_property("svg_id", "#ROAD_1")
      self.state = 1

    self.move = gobject.timeout_add(500, self.update)


class Sign:
  def __init__(self, car, svghandle):
    self.rootitem = car.rootitem
    self.svghandle = svghandle
    self.car = car

    self.stand = None
    self.signboard = None

    self.sign = None

    self.sign_items = []
    self.sign_seq = range(1, 21)
    for i in self.sign_seq:
      self.sign_items.append("#SIGN_" + str(i))

    self.sign_stack = self.sign_items[:]

    self.sign_dict = {"#SIGN_1": "No right turn",
                      "#SIGN_2": "National Truck Network Route",
                      "#SIGN_3": "Men at work",
                      "#SIGN_4": "Deer may cross the road at any time",
                      "#SIGN_5": "Slippery when wet",
                      "#SIGN_6": "Merging Lanes",
                      "#SIGN_7": "Camp Ahead",
                      "#SIGN_8": "Wrong Way",
                      "#SIGN_9": "Yield to Pedestrians",
                      "#SIGN_10": "Tow Away Zone",
                      "#SIGN_11": "Keep Right",
                      "#SIGN_12": "Stop",
                      "#SIGN_13": "Yield",
                      "#SIGN_14": "Bicycle Route",
                      "#SIGN_15": "No standing",
                      "#SIGN_16": "Added Lane",
                      "#SIGN_17": "Do Not Block Intersection",
                      "#SIGN_18": "Divided Highway",
                      "#SIGN_19": "Left Turn Yield on Green",
                      "#SIGN_20": "Do not Pass"
                      }

    self.question = Question(self, self.svghandle)

    self.show(self.rootitem)

  def show(self, rootitem):
    self.rootitem = rootitem
    self.stand = goocanvas.Svg(parent = self.rootitem,
                               svg_handle = self.svghandle,
                               svg_id = "#STAND",
                               visibility = goocanvas.ITEM_INVISIBLE
                               )

    self.signboard = goocanvas.Svg(parent = self.rootitem,
                                   svg_handle = self.svghandle,
                                   svg_id = self.sign_items[0],
                                   visibility = goocanvas.ITEM_INVISIBLE,
                                   )
    self.question.show(self.rootitem)

  def show_stand(self):
    self.stand.set_property("visibility", goocanvas.ITEM_VISIBLE)
    
  def hide_stand(self):
    self.stand.set_property("visibility", goocanvas.ITEM_INVISIBLE)
    
  def show_sign(self):
    if len(self.sign_stack) == 0:
      self.sign_stack = self.sign_items[:]
    random.shuffle(self.sign_stack)
    self.sign = self.sign_stack.pop()
    self.signboard.set_property("svg_id", self.sign)
    self.signboard.set_property("visibility", goocanvas.ITEM_VISIBLE)
    self.question.show_question(self.rootitem)

  def hide_sign(self):
    self.signboard.set_property("visibility", goocanvas.ITEM_INVISIBLE)


class Question:
  def __init__(self, sign, svghandle):
    self.rootitem = sign.rootitem
    self.svghandle = svghandle
    self.sign = sign 
    self.white = None
    self.quest = None
    self.show(self.rootitem)

  def show(self, rootitem):
    self.rootitem = rootitem
    self.white = goocanvas.Rect(parent = self.rootitem,
                                x = 80,
                                y = 70,
                                width = 500,
                                height = 200,
                                fill_color = "white",
                                visibility = goocanvas.ITEM_INVISIBLE
                                )

    self.quest = goocanvas.Text(parent = self.rootitem,
                                x = 200,
                                y = 80,
                                fill_color = "black",
                                text = "What is that signboard for?",
                                visibility = goocanvas.ITEM_INVISIBLE
                                )

  def answered(self, event, target, item, text):
    if text == self.sign.sign_dict[self.sign.sign]:
      gcompris.sound.play_ogg("sounds/tuxok.wav")
      gcompris.bonus.display(gcompris.bonus.WIN, gcompris.bonus.TUX)
      self.sign.car.render()
      self.sign.car.road.start()
      self.sign.hide_sign()
      self.sign.hide_stand()
      self.hide_question()
    else:
      gcompris.bonus.display(gcompris.bonus.LOOSE, gcompris.bonus.TUX)


  def show_question(self, rootitem):
    self.rootitem = rootitem
    self.white.set_property("visibility", goocanvas.ITEM_VISIBLE)
    self.quest.set_property("visibility", goocanvas.ITEM_VISIBLE)

    self.x = 100
    self.y = 130

    # Form the options.
    self.opt_text = [self.sign.sign_dict[self.sign.sign]]
    # Add other 3 unique options in the options list.
    for i in range(3):
      while True:
        temp = random.randrange(20)
        if self.sign.sign != self.sign.sign_items[temp]:
          self.opt_text.append(self.sign.sign_dict[self.sign.sign_items[temp]])
          break

    random.shuffle(self.opt_text)
    self.options = []
    self.opt_button = []
    for i in range(4):
      self.opt_button.append(goocanvas.Text(parent = self.rootitem,
                     x = self.x,
                     y = self.y,
                     width = 240,
                     fill_color = "green",
                     font = gcompris.skin.get_font("gcompris/subtitle"),
                     text = self.opt_text[i]
                     ))
      gcompris.utils.item_focus_init(self.opt_button[i], None)

      self.opt_button[i].connect("button_press_event",
                     self.answered, self.opt_text[i])

      if i == 1:
        self.x = 100
        self.y += 80
      else:
        self.x += 250

  def hide_question(self):
    self.quest.set_property("visibility", goocanvas.ITEM_INVISIBLE)
    self.white.set_property("visibility", goocanvas.ITEM_INVISIBLE)
    for i in range(4):
      self.opt_button[i].set_property("visibility", goocanvas.ITEM_INVISIBLE)

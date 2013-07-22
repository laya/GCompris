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

    # Needed to get key_press
    gcomprisBoard.disable_im_context = True

  def start(self):
    print "stop_look_listen start"

    # Set the buttons we want in the bar

    # Set a background image
    #gcompris.set_default_background(self.gcomprisBoard.canvas.get_root_item())

    self.timerinc = 20
    self.step_time = 100

    # Create our rootitem. We put each canvas item in it so at the end we
    # only have to kill it. The canvas deletes all the items it contains
    # automaticaly.
    self.rootitem = goocanvas.Group(parent =
                                    self.gcomprisBoard.canvas.get_root_item())

    self.svghandle = gcompris.utils.load_svg("stop_look_listen/background.svgz")
    # self.svghandle = gcompris.utils.load_svg("stop_look_listen/hydroelectric.svgz")
    self.bg = goocanvas.Svg(parent = self.rootitem,
                            svg_handle = self.svghandle,
                            svg_id = "#BACKGROUND",
                            pointer_events = goocanvas.EVENTS_NONE
                            )
    self.bg.lower(None)

    # Store Steering Wheels in a list
    self.steering_items = []
    self.steer_seq = [0,1,2,1,0,3,4,3]
    for i in self.steer_seq:
      self.steering_items.append("#STEERING_" + str(i))

    # Create Steering Wheel
    Steering(self, self.svghandle, self.steering_items)

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


class Steering:
  def __init__(self, stop_look_listen, svghandle, steeringitems):
    self.rootitem = stop_look_listen.rootitem
    self.pos = 0
    self.steeringitems = steeringitems
    self.svghandle = svghandle
    self.timer = 0

    self.steering = goocanvas.Svg(parent = self.rootitem,
                                  svg_handle = self.svghandle,
                                  svg_id = "#STEERING_0"
                                  )
    self.steering.connect("button_press_event",
                          self.steering_event_on)
    gcompris.utils.item_focus_init(self.steering, None)

    self.road = Road(self, self.svghandle)
    self.sign = Sign(self, self.svghandle)

  def steering_event_on(self, event, target, item):
    self.move = gobject.timeout_add(1000, self.render)
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
    self.state = 1
    self.timer = 0
    print "road created"

    self.road = goocanvas.Svg(parent = self.rootitem,
                              svg_handle = svghandle,
                              svg_id = "#ROAD"
                              )

  def start(self):
    print "road start moving"
    self.move = gobject.timeout_add(500, self.update)

  def stop(self):
    print "road stop moving"
    gobject.source_remove(self.move)

  def update(self):
    if self.state == 1:
      self.road.set_property("visibility", goocanvas.ITEM_INVISIBLE)
      self.state = 0
    elif self.state == 0:
      self.road.set_property("visibility", goocanvas.ITEM_VISIBLE)
      self.state = 1

    self.move = gobject.timeout_add(500, self.update)


class Sign:
  def __init__(self, car, svghandle):
    self.rootitem = car.rootitem
    self.car = car

    print "sign created"

    self.stand = goocanvas.Svg(parent = self.rootitem,
                               svg_handle = svghandle,
                               svg_id = "#STAND",
                               visibility = goocanvas.ITEM_INVISIBLE
                               )
    self.sign = None

    self.sign_items = []
    self.sign_seq = range(1, 21)
    print "sign_seq ", self.sign_seq
    for i in self.sign_seq:
      self.sign_items.append("#SIGN_" + str(i))

    self.sign_stack = self.sign_items[:]

    self.signboard = goocanvas.Svg(parent = self.rootitem,
                                   svg_handle = svghandle,
                                   svg_id = self.sign_items[0],
                                   visibility = goocanvas.ITEM_INVISIBLE,
                                   )

    '''
    self.cloud = goocanvas.Svg(parent = self.rootitem,
                               svg_handle = svghandle,
                               svg_id = "#CLOUD",
                               pointer_events = goocanvas.EVENTS_NONE,
                               visibility = goocanvas.ITEM_INVISIBLE
                               )
    '''
 
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

    self.question = Question(self, svghandle)

  def show_stand(self):
    self.stand.set_property("visibility", goocanvas.ITEM_VISIBLE)
    
  def hide_stand(self):
    self.stand.set_property("visibility", goocanvas.ITEM_INVISIBLE)
    
  def show_sign(self):
    if len(self.sign_stack) == 0:
      self.sign_stack = self.sign_items[:]
    random.shuffle(self.sign_stack)
    print "stack: ", self.sign_stack
    self.sign = self.sign_stack.pop()
    # self.sign = self.sign_items[temp]
    self.signboard.set_property("svg_id", self.sign)
    self.signboard.set_property("visibility", goocanvas.ITEM_VISIBLE)
    self.question.show()

  def hide_sign(self):
    self.signboard.set_property("visibility", goocanvas.ITEM_INVISIBLE)


class Question:
  def __init__(self, sign, svghandle):
    self.rootitem = sign.rootitem
    self.sign = sign 

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
      self.hide()
    else:
      gcompris.bonus.display(gcompris.bonus.LOOSE, gcompris.bonus.TUX)


  def show(self):
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
        print "comparing: ", self.sign.sign, " and ", self.sign.sign_items[temp]
        if self.sign.sign != self.sign.sign_items[temp]:
          self.opt_text.append(self.sign.sign_dict[self.sign.sign_items[temp]])
          break

    print "options :", self.opt_text
    random.shuffle(self.opt_text)
    print self.opt_text
    self.options = []
    self.opt_button = []
    for i in range(4):
      print self.x
      self.opt_button.append(goocanvas.Text(parent = self.rootitem,
                     x = self.x,
                     y = self.y,
                     width = 240,
                     fill_color = "green",
                     font = gcompris.skin.get_font("gcompris/subtitle"),
                     #anchor = gtk.ANCHOR_CENTER,
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


  def hide(self):
    self.quest.set_property("visibility", goocanvas.ITEM_INVISIBLE)
    self.white.set_property("visibility", goocanvas.ITEM_INVISIBLE)
    for i in range(4):
      self.opt_button[i].set_property("visibility", goocanvas.ITEM_INVISIBLE)

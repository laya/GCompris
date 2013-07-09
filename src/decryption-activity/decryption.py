#  gcompris - decryption.py
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
# decryption activity.
import gtk
import gtk.gdk
import gcompris
import gcompris.utils
import gcompris.skin
import gcompris.bonus
import gcompris.sound
import goocanvas
import pango
from key_value import *

from gcompris import gcompris_gettext as _

#
# The name of the class is important. It must start with the prefix
# 'Gcompris_' and the last part 'decryption' here is the name of
# the activity and of the file in which you put this code. The name of
# the activity must be used in your menu.xml file to reference this
# class like this: type="python:decryption"
#
class Gcompris_decryption:
  """Empty gcompris Python class"""


  def __init__(self, gcomprisBoard):
    print "decryption init"

    # Save the gcomprisBoard, it defines everything we need
    # to know from the core
    self.gcomprisBoard = gcomprisBoard
    self.gcomprisBoard.level = 1
    self.gcomprisBoard.maxlevel = 3
    self.gcomprisBoard.sublevel = 1
    self.gcomprisBoard.number_of_sublevel = 3
    self.won = False

    # The text entry for input
    self.entry = None

    # Parameters for different sublevels
    self.NUMBERS = 1
    self.SYMBOLS = 2
    self.ALPHABETS = 3
    self.VALUE = None

    # Needed to get key_press
    gcomprisBoard.disable_im_context = True

  def start(self):
    print "decryption start"

    self.wordlist = None

    try:
      self.language = gcompris.gcompris_gettext( gcompris.get_locale_name(gcompris.get_locale()) )
      self.wordlist = gcompris.get_wordlist("decryption/default-$LOCALE.xml")
    except:
      pass
    # Fallback to wordsgame list
    if not self.wordlist:
      try:
        self.language = gcompris.gcompris_gettext( gcompris.get_locale_name(gcompris.get_locale()) )
        self.wordlist = gcompris.get_wordlist("wordsgame/default-$LOCALE.xml")
      except:
        pass
    # Fallback to english
    if not self.wordlist:
      try:
        self.wordlist = gcompris.get_wordlist("decryption/default-en.xml")
        self.language = _("English")
      except:
        pass
    # Fallback to English wordsgame list
    if not self.wordlist:
      self.wordlist = gcompris.get_wordlist("wordsgame/default-en.xml")
      self.language = _("English")

    if not self.wordlist:
      gcompris.utils.dialog(_("Could not find the list of words."),
                            stop_board)
      return;

    # Create our rootitem. We put each canvas item in it so at the end we
    # only have to kill it. The canvas deletes all the items it contains
    # automaticaly.
    self.rootitem = goocanvas.Group(parent =
                                   self.gcomprisBoard.canvas.get_root_item())

    self.next_level()


  def end(self):
    print "decryption end"
    # Remove the root item removes all the others inside it
    self.rootitem.remove()


  def ok(self):
    print("decryption ok.")

  def repeat(self):
    print("decryption repeat.")
    self.next_level()

  #mandatory but unused yet
  def config_stop(self):
    pass

  # Configuration function.
  def config_start(self, profile):
    print("decryption config_start.")

  def key_press(self, keyval, commit_str, preedit_str):
    utf8char = gtk.gdk.keyval_to_unicode(keyval)
    strn = u'%c' % utf8char

    print strn

  def pause(self, pause):

    if ((pause == 0) and (self.won == True)):
      self.next_level()

    return


  def display_arrow(self):
    x_init = 40
    n = 26
    for i in range (0,n/2):
      goocanvas.Image(parent = self.rootitem,
                    pixbuf = gcompris.utils.load_pixmap("decryption/arrow.png"),
                    x = x_init,
                    y = 65,
                    )
      goocanvas.Image(parent = self.rootitem,
                    pixbuf = gcompris.utils.load_pixmap("decryption/arrow.png"),
                    x = x_init,
                    y = 155,
                    )
      x_init = x_init + 58

  # Called by gcompris when the user clicks on level icons
  def set_level(self, level):
    self.gcomprisBoard.level = level
    self.gcomprisBoard.sublevel = 1
    self.next_level()


  def increment_level(self):
    self.gcomprisBoard.sublevel += 1

    if(self.gcomprisBoard.sublevel > self.gcomprisBoard.number_of_sublevel):
      self.gcomprisBoard.sublevel = 1
      self.gcomprisBoard.level += 1
      if(self.gcomprisBoard.level > self.gcomprisBoard.maxlevel):
        self.gcomprisBoard.level = 1

    return 1

  # Receive entered text
  def entry_text(self):
    self.entry = gtk.Entry()

    self.entry.modify_font(pango.FontDescription("sans bold 25"))

    self.entry.set_max_length(len(self.word))
    self.entry.connect("activate", self.enter_callback)
    self.entry.connect("changed", self.enter_char_callback)

    self.entry.props.visibility = goocanvas.ITEM_VISIBLE

    self.widget = goocanvas.Widget(parent = self.rootitem,
                                   widget = self.entry,
                                   x = 275,
                                   y = 450,
                                   width = 300,
                                   height = 100,
                                   anchor = gtk.ANCHOR_CENTER,
                                   )

    self.widget.raise_(None)

    self.entry.grab_focus()

    return self.entry

  def enter_char_callback(self, widget):
    text = widget.get_text()
    widget.set_text(text.decode('utf8').upper().encode('utf8'))

  def enter_callback(self, widget):
    text = widget.get_text()

    if (self.word.upper() == text):
      self.won = True
      self.increment_level()
      gcompris.sound.play_ogg("sounds/tuxok.wav")
      gcompris.bonus.display(gcompris.bonus.WIN, gcompris.bonus.TUX)
    else:
      gcompris.bonus.display(gcompris.bonus.LOOSE, gcompris.bonus.TUX)

    widget.set_text('')

  # Place background image and control bar
  def base_setup(self):
    gcompris.set_background(self.gcomprisBoard.canvas.get_root_item(), "decryption/background.png")
    gcompris.bar_set(gcompris.BAR_LEVEL)
    gcompris.bar_set_level(self.gcomprisBoard)
    gcompris.bar_set(gcompris.BAR_LEVEL|gcompris.BAR_REPEAT_ICON)
    gcompris.bar_location(630, -1, 0.5)
    p = key_value(self.rootitem, self.VALUE)
    self.display_arrow()
    self.display_images(p.get_pair())


  def next_level(self):
    self.won = False

    self.rootitem.remove()

    if (self.gcomprisBoard.sublevel == 1):
      self.VALUE = self.NUMBERS
    elif (self.gcomprisBoard.sublevel == 2):
      self.VALUE = self.SYMBOLS
    elif (self.gcomprisBoard.sublevel == 3):
      self.VALUE = self.ALPHABETS

    gcompris.bar_set_level(self.gcomprisBoard)
    self.rootitem = goocanvas.Group(parent = \
      self.gcomprisBoard.canvas.get_root_item())

    self.base_setup()

  def display_images(self, pair):
    self.pair = pair
    self.word = gcompris.get_random_word(
                          self.wordlist,
                          self.gcomprisBoard.level + 2
                          )
    self.letters = list(self.word)
    self.letters = map(lambda x: x.upper(), self.letters)

    self.values = map(lambda x: self.pair[x], self.letters)

    self.ciphertext = "\" "
    for i in self.values:
      self.ciphertext +=  str(i) + "  "

    self.ciphertext += "\""

    goocanvas.Text(parent = self.rootitem,
                   x = 275,
                   y = 360,
                   fill_color = "white",
                   font = gcompris.skin.get_font("gcompris/subtitle"),
                   anchor = gtk.ANCHOR_CENTER,
                   text = self.ciphertext
                   )

    text_item = self.entry_text()

    # TUX svghandle
    svghandle = gcompris.utils.load_svg("decryption/tux.svg")
    self.tuxitem = goocanvas.Svg(
                                     parent = self.rootitem,
                                     svg_handle = svghandle,
                                     svg_id = "#TUX",
                                     # tooltip = _("click on me to check whether you have decrypted rightly")
                                     )
    self.tuxitem.translate(560,340)

    item = goocanvas.Svg(parent = self.rootitem,
                         svg_handle = gcompris.skin.svg_get(),
                         svg_id = "#OK"
                         )
    item.translate(-100, -20)
    item.connect("button_press_event", self.ok_event, text_item)
    gcompris.utils.item_focus_init(item, None)

    goocanvas.Text(parent = self.rootitem,
                   x = 220,
                   y = 250,
                   fill_color = "yellow",
                   font = gcompris.skin.get_font("gcompris/subtitle"),
                   anchor = gtk.ANCHOR_CENTER,
                   text = _("Decode the encrypted text given below")
                   ) 


  def ok_event(self, widget, target, event, data):
    self.enter_callback(data)

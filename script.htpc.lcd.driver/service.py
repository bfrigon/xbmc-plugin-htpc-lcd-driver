"""
    Plugin for driving HTPC LCD display
"""

import os
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import math
import string
import time


__plugin__ = "script.htpc.lcd.driver"
__author__ = 'bfrigon [benoit@frigon.info]'
__url__ = "www.bfrigon.com"
__credits__ = ""
__version__ = "0.1.015"
__settings__ = xbmcaddon.Addon(id='script.htpc.lcd.driver')
__cwd__ = __settings__.getAddonInfo('path')
__DEBUG__ = False

#-----------------------------------------
# Load libraries in ressources/lib
#-----------------------------------------
BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )
sys.path.append (BASE_RESOURCE_PATH)

from lcddriver import *
from xbmcstate import *



MASK_ICON_PLAY = 0x01
MASK_ICON_PAUSE = 0x02
MASK_ICON_PLAY_PAUSE = MASK_ICON_PLAY | MASK_ICON_PAUSE
MASK_ICON_NAV_UPDOWN = 0x04
MASK_ICON_NAV_LEFTRIGHT = 0x08
MASK_ICON_NAV = MASK_ICON_NAV_UPDOWN | MASK_ICON_NAV_LEFTRIGHT
MASK_ICON_MUSIC = 0x10
MASK_ICON_TV = 0x20

ICON_ID_PLAY = 0
ICON_ID_PAUSE = 1
ICON_ID_NAV_UPDOWN = 2
ICON_ID_NAV_LEFTRIGHT = 3
ICON_ID_MUSIC = 4
ICON_ID_TV = 5


       
#================================================================================================================
#
# Plugin class
#
#================================================================================================================
class Plugin():


    #----------------------------------------------------------------------------
    # __init__
    #
    # Arguments : None
    # 
    # Returns: None
    #----------------------------------------------------------------------------
    def __init__(self):
        self.scrollpos = 0
        self.scrolltext = ''
        self.scrollnextinc = 0
        self.scrollleft = False
        self.prev_scrolltext = ''
        self.prev_player_cur_time = None
        self.prev_player_total_time = None
        self.prev_icon_state = None
        self.icon_state = 0
        self.prev_pvr_rec_state = None
        self.prev_pvr_schd_state = None
        self.prev_backlight_red = -1
        self.prev_backlight_green = -1
        self.prev_backlight_blue = -1
        
        self.lcd = LcdDriver()
        self.xbmcstate = XbmcState()
        
        self.lcd.clear()
        
        self.lcd.def_custom_char(ICON_ID_PLAY, [0b00000, 0b01000, 0b01100, 0b01110, 0b01100, 0b01000, 0b00000, 0b00000])
        self.lcd.def_custom_char(ICON_ID_PAUSE, [0b00000, 0b11011, 0b11011, 0b11011, 0b11011, 0b11011, 0b00000, 0b00000])
        self.lcd.def_custom_char(ICON_ID_NAV_UPDOWN, [0b00100, 0b01110, 0b11111, 0b00000, 0b11111, 0b01110, 0b00100, 0b00000])
        self.lcd.def_custom_char(ICON_ID_NAV_LEFTRIGHT, [0b00000, 0b00000, 0b01010, 0b11011, 0b11011, 0b01010, 0b00000, 0b00000])    
        self.lcd.def_custom_char(ICON_ID_MUSIC, [0b00011, 0b00111, 0b01101, 0b01001, 0b01011, 0b11011, 0b11000, 0b00000])
        self.lcd.def_custom_char(ICON_ID_TV, [0b00000, 0b01010, 0b00100, 0b11111, 0b10001, 0b10001, 0b11111, 0b00000])


    #----------------------------------------------------------------------------
    # update_marquee() : Refresh the scrolling marquee
    #
    # Arguments : 
    #       - value : If set, replace the current text and reset the scroll position
    #
    # Returns: None
    #----------------------------------------------------------------------------
    def update_marquee(self, value=None):
        if value is not None:
            self.scrolltext = value

        if (time.time() < self.scrollnextinc) and (self.prev_scrolltext == self.scrolltext):
            return

        if self.prev_scrolltext != self.scrolltext:
            self.prev_scrolltext = self.scrolltext
            self.scrollpos = 0
            self.scrollleft = False
            self.scrollnextinc = time.time() + 3
        else:
            
            if len(self.scrolltext) <= 19:
                return
            
            self.scrollnextinc = time.time() + 0.25
            self.scrollpos = self.scrollpos + (-1 if self.scrollleft else 1)
            
            if self.scrollpos < 0:
                self.scrollleft = False
                self.scrollpos = 0
                self.scrollnextinc = time.time() + 1
                
            elif self.scrollpos + 19 > len(self.scrolltext):
                self.scrollpos = len(self.scrolltext) - 19
                self.scrollleft = True
                self.scrollnextinc = time.time() + 1
        
        if __DEBUG__:
            xbmc.log('script.htpc.lcd.driver: Update marquee, time : {0:f}   next inc: {1:f}  pos: {2}'.format(time.time(), self.scrollnextinc, self.scrollpos))
            
        self.lcd.goto(2,1)
        self.lcd.write(self.scrolltext[self.scrollpos:self.scrollpos+19].ljust(19), 2, 1)


    #----------------------------------------------------------------------------
    # update_time_display(): Refresh the current/total time display
    #
    # Arguments : 
    #       - current : Current playback position (hh:mm:ss)
    #       - total : Total playback time (hh:mm:ss)
    #
    # Returns: None
    #----------------------------------------------------------------------------
    def update_time_display(self, current, total):
        if (self.prev_player_cur_time == current) and (self.prev_player_total_time == total):
            return
    
        self.prev_player_cur_time = current
        self.prev_player_total_time = total
        
        if __DEBUG__:
            xbmc.log('script.htpc.lcd.driver: Update time display, current={0} total={1}'.format(current, total))
        
        self.lcd.goto(6,4)
        if len(current) == 0 or len(total) == 0:
            self.lcd.write('--:--/--:--  ')
        else:
            current = current.split(':')
            total = total.split(':')
            
            if len(current) > 2 and int(current[0]) > 0:
                self.lcd.write('{0:d}:{1}:{2}/'.format(int(current[0]), current[1], current[2]))
            else:
                self.lcd.write('{0}:{1}/'.format(current[-2], current[-1]))
            
            if len(total) > 2:
                self.lcd.write('{0:d}h{1} '.format(int(total[0]), total[1]))
            else:
                self.lcd.write('{0}:{1}'.format(total[0], total[1]))

            if len(current) > 2: self.lcd.write('  ')
        
        
    #----------------------------------------------------------------------------
    # update_icons() : Update the icons
    #
    # Arguments : 
    #       - mask : If set, replace the current text and reset the scroll position
    #
    # Returns: None
    #----------------------------------------------------------------------------
    def update_icons(self, mask = None, on = True):
        if mask is not None:
            if on:
                self.icon_state = self.icon_state | mask
            else:
                self.icon_state = self.icon_state & ~(mask)
        
        #--- Check if the icons needs to be updated ---#
        if self.icon_state is self.prev_icon_state:
            return
        
        self.prev_icon_state = self.icon_state
        
        if __DEBUG__:
            xbmc.log('script.htpc.lcd.driver: Update icons, state=0b{0:08b}'.format(self.icon_state))
        
        #--- Update pause/play icon ---#
        if (self.icon_state & MASK_ICON_PLAY) and (self.icon_state & MASK_ICON_PAUSE):
            self.lcd.write_custom_char(ICON_ID_PAUSE, 4, 2)
        elif (self.icon_state & MASK_ICON_PLAY):
            self.lcd.write_custom_char(ICON_ID_PLAY, 4, 2)
        else:
            self.lcd.write(' ', 4, 2)
            
        #--- Update menu navigation icon ---#
        if (self.icon_state & MASK_ICON_NAV_UPDOWN):
            self.lcd.write_custom_char(ICON_ID_NAV_UPDOWN, 1, 1)
        elif (self.icon_state & MASK_ICON_NAV_LEFTRIGHT):
            self.lcd.write_custom_char(ICON_ID_NAV_LEFTRIGHT, 1, 1)
        else:
            self.lcd.write(' ', 1, 1)
        
        #--- Update music mode icon ---#
        if self.icon_state & MASK_ICON_MUSIC:
            self.lcd.write_custom_char(ICON_ID_MUSIC, 2, 2)
        else:
            self.lcd.write(' ', 2, 2)
            
        #--- Update tv mode icon ---#
        if self.icon_state & MASK_ICON_TV:
            self.lcd.write_custom_char(ICON_ID_TV, 1, 2)
        else:
            self.lcd.write(' ', 1, 2)


    #----------------------------------------------------------------------------
    # update_status_leds() : Update record led status
    #
    # Arguments : None
    #
    # Returns: None
    #----------------------------------------------------------------------------
    def update_status_leds(self):
            
        pvr_rec_state = xbmc.getCondVisibility('Pvr.IsRecording')
        pvr_schd_state = xbmc.getCondVisibility('Pvr.HasTimer')
        
        #--- Check if the status leds needs to be updated ---#
        if (self.prev_pvr_rec_state is pvr_rec_state) and (self.prev_pvr_schd_state is pvr_schd_state):
            return
        
        self.prev_pvr_rec_state = pvr_rec_state
        self.prev_pvr_schd_state = pvr_schd_state
        
        if __DEBUG__:
            xbmc.log('script.htpc.lcd.driver: Update status leds: PVR_REC={0:d} PVR_SCHD={1:d}'.format(int(pvr_rec_state), int(pvr_schd_state)))
    
        self.lcd.set_led(LCD_LED_ALLOFF, 0)
        
        #--- update pvr scheduled/recording ---#
        if pvr_rec_state or pvr_schd_state:
            
            #--- 0=Green : Recording scheduled ---#
            #--- 1=Red : Recording active ---#
            self.lcd.set_led(LCD_LED_RECORD, int(pvr_rec_state))
        
    
    #----------------------------------------------------------------------------
    # update_backlight() : Sets the lcd backlight based on status
    #
    # Arguments : None
    #
    # Returns: None
    #----------------------------------------------------------------------------
    def update_backlight(self):
        
        if self.xbmcstate.isPlaying():
            r = 0
            g = 120
            b = 0
            
        elif self.xbmcstate.isPaused():
            r = 120
            g = 120
            b = 0
            
        else:
            r = 140
            g = 20
            b = 0
        
        
        #--- Check if the backlight needs to be updated ---#
        if (r is self.prev_backlight_red) and (g is self.prev_backlight_green) and (b is self.prev_backlight_blue):
            return
    
        self.prev_backlight_red = r
        self.prev_backlight_green = g
        self.prev_backlight_blue = b
    
        if __DEBUG__:
            xbmc.log('script.htpc.lcd.driver: Set RGB backlight RED={0:d} GREEN={1:d} BLUE={2:d}'.format(r,g,b))
    
        self.lcd.setrgb(r,g,b)
    
    
    #----------------------------------------------------------------------------
    # refresh() : Refresh data on the LCD
    #
    # Arguments : None
    #
    # Returns: None
    #----------------------------------------------------------------------------
    def refresh(self):
        #--- Update time display ---#
        if self.xbmcstate.isPlaying() or self.xbmcstate.isPaused():
            self.update_time_display(xbmc.getInfoLabel('Player.Time'), xbmc.getInfoLabel('Player.Duration'))
            
            self.update_icons(MASK_ICON_PLAY, True)
            self.update_icons(MASK_ICON_PAUSE, self.xbmcstate.isPaused())
            
        else:
            self.update_time_display('', '')
            self.update_icons(MASK_ICON_PLAY_PAUSE, False)


        #--- Set Music mode icon ---#
        if self.xbmcstate.hasAudio():
            self.icon_state = self.icon_state | MASK_ICON_MUSIC
        else:
            self.icon_state = self.icon_state & ~(MASK_ICON_MUSIC)
        
        
        #--- Set TV mode icon ---#
        if self.xbmcstate.isPlayingLiveTV():
            self.icon_state = self.icon_state | MASK_ICON_TV
        else:
            self.icon_state = self.icon_state & ~(MASK_ICON_TV)

        
        #--- Update marquee and other status icons based on the current state ---#
        state = self.xbmcstate.getCurrentState()
        if state is XBMC_STATE_PLAYING_VIDEO:
            self.icon_state = self.icon_state & ~(MASK_ICON_NAV)
            
            self.update_marquee(xbmc.getInfoLabel('VideoPlayer.Title'))
        
        elif state is XBMC_STATE_LIVE_TV:
            self.icon_state = self.icon_state & ~(MASK_ICON_NAV | MASK_ICON_MUSIC)
            
            ch_num = xbmc.getInfoLabel('VideoPlayer.ChannelNumber')
            ch_name = xbmc.getInfoLabel('VideoPlayer.ChannelName')
            self.update_marquee('CH {0:0>2s} {1:s}'.format(ch_num, ch_name))
        
        elif state is XBMC_STATE_BROWSE_PVR:
            self.icon_state = self.icon_state & ~(MASK_ICON_NAV | MASK_ICON_MUSIC)
            self.icon_state = self.icon_state | MASK_ICON_NAV_UPDOWN
            
            ch_num = xbmc.getInfoLabel('ListItem.ChannelNumber')
            ch_name = xbmc.getInfoLabel('ListItem.ChannelName')
            self.update_marquee('CH {0:0>2s} {1:s}'.format(ch_num, ch_name))
        
        elif state is XBMC_STATE_MUSIC_VIS:
            self.icon_state = self.icon_state & ~(MASK_ICON_NAV)
            
            self.update_marquee(xbmc.getInfoLabel('MusicPlayer.Title'))
        
        elif state is XBMC_STATE_BROWSE_VIDEO:
            self.icon_state = self.icon_state & ~(MASK_ICON_NAV | MASK_ICON_MUSIC)
            self.icon_state = self.icon_state | MASK_ICON_NAV_UPDOWN
            
            self.update_marquee(xbmc.getInfoLabel('ListItem.Label'))
            
        elif state is XBMC_STATE_BROWSE_MUSIC:
            self.icon_state = self.icon_state & ~(MASK_ICON_NAV)
            self.icon_state = self.icon_state | MASK_ICON_NAV_UPDOWN | MASK_ICON_MUSIC
            
            self.update_marquee(xbmc.getInfoLabel('ListItem.Label'))
            
        elif state is XBMC_STATE_HOME_MENU:
            self.icon_state = self.icon_state & ~(MASK_ICON_NAV)
            self.icon_state = self.icon_state | MASK_ICON_NAV_LEFTRIGHT
            
            self.update_marquee('Home > ' + xbmc.getInfoLabel('$INFO[System.CurrentControl]').lower().capitalize())
        else:
            self.icon_state = self.icon_state & ~(MASK_ICON_NAV)
            
            self.update_marquee('')

        self.update_icons()
        self.update_marquee()
        self.update_status_leds()
        self.update_backlight()


    #----------------------------------------------------------------------------
    # run() : Start service loop
    #
    # Arguments : None
    #
    # Returns: None
    #----------------------------------------------------------------------------
    def run(self):
        while (not xbmc.abortRequested):
            self.refresh()
            time.sleep(0.25)
            
            #--- Check if a key was pressed ---#
            key = self.lcd.read_next_key()
            if key is None:
                continue
            
            if self.xbmcstate.isPlaying() or self.xbmcstate.isPaused():
                if key is LCD_KEY_UP: xbmc.executebuiltin("Action(VolumeUp)")
                if key is LCD_KEY_DOWN:xbmc.executebuiltin("Action(VolumeDown)")
                if key is LCD_KEY_RIGHT: xbmc.executebuiltin("Action(StepForward)")
                if key is LCD_KEY_LEFT: xbmc.executebuiltin("Action(StepBack)")
                if key is LCD_KEY_ESC: xbmc.executebuiltin("Action(Stop)")
                
                if key is LCD_KEY_ENTER: 
                    if self.xbmcstate.isPlaying():
                        xbmc.executebuiltin("Action(Pause)")
                    else:
                        xbmc.executebuiltin("Action(Play)")
            else:
                if key is LCD_KEY_UP: xbmc.executebuiltin("Action(Up)")
                if key is LCD_KEY_DOWN:xbmc.executebuiltin("Action(Down)")
                if key is LCD_KEY_RIGHT: xbmc.executebuiltin("Action(Right)")
                if key is LCD_KEY_LEFT: xbmc.executebuiltin("Action(Left)")
                if key is LCD_KEY_ENTER: xbmc.executebuiltin("Action(Select)")
                if key is LCD_KEY_ESC: xbmc.executebuiltin("Action(Back)")
            
    
    


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if (__name__ == "__main__"):
    plugin = Plugin()
    plugin.run()


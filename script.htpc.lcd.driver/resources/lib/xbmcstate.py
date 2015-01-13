import xbmc
import xbmcgui
import string

__DEBUG__ = False


XBMC_STATE_UNKNOWN = -1
XBMC_STATE_HOME_MENU = 0
XBMC_STATE_BROWSE_VIDEO = 1
XBMC_STATE_PLAYING_VIDEO = 2
XBMC_STATE_MUSIC_VIS = 3
XBMC_STATE_BROWSE_MUSIC = 4
XBMC_STATE_LIVE_TV = 5
XBMC_STATE_BROWSE_PVR = 6

XBMC_WINDOW_HOME = 10000
XBMC_WINDOW_VIDEO_NAV = 10025
XBMC_WINDOW_MUSIC_FILES = 10501
XBMC_WINDOW_MUSIC_PLAYLIST = 10500
XBMC_WINDOW_FULLSCREEN_VIDEO = 12005
XBMC_WINDOW_MUSIC_VIS = 12006
XBMC_WINDOW_PVR = 10601

#================================================================================================================
#
# XbmcState
#
#================================================================================================================
class XbmcState():
    
    def __init__(self):
        self.prev_winid = None


    def getInfoLabel(self, label):
        return xbmc.getInfoLabel(label)


    def getInfoLabelBool(self, label):
        return xbmc.getCondVisibility(label)


    def getActiveWindowID(self):
        return int(xbmcgui.getCurrentWindowId())
    
    
    def hasVideo(self):
        return self.getInfoLabelBool('Player.HasVideo')

    
    def hasAudio(self):
        return self.getInfoLabelBool('Player.HasAudio')

    
    def isPlaying(self):
        return self.getInfoLabelBool('Player.Playing')

        
    def isPaused(self):
        return self.getInfoLabelBool('Player.Paused')

    
    def isPlayingLiveTV(self):
        return self.getInfoLabelBool('Pvr.IsPlayingTv')
    
    
    def getCurrentState(self):
        winid = self.getActiveWindowID()
        
        if winid is not self.prev_winid and __DEBUG__:
            self.prev_winid = winid
            xbmc.log('Window ID changed: {0:d}'.format(winid))
        
        if winid == XBMC_WINDOW_HOME:
            return XBMC_STATE_HOME_MENU
        
        if winid == XBMC_WINDOW_VIDEO_NAV:
            return XBMC_STATE_BROWSE_VIDEO
        
        if winid in [XBMC_WINDOW_MUSIC_FILES, XBMC_WINDOW_MUSIC_PLAYLIST]:
            return XBMC_STATE_BROWSE_MUSIC

        if winid == XBMC_WINDOW_PVR:
            return XBMC_STATE_BROWSE_PVR

        if self.getInfoLabelBool('Pvr.IsPlayingTv'):
            return XBMC_STATE_LIVE_TV

        if winid == XBMC_WINDOW_MUSIC_VIS:
            return XBMC_STATE_MUSIC_VIS
        
        if winid == XBMC_WINDOW_FULLSCREEN_VIDEO:
            return XBMC_STATE_PLAYING_VIDEO
        
        return XBMC_STATE_UNKNOWN

    
        
        
        

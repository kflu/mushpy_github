from consts import *

def set_trig_onoff(name, set_on):
    Trigger(name).enabled = set_on

def get_trig_onoff(name):
    return Trigger(name).enabled

def enable_trigger(name):
    set_trig_onoff(name, True)

def disable_trigger(name):
    set_trig_onoff(name, False)

def del_trigger(name):
    res = world.DeleteTrigger(name)
    if res != ErrorNo.eOK:
        raise TriggerOpError("Trigger deletion failed: {0}".format(res))

def add_trigger(name, pattern, script):
    res = world.AddTrigger(name, pattern, 
            "", # ResponseText
            TriggerFlags.KeepEval_Re, 
            -1, # Colour: NoChange
            0, # copy which wildcard to clipboard
            "", #foundfilename
            script # script name
            )
    if res != ErrorNo.eOK:
        raise TriggerOpError("Trigger creation failed: {0}".format(res))

class TriggerNotFoundError(Exception): pass
class TriggerOpError(Exception): pass

class Trigger:
    '''Trigger proxy class to a MushClient trigger.

    You can set or get options about the trigger.

    For getting, refer to:
    http://www.gammon.com.au/scripts/function.php?name=GetTriggerInfo

    For setting, refer to:
    http://www.gammon.com.au/scripts/function.php?name=SetTriggerOption
    
    '''

    TriggerInfoNames = {
        "whattomatch" : 1         ,#  What to match on (string)
        "whattosend" : 2          ,#  What to send (string)
        "soundtoplay" : 3         ,#  Sound to play (string)
        "scriptprocname" : 4      ,#  Script procedure name (string)
        "omitfromlog" : 5         ,#  Omit from log (boolean)
        "omitfromoutput" : 6      ,#  Omit from output (boolean)
        "keepeval" : 7            ,#  Keep evaluating (boolean)
        "enabled" : 8             ,#  Enabled (boolean)
        "regex" : 9               ,#  Regular expression (boolean)
        "ignorecase" : 10         ,# Ignore case (boolean)
        "reponsameline" : 11      ,# Repeat on same line (boolean)
        "playsoundifinactive" : 12 ,# Play sound if inactive (boolean)
        "expandvar" : 13          ,# Expand variables (boolean)
        "sendto" : 15             ,# Send to - see below (short)
        "sequence" : 16           ,# Sequence (short)
        "invoccount" : 20         ,# Invocation count (long)
        "timesmatched" : 21       ,# Times matched (long)
        "lastmatchedon" : 22      ,# Date/time trigger last matched (date)
        "groupname" : 26          ,# Group name (string)
        "varname" : 27            ,# Variable name (string)
        "execscriptflag" : 33     ,# Executing-script flag (boolean)
        "isscriptvalid" : 34      ,# Script is valid flag (boolean)
        "isoneshot" : 36          ,# 'one shot' flag (boolean)
    }

    _boolean_opts = set([
        "enabled", "expand_variables", "ignore_case", 
        "inverse", "italic", "keep_evaluating", 
        "lowercase_wildcard", "multi_line", "omit_from_log", 
        "omit_from_output", "one_shot", "regexp", 
        "repeat", "sound_if_inactive"])

    def __init__(self, name):
        if (world.istrigger(name) != ErrorNo.eOK):
            raise TriggerNotFoundError()
        # avoid recursive calls into __setattr__ and __getattr__
        self.__dict__["name"] = name

    def __getitem__(self, key):
        return world.GetTriggerInfo(self.name, self.TriggerInfoNames[key.lower()])

    def __getattr__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            return self.__getitem__(key)

    def __setitem__(self, key, value):
        '''Set option to a trigger.
        
        Things you can set:
        http://www.gammon.com.au/scripts/function.php?name=SetTriggerOption

"clipboard_arg": 0 - 10 - which wildcard to copy to the clipboard
"colour_change_type": 0=both, 1=foreground, 2=background
"custom_colour": 0=no change, 1 - 16, 17=other
"enabled": y/n - trigger is enabled
"expand_variables": y/n - expand variables (like @target)
"group": (string - group name)
"ignore_case": y/n - caseless matching
"inverse": y/n - only match if inverse, however see match_inverse
"italic": y/n - only match if italic, however see match_italic
"keep_evaluating": y/n - evaluate next trigger in sequence
"lines_to_match": 0 - 200 - how many lines to match for multi-line triggers
"lowercase_wildcard": y/n - make matching wildcards lower-case
"match": (string - what to match)
"match_style": (see below) - what style and colour combination to match on
"multi_line": y/n - multi-line trigger
"name": (string - name/label of trigger)
"new_style": (style(s) to change to: (bold (1) / underline (2) / italic (4) ) )
"omit_from_log": y/n - omit matching line from log file
"omit_from_output": y/n - omit matching line from output window
"one_shot": y/n - trigger is deleted after firing
"other_back_colour": (string - name of colour to change to)
"other_text_colour": (string - name of colour to change to)
"regexp": y/n - regular expression
"repeat": y/n - repeatedly evaluate on same line
"script": (string - name of function to call)
"send": (multi-line string - what to send)
"send_to": 0 - 14 - "send to" location (see below)
"sequence": 0 - 10000 - sequence in which to check - lower first
"sound": (string - sound file name to play)
"sound_if_inactive": y/n - play sound even if world inactive
"user": -2147483647 to 2147483647 - user-defined number
"variable": (string - name of variable to send to)
            
        '''
        if key in self._boolean_opts:
            value = "y" if value == True else "n"

        res = world.SetTriggerOption(self.name, key, value)
        if res != ErrorNo.eOK:
            raise TriggerOpError("Error setting trigger option: {0} {1} {2}".format(
                self.name, key, value))

    def __setattr__(self, key, value):
        if key in self.__dict__:
            self.__dict__[key] = value
        else:
            self.__setitem__(key, value)

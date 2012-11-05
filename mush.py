from greenlet import greenlet

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
        self.name = name

    def __getitem__(self, key):
        return world.GetTriggerInfo(self.name, key.lower())

    __getattr__ = __getitem__

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

        world.SetTriggerOption(self.name, key, value)

    __setattr__ = __setitem__

def init(ax):
    """Initialize this module with necessary global variables.

    This function must be called before using it.
    """
    globals["ax"] = ax
    globals["world"] = ax._scriptEngine_.globalNameSpaceModule.world

def expose(*args):
    '''Expose the functino to global namespace.

    After exposing, the global name is set to an attribute in the callable
    object as "global_name"

    Can be used as decorator as well as a function:

    @expose("global_name")
    def func: ...
    
    or

    expose(func, "global name")
    '''
    if len(args) == 2:
        # called as a function
        func, name = args[0:2]
        if not callable(func):
            raise TypeError(func, 'Not callable')   #FIXME
        print "exposing func: %s with name: %s" % (str(func), name)
        print 'expose(): global name space already has %s exposed.' % name
        setattr(ax._scriptEngine_.globalNameSpaceModule, name, func.__call__)
        setattr(func, 'global_name', name)
        return

    if len(args) == 1:
        # called as a decorator
        name = args[0]
        def CalledOnFunc(func):
            expose(func, name)
            return func
        return CalledOnFunc

class Task(greenlet):
    _func2pattern = {}

    def __init__(self):
        self._trig_state = {} # func : on/off
        self._register_trigs()

    def _register_trigs(self):
        for func in self._func2pattern:
            class_name = func.im_class.__name__
            func_name = func.im_func.__name__
            global_name = "g__{0}__{1}__{2}".format(class_name, func_name, id(func))
            expose(func, func.global_name)
            add_trigger(name=func.global_name, pattern=self._func2pattern[func],
                    script=func.global_name)

    def enable_all(self, store_state=True):
        if store_state:
            self._store_trig_state()
        for func in self._func2pattern:
            enable_trigger(name=func.global_name)

    def disable_all(self, store_state=True):
        if store_state:
            self._store_trig_state()
        for func in self._func2pattern:
            disable_trigger(name=func.global_name)

    def delete_all(self):
        self.disable_all(store_state=False)
        for func in self._func2pattern:
            del_trigger(name=func.global_name)

    def _store_trig_state(self):
        self._trig_state = {}
        for func in self._func2pattern:
            self._trig_state[func] = get_trig_onoff(name=func.global_name)

    def _resume_trig_state(self):
        for func in self._trig_state:
            set_trig_onoff(func.global_name, self._trig_state[func])
    resume = _resume_trig_state

    def _turn_onoff(self, func_or_list, on):
        if not isinstance(func_or_list, list):
            func_or_list = [func_or_list]
        for func in func_or_list:
            if on:
                enable_trigger(name=func.global_name)
            else:
                disable_trigger(name=func.global_name)

    def enable(self, func_or_list):
        self._turn_onoff(func_or_list, on=True)

    def disable(self, func_or_list):
        self._turn_onoff(func_or_list, on=False)

    def sw(self, task, *args, **kw):
        self.disable_all()
        result = task.switch(*args, **kw)
        self.resume()
        return result

    @staticmethod
    def trigger(pattern):
        def wrapper(func):
            Task._func2pattern[func] = pattern
            return func
        return wrapper

class TriggerFlags:
    eEnabled = 1 # enable trigger 
    eOmitFromLog = 2 # omit from log file 
    eOmitFromOutput = 4 # omit trigger from output 
    eKeepEvaluating = 8 # keep evaluating 
    eIgnoreCase = 16 # ignore case when matching 
    eTriggerRegularExpression = 32 # trigger uses regular expression 
    eExpandVariables = 512 # expand variables like @direction 
    eReplace = 1024 # replace existing trigger of same name 
    eLowercaseWildcard = 2048 # wildcards forced to lower-case
    eTemporary = 16384 # temporary - do not save to world file 

    KeepEval_Re_Replace = eKeepEvaluating|eTriggerRegularExpression|eReplace|eTemporary
    KeepEval_Re = eKeepEvaluating|eTriggerRegularExpression|eTemporary

class SendToFlags:
    eWorld = 0    # send to MUD                  
    eCommand = 1    # put in command window        
    eOutput = 2    # display in output window     
    eStatus = 3    # put in status line           
    eNewNotepad = 4    # new notepad                  
    eAppendNotepad = 5    # append to notepad            
    eLog = 6    # put in log file              
    eReplaceNotepad = 7    # replace notepad              
    eQueue = 8    # queue it                     
    eVariable = 9    # set a variable               
    eExecute = 10    # re-parse as command          
    eSpeedWalk = 11    # send to MUD as speedwalk     
    eScript = 12    # send to script engine        
    eBeforeQueue = 13    # send without queuing
    eScriptOmitFromOutput = 14    # Only Alias: send to script engine - after omitting from output

class TriggerColours:
    NOCHANGE = -1
    custom1 = 0
    custom2 = 1
    custom3 = 2 
    custom4 = 3
    custom5 = 4
    custom6 = 5
    custom7 = 6
    custom8 = 7
    custom9 = 8
    custom10 = 9
    custom11 = 10
    custom12 = 11
    custom13 = 12
    custom14 = 13
    custom15 = 14
    custom16 = 15

class AliasFlags:
    eEnabled = 1 # same as for AddTrigger 
    eIgnoreAliasCase = 32 # ignore case when matching 
    eOmitFromLogFile = 64 # omit this alias from the log file 
    eAliasRegularExpression = 128 # alias is regular expressions 
    eExpandVariables = 512 # same as for AddTrigger 
    eReplace = 1024 # same as for AddTrigger 
    eAliasSpeedWalk = 2048 # interpret send string as a speed walk string 
    eAliasQueue = 4096 # queue this alias for sending at the speedwalking delay interval 
    eAliasMenu = 8192 # this alias appears on the alias menu 
    eTemporary = 16384 # same as for AddTrigger

    Re_Replace = eAliasRegularExpression | eReplace | eTemporary
    Re = eAliasRegularExpression | eTemporary

class TimerFlags:
    eEnabled = 1 # same as for AddTrigger
    eAtTime = 2 # if not set, time is "every" 
    eOneShot = 4 # if set, timer only fires once 
    eTimerSpeedWalk = 8 # timer does a speed walk when it fires 
    eTimerNote = 16 # timer does a world.note when it fires 
    eActiveWhenClosed = 32  # timer fires even when world is disconnected
    eReplace = 1024 # same as for AddTrigger
    eTemporary = 16384 # same as for AddTrigger

    OneShot = eOneShot | eTemporary | eActiveWhenClosed

class ErrorNo:
    eOK = 0 # No error
    eWorldOpen = 30001 # The world is already open
    eWorldClosed = 30002 # The world is closed, this action cannot be performed
    eNoNameSpecified = 30003 # No name has been specified where one is required
    eCannotPlaySound = 30004 # The sound file could not be played
    eTriggerNotFound = 30005 # The specified trigger name does not exist
    eTriggerAlreadyExists = 30006 # Attempt to add a trigger that already exists
    eTriggerCannotBeEmpty = 30007 # The trigger "match" string cannot be empty
    eInvalidObjectLabel = 30008 # The name of this object is invalid
    eScriptNameNotLocated = 30009 # Script name is not in the script file
    eAliasNotFound = 30010 # The specified alias name does not exist
    eAliasAlreadyExists = 30011 # Attempt to add a alias that already exists
    eAliasCannotBeEmpty = 30012 # The alias "match" string cannot be empty
    eCouldNotOpenFile = 30013 # Unable to open requested file
    eLogFileNotOpen = 30014 # Log file was not open
    eLogFileAlreadyOpen = 30015 # Log file was already open
    eLogFileBadWrite = 30016 # Bad write to log file
    eTimerNotFound = 30017 # The specified timer name does not exist
    eTimerAlreadyExists = 30018 # Attempt to add a timer that already exists
    eVariableNotFound = 30019 # Attempt to delete a variable that does not exist
    eCommandNotEmpty = 30020 # Attempt to use SetCommand with a non-empty command window
    eBadRegularExpression = 30021 # Bad regular expression syntax
    eTimeInvalid = 30022 # Time given to AddTimer is invalid
    eBadMapItem = 30023 # Direction given to AddToMapper is invalid
    eNoMapItems = 30024 # No items in mapper
    eUnknownOption = 30025 # Option name not found
    eOptionOutOfRange = 30026 # New value for option is out of range
    eTriggerSequenceOutOfRange = 30027 # Trigger sequence value invalid
    eTriggerSendToInvalid = 30028 # Where to send trigger text to is invalid
    eTriggerLabelNotSpecified = 30029 # Trigger label not specified/invalid for 'send to variable'
    ePluginFileNotFound = 30030 # File name specified for plugin not found
    eProblemsLoadingPlugin = 30031 # There was a parsing or other problem loading the plugin
    ePluginCannotSetOption = 30032 # Plugin is not allowed to set this option
    ePluginCannotGetOption = 30033 # Plugin is not allowed to get this option
    eNoSuchPlugin = 30034 # Requested plugin is not installed
    eNotAPlugin = 30035 # Only a plugin can do this
    eNoSuchRoutine = 30036 # Plugin does not support that subroutine (subroutine not in script)
    ePluginDoesNotSaveState = 30037 # Plugin does not support saving state
    ePluginCouldNotSaveState = 30037 # Plugin could not save state (eg. no state directory)
    ePluginDisabled = 30039 # Plugin is currently disabled
    eErrorCallingPluginRoutine = 30040 # Could not call plugin routine
    eCommandsNestedTooDeeply = 30041 # Calls to "Execute" nested too deeply
    eCannotCreateChatSocket = 30042 # Unable to create socket for chat connection
    eCannotLookupDomainName = 30043 # Unable to do DNS (domain name) lookup for chat connection
    eNoChatConnections = 30044 # No chat connections open
    eChatPersonNotFound = 30045 # Requested chat person not connected
    eBadParameter = 30046 # General problem with a parameter to a script call
    eChatAlreadyListening = 30047 # Already listening for incoming chats
    eChatIDNotFound = 30048 # Chat session with that ID not found
    eChatAlreadyConnected = 30049 # Already connected to that server/port
    eClipboardEmpty = 30050 # Cannot get (text from the) clipboard
    eFileNotFound = 30051 # Cannot open the specified file
    eAlreadyTransferringFile = 30052 # Already transferring a file
    eNotTransferringFile = 30053 # Not transferring a file
    eNoSuchCommand = 30054 # There is not a command of that name
    eArrayAlreadyExists = 30055 # That array already exists
    eBadKeyName = 30056 # That name is not permitted for a key
    eArrayDoesNotExist = 30056 # That array does not exist
    eArrayNotEvenNumberOfValues = 30057 # Values to be imported into array are not in pairs
    eImportedWithDuplicates = 30058 # Import succeeded, however some values were overwritten
    eBadDelimiter = 30059 # Import/export delimiter must be a single character, other than backslash
    eSetReplacingExistingValue = 30060 # Array element set, existing value overwritten
    eKeyDoesNotExist = 30061 # Array key does not exist
    eCannotImport = 30062 # Cannot import because cannot find unused temporary character
    eItemInUse  = 30063  # Cannot delete trigger/alias/timer because it is executing a script
    eSpellCheckNotActive  = 30064  # Spell checker is not active
    eCannotAddFont  = 30065  # Cannot create requested font
    ePenStyleNotValid  = 30066  # Invalid settings for pen parameter
    eUnableToLoadImage  = 30067  # Bitmap image could not be loaded
    eImageNotInstalled  = 30068  # Image has not been loaded into window
    eInvalidNumberOfPoints  = 30069  # Number of points supplied is incorrect
    eInvalidPoint  = 30070  # Point is not numeric
    eHotspotPluginChanged  = 30071  # Hotspot processing must all be in same plugin
    eHotspotNotInstalled  = 30072  # Hotspot has not been defined for this window
    eNoSuchWindow  = 30073  # Requested miniwindow does not exist
    eBrushStyleNotValid  = 30074  # Invalid settings for brush parameter


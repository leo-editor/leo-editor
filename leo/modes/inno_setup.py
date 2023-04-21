# Leo colorizer control file for inno_setup mode.
# This file is in the public domain.

# Properties for inno_setup mode.
properties = {
    "lineComment": ";",
}

# Attributes dict for inno_setup_main ruleset.
inno_setup_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for inno_setup_string ruleset.
inno_setup_string_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for inno_setup_constant ruleset.
inno_setup_constant_attributes_dict = {
    "default": "KEYWORD3",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for inno_setup_directive ruleset.
inno_setup_directive_attributes_dict = {
    "default": "LITERAL4",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for inno_setup mode.
attributesDictDict = {
    "inno_setup_constant": inno_setup_constant_attributes_dict,
    "inno_setup_directive": inno_setup_directive_attributes_dict,
    "inno_setup_main": inno_setup_main_attributes_dict,
    "inno_setup_string": inno_setup_string_attributes_dict,
}

# Keywords dict for inno_setup_main ruleset.
inno_setup_main_keywords_dict = {
    "AfterInstall": "keyword4",
    "AllowCancelDuringInstall": "keyword1",
    "AllowNoIcons": "keyword1",
    "AllowRootDirectory": "keyword1",
    "AllowUNCPath": "keyword1",
    "AlwaysRestart": "keyword1",
    "AlwaysShowComponentsList": "keyword1",
    "AlwaysShowDirOnReadyPage": "keyword1",
    "AlwaysShowGroupOnReadyPage": "keyword1",
    "AlwaysUsePersonalGroup": "keyword1",
    "AppComments": "keyword1",
    "AppContact": "keyword1",
    "AppCopyright": "keyword1",
    "AppId": "keyword1",
    "AppModifyPath": "keyword1",
    "AppMutex": "keyword1",
    "AppName": "keyword1",
    "AppPublisher": "keyword1",
    "AppPublisherURL": "keyword1",
    "AppReadmeFile": "keyword1",
    "AppSupportURL": "keyword1",
    "AppUpdatesURL": "keyword1",
    "AppVerName": "keyword1",
    "AppVersion": "keyword1",
    "AppendDefaultDirName": "keyword1",
    "AppendDefaultGroupName": "keyword1",
    "Attribs": "keyword4",
    "BackColor": "keyword1",
    "BackColor2": "keyword1",
    "BackColorDirection": "keyword1",
    "BackSolid": "keyword1",
    "BeforeInstall": "keyword4",
    "ChangesAssociations": "keyword1",
    "Check": "keyword4",
    "Comment": "keyword4",
    "Components": "keyword4",
    "Compression": "keyword1",
    "CopyMode": "keyword4",
    "CreateAppDir": "keyword1",
    "CreateUninstallRegKey": "keyword1",
    "DefaultDirName": "keyword1",
    "DefaultGroupName": "keyword1",
    "DefaultUserInfoName": "keyword1",
    "DefaultUserInfoOrg": "keyword1",
    "DefaultUserInfoSerial": "keyword1",
    "Description": "keyword4",
    "DestDir": "keyword4",
    "DestName": "keyword4",
    "DirExistsWarning": "keyword1",
    "DisableDirPage": "keyword1",
    "DisableFinishedPage": "keyword1",
    "DisableProgramGroupPage": "keyword1",
    "DisableReadyMemo": "keyword1",
    "DisableReadyPage": "keyword1",
    "DisableStartupPrompt": "keyword1",
    "DiskClusterSize": "keyword1",
    "DiskSliceSize": "keyword1",
    "DiskSpanning": "keyword1",
    "EnableDirDoesntExistWarning": "keyword1",
    "Encryption": "keyword1",
    "Excludes": "keyword4",
    "ExtraDiskSpaceRequired": "keyword4",
    "Filename": "keyword4",
    "Flags": "keyword4",
    "FlatComponentsList": "keyword1",
    "FontInstall": "keyword4",
    "GroupDescription": "keyword4",
    "HKCC": "literal3",
    "HKCR": "literal3",
    "HKCU": "literal3",
    "HKLM": "literal3",
    "HKU": "literal3",
    "HotKey": "keyword4",
    "IconFilename": "keyword4",
    "IconIndex": "keyword4",
    "InfoAfterFile": "keyword4",
    "InfoBeforeFile": "keyword4",
    "InternalCompressLevel": "keyword1",
    "Key": "keyword4",
    "LanguageDetectionMethod": "keyword1",
    "LicenseFile": "keyword1",
    "MergeDuplicateFiles": "keyword1",
    "MessagesFile": "keyword4",
    "MinVersion": "keyword1",
    "Name": "keyword4",
    "OnlyBelowVersion": "keyword1",
    "OutputBaseFilename": "keyword1",
    "OutputDir": "keyword1",
    "Parameters": "keyword4",
    "Password": "keyword1",
    "Permissions": "keyword4",
    "PrivilegesRequired": "keyword1",
    "ReserveBytes": "keyword1",
    "RestartIfNeededByRun": "keyword1",
    "Root": "keyword4",
    "RunOnceId": "keyword4",
    "Section": "keyword4",
    "SetupIconFile": "keyword1",
    "ShowComponentSizes": "keyword1",
    "ShowLanguageDialog": "keyword1",
    "ShowTasksTreeLines": "keyword1",
    "SlicesPerDisk": "keyword1",
    "SolidCompression": "keyword1",
    "Source": "keyword4",
    "SourceDir": "keyword1",
    "StatusMsg": "keyword4",
    "String": "keyword4",
    "Subkey": "keyword4",
    "Tasks": "keyword4",
    "TimeStampRounding": "keyword1",
    "TimeStampsInUTC": "keyword1",
    "TouchDate": "keyword1",
    "TouchTime": "keyword1",
    "Type": "keyword4",
    "Types": "keyword4",
    "UninstallDisplayIcon": "keyword1",
    "UninstallDisplayName": "keyword1",
    "UninstallFilesDir": "keyword1",
    "UninstallIconFile": "keyword1",
    "UninstallLogMode": "keyword1",
    "UninstallRestartComputer": "keyword1",
    "UninstallStyle": "keyword1",
    "Uninstallable": "keyword1",
    "UpdateUninstallLogAppName": "keyword1",
    "UsePreviousAppDir": "keyword1",
    "UsePreviousGroup": "keyword1",
    "UsePreviousSetupType": "keyword1",
    "UsePreviousTasks": "keyword1",
    "UsePreviousUserInfo": "keyword1",
    "UseSetupLdr": "keyword1",
    "UserInfoPage": "keyword1",
    "ValueData": "keyword4",
    "ValueName": "keyword4",
    "ValueType": "keyword4",
    "VersionInfoCompany": "keyword1",
    "VersionInfoDescription": "keyword1",
    "VersionInfoTextVersion": "keyword1",
    "VersionInfoVersion": "keyword1",
    "WindowResizable": "keyword1",
    "WindowShowCaption": "keyword1",
    "WindowStartMaximized": "keyword1",
    "WindowVisible": "keyword1",
    "WizardImageBackColor": "keyword1",
    "WizardImageFile": "keyword1",
    "WizardImageStretch": "keyword1",
    "WizardSmallImageBackColor": "keyword1",
    "WizardSmallImageFile": "keyword1",
    "WorkingDir": "keyword4",
    "allowunsafefiles": "literal3",
    "binary": "literal3",
    "checkedonce": "literal3",
    "closeonexit": "literal3",
    "compact": "literal3",
    "comparetimestamp": "literal3",
    "confirmoverwrite": "literal3",
    "createkeyifdoesntexist": "literal3",
    "createonlyiffileexists": "literal3",
    "createvalueifdoesntexist": "literal3",
    "deleteafterinstall": "literal3",
    "deletekey": "literal3",
    "deletevalue": "literal3",
    "desktopicon": "literal3",
    "dirifempty": "literal3",
    "disablenouninstallwarning": "literal3",
    "dontcloseonexit": "literal3",
    "dontcopy": "literal3",
    "dontcreatekey": "literal3",
    "dontinheritcheck": "literal3",
    "dontverifychecksum": "literal3",
    "dword": "literal3",
    "exclusive": "literal3",
    "expandsz": "literal3",
    "external": "literal3",
    "files": "literal3",
    "filesandordirs": "literal3",
    "fixed": "literal3",
    "fontisnttruetype": "literal3",
    "full": "literal3",
    "hidden": "literal3",
    "hidewizard": "literal3",
    "ignoreversion": "literal3",
    "iscustom": "literal3",
    "isreadme": "literal3",
    "modify": "literal3",
    "multisz": "literal3",
    "nocompression": "literal3",
    "noencryption": "literal3",
    "noerror": "literal3",
    "none": "literal3",
    "noregerror": "literal3",
    "nowait": "literal3",
    "onlyifdestfileexists": "literal3",
    "onlyifdoesntexist": "literal3",
    "overwritereadonly": "literal3",
    "postinstall": "literal3",
    "preservestringtype": "literal3",
    "promptifolder": "literal3",
    "quicklaunchicon": "literal3",
    "read": "literal3",
    "readexec": "literal3",
    "readonly": "literal3",
    "recursesubdirs": "literal3",
    "regserver": "literal3",
    "regtypelib": "literal3",
    "replacesameversion": "literal3",
    "restart": "literal3",
    "restartreplace": "literal3",
    "runhidden": "literal3",
    "runmaximized": "literal3",
    "runminimized": "literal3",
    "sharedfile": "literal3",
    "shellexec": "literal3",
    "skipifdoesntexist": "literal3",
    "skipifnotsilent": "literal3",
    "skipifsilent": "literal3",
    "skipifsourcedoesntexist": "literal3",
    "sortfilesbyextension": "literal3",
    "string": "literal3",
    "system": "literal3",
    "touch": "literal3",
    "unchecked": "literal3",
    "uninsalwaysuninstall": "literal3",
    "uninsclearvalue": "literal3",
    "uninsdeleteentry": "literal3",
    "uninsdeletekey": "literal3",
    "uninsdeletekeyifempty": "literal3",
    "uninsdeletesection": "literal3",
    "uninsdeletesectionifempty": "literal3",
    "uninsdeletevalue": "literal3",
    "uninsneveruninstall": "literal3",
    "uninsremovereadonly": "literal3",
    "uninsrestartdelete": "literal3",
    "useapppaths": "literal3",
    "waituntilidle": "literal3",
}

# Keywords dict for inno_setup_string ruleset.
inno_setup_string_keywords_dict = {}

# Keywords dict for inno_setup_constant ruleset.
inno_setup_constant_keywords_dict = {}

# Keywords dict for inno_setup_directive ruleset.
inno_setup_directive_keywords_dict = {
    "copy": "function",
    "copyfile": "function",
    "defined": "function",
    "deletefile": "function",
    "entrycount": "function",
    "exec": "function",
    "fileclose": "function",
    "fileeof": "function",
    "fileexists": "function",
    "fileopen": "function",
    "fileread": "function",
    "filereset": "function",
    "filesize": "function",
    "find": "function",
    "findclose": "function",
    "findfirst": "function",
    "findgetfilename": "function",
    "findnext": "function",
    "getenv": "function",
    "getfileversion": "function",
    "getstringfileinfo": "function",
    "int": "function",
    "len": "function",
    "lowercase": "function",
    "pos": "function",
    "readini": "function",
    "readreg": "function",
    "rpos": "function",
    "savetofile": "function",
    "setsetupsetting": "function",
    "setupsetting": "function",
    "str": "function",
    "typeof": "function",
    "writeini": "function",
}

# Dictionary of keywords dictionaries for inno_setup mode.
keywordsDictDict = {
    "inno_setup_constant": inno_setup_constant_keywords_dict,
    "inno_setup_directive": inno_setup_directive_keywords_dict,
    "inno_setup_main": inno_setup_main_keywords_dict,
    "inno_setup_string": inno_setup_string_keywords_dict,
}

# Rules for inno_setup_main ruleset.

def inno_setup_rule0(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="[code]",
          at_line_start=True,
          delegate="pascal::main")

def inno_setup_rule1(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="[Setup]",
          at_line_start=True)

def inno_setup_rule2(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="[Types]",
          at_line_start=True)

def inno_setup_rule3(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="[Components]",
          at_line_start=True)

def inno_setup_rule4(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="[Tasks]",
          at_line_start=True)

def inno_setup_rule5(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="[Dirs]",
          at_line_start=True)

def inno_setup_rule6(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="[Files]",
          at_line_start=True)

def inno_setup_rule7(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="[Icons]",
          at_line_start=True)

def inno_setup_rule8(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="[INI]",
          at_line_start=True)

def inno_setup_rule9(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="[InstallDelete]",
          at_line_start=True)

def inno_setup_rule10(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="[Languages]",
          at_line_start=True)

def inno_setup_rule11(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="[Messages]",
          at_line_start=True)

def inno_setup_rule12(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="[CustomMessages]",
          at_line_start=True)

def inno_setup_rule13(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="[LangOptions]",
          at_line_start=True)

def inno_setup_rule14(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="[Registry]",
          at_line_start=True)

def inno_setup_rule15(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="[Run]",
          at_line_start=True)

def inno_setup_rule16(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="[UninstallRun]",
          at_line_start=True)

def inno_setup_rule17(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="[UninstallDelete]",
          at_line_start=True)

def inno_setup_rule18(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal4", seq="#define",
          delegate="inno_setup::directive")

def inno_setup_rule19(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal4", seq="#dim",
          delegate="inno_setup::directive")

def inno_setup_rule20(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal4", seq="#undef",
          delegate="inno_setup::directive")

def inno_setup_rule21(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal4", seq="#include",
          delegate="inno_setup::directive")

def inno_setup_rule22(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal4", seq="#emit",
          delegate="inno_setup::directive")

def inno_setup_rule23(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal4", seq="#expr",
          delegate="inno_setup::directive")

def inno_setup_rule24(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal4", seq="#insert",
          delegate="inno_setup::directive")

def inno_setup_rule25(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal4", seq="#append",
          delegate="inno_setup::directive")

def inno_setup_rule26(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal4", seq="#if",
          delegate="inno_setup::directive")

def inno_setup_rule27(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal4", seq="#elif",
          delegate="inno_setup::directive")

def inno_setup_rule28(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal4", seq="#else",
          delegate="inno_setup::directive")

def inno_setup_rule29(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal4", seq="#endif",
          delegate="inno_setup::directive")

def inno_setup_rule30(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal4", seq="#ifexist",
          delegate="inno_setup::directive")

def inno_setup_rule31(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal4", seq="#ifnexist",
          delegate="inno_setup::directive")

def inno_setup_rule32(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal4", seq="#ifdef",
          delegate="inno_setup::directive")

def inno_setup_rule33(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal4", seq="#for",
          delegate="inno_setup::directive")

def inno_setup_rule34(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal4", seq="#sub",
          delegate="inno_setup::directive")

def inno_setup_rule35(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal4", seq="#endsub",
          delegate="inno_setup::directive")

def inno_setup_rule36(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal4", seq="#pragma",
          delegate="inno_setup::directive")

def inno_setup_rule37(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal4", seq="#error",
          delegate="inno_setup::directive")

def inno_setup_rule38(colorer, s, i):
    return colorer.match_span(s, i, kind="literal4", begin="{#", end="}")

def inno_setup_rule39(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal2", pattern="%")

def inno_setup_rule40(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="inno_setup::string")

def inno_setup_rule41(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          delegate="inno_setup::string")

def inno_setup_rule42(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="{", end="}")

def inno_setup_rule43(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq=";",
          at_line_start=True)

def inno_setup_rule44(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#",
          at_line_start=True)

def inno_setup_rule45(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for inno_setup_main ruleset.
rulesDict1 = {
    "\"": [inno_setup_rule40,],
    "#": [inno_setup_rule18, inno_setup_rule19, inno_setup_rule20, inno_setup_rule21, inno_setup_rule22, inno_setup_rule23, inno_setup_rule24, inno_setup_rule25, inno_setup_rule26, inno_setup_rule27, inno_setup_rule28, inno_setup_rule29, inno_setup_rule30, inno_setup_rule31, inno_setup_rule32, inno_setup_rule33, inno_setup_rule34, inno_setup_rule35, inno_setup_rule36, inno_setup_rule37, inno_setup_rule44,],
    "%": [inno_setup_rule39,],
    "'": [inno_setup_rule41,],
    "0": [inno_setup_rule45,],
    "1": [inno_setup_rule45,],
    "2": [inno_setup_rule45,],
    "3": [inno_setup_rule45,],
    "4": [inno_setup_rule45,],
    "5": [inno_setup_rule45,],
    "6": [inno_setup_rule45,],
    "7": [inno_setup_rule45,],
    "8": [inno_setup_rule45,],
    "9": [inno_setup_rule45,],
    ";": [inno_setup_rule43,],
    "@": [inno_setup_rule45,],
    "A": [inno_setup_rule45,],
    "B": [inno_setup_rule45,],
    "C": [inno_setup_rule45,],
    "D": [inno_setup_rule45,],
    "E": [inno_setup_rule45,],
    "F": [inno_setup_rule45,],
    "G": [inno_setup_rule45,],
    "H": [inno_setup_rule45,],
    "I": [inno_setup_rule45,],
    "J": [inno_setup_rule45,],
    "K": [inno_setup_rule45,],
    "L": [inno_setup_rule45,],
    "M": [inno_setup_rule45,],
    "N": [inno_setup_rule45,],
    "O": [inno_setup_rule45,],
    "P": [inno_setup_rule45,],
    "Q": [inno_setup_rule45,],
    "R": [inno_setup_rule45,],
    "S": [inno_setup_rule45,],
    "T": [inno_setup_rule45,],
    "U": [inno_setup_rule45,],
    "V": [inno_setup_rule45,],
    "W": [inno_setup_rule45,],
    "X": [inno_setup_rule45,],
    "Y": [inno_setup_rule45,],
    "Z": [inno_setup_rule45,],
    "[": [inno_setup_rule0, inno_setup_rule1, inno_setup_rule2, inno_setup_rule3, inno_setup_rule4, inno_setup_rule5, inno_setup_rule6, inno_setup_rule7, inno_setup_rule8, inno_setup_rule9, inno_setup_rule10, inno_setup_rule11, inno_setup_rule12, inno_setup_rule13, inno_setup_rule14, inno_setup_rule15, inno_setup_rule16, inno_setup_rule17,],
    "a": [inno_setup_rule45,],
    "b": [inno_setup_rule45,],
    "c": [inno_setup_rule45,],
    "d": [inno_setup_rule45,],
    "e": [inno_setup_rule45,],
    "f": [inno_setup_rule45,],
    "g": [inno_setup_rule45,],
    "h": [inno_setup_rule45,],
    "i": [inno_setup_rule45,],
    "j": [inno_setup_rule45,],
    "k": [inno_setup_rule45,],
    "l": [inno_setup_rule45,],
    "m": [inno_setup_rule45,],
    "n": [inno_setup_rule45,],
    "o": [inno_setup_rule45,],
    "p": [inno_setup_rule45,],
    "q": [inno_setup_rule45,],
    "r": [inno_setup_rule45,],
    "s": [inno_setup_rule45,],
    "t": [inno_setup_rule45,],
    "u": [inno_setup_rule45,],
    "v": [inno_setup_rule45,],
    "w": [inno_setup_rule45,],
    "x": [inno_setup_rule45,],
    "y": [inno_setup_rule45,],
    "z": [inno_setup_rule45,],
    "{": [inno_setup_rule38, inno_setup_rule42,],
}

# Rules for inno_setup_string ruleset.

def inno_setup_rule46(colorer, s, i):
    return colorer.match_span(s, i, kind="literal4", begin="{#", end="}")

def inno_setup_rule47(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="{", end="}",
          delegate="inno_setup::constant")

# Rules dict for inno_setup_string ruleset.
rulesDict2 = {
    "{": [inno_setup_rule46, inno_setup_rule47,],
}

# Rules for inno_setup_constant ruleset.

def inno_setup_rule48(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern="code:",
          exclude_match=True)

def inno_setup_rule49(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

# Rules dict for inno_setup_constant ruleset.
rulesDict3 = {
    "c": [inno_setup_rule48,],
    "|": [inno_setup_rule49,],
}

# Rules for inno_setup_directive ruleset.

def inno_setup_rule50(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq=";")

def inno_setup_rule51(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="/*", end="*/")

def inno_setup_rule52(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def inno_setup_rule53(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for inno_setup_directive ruleset.
rulesDict4 = {
    "\"": [inno_setup_rule52,],
    "/": [inno_setup_rule51,],
    "0": [inno_setup_rule53,],
    "1": [inno_setup_rule53,],
    "2": [inno_setup_rule53,],
    "3": [inno_setup_rule53,],
    "4": [inno_setup_rule53,],
    "5": [inno_setup_rule53,],
    "6": [inno_setup_rule53,],
    "7": [inno_setup_rule53,],
    "8": [inno_setup_rule53,],
    "9": [inno_setup_rule53,],
    ";": [inno_setup_rule50,],
    "@": [inno_setup_rule53,],
    "A": [inno_setup_rule53,],
    "B": [inno_setup_rule53,],
    "C": [inno_setup_rule53,],
    "D": [inno_setup_rule53,],
    "E": [inno_setup_rule53,],
    "F": [inno_setup_rule53,],
    "G": [inno_setup_rule53,],
    "H": [inno_setup_rule53,],
    "I": [inno_setup_rule53,],
    "J": [inno_setup_rule53,],
    "K": [inno_setup_rule53,],
    "L": [inno_setup_rule53,],
    "M": [inno_setup_rule53,],
    "N": [inno_setup_rule53,],
    "O": [inno_setup_rule53,],
    "P": [inno_setup_rule53,],
    "Q": [inno_setup_rule53,],
    "R": [inno_setup_rule53,],
    "S": [inno_setup_rule53,],
    "T": [inno_setup_rule53,],
    "U": [inno_setup_rule53,],
    "V": [inno_setup_rule53,],
    "W": [inno_setup_rule53,],
    "X": [inno_setup_rule53,],
    "Y": [inno_setup_rule53,],
    "Z": [inno_setup_rule53,],
    "a": [inno_setup_rule53,],
    "b": [inno_setup_rule53,],
    "c": [inno_setup_rule53,],
    "d": [inno_setup_rule53,],
    "e": [inno_setup_rule53,],
    "f": [inno_setup_rule53,],
    "g": [inno_setup_rule53,],
    "h": [inno_setup_rule53,],
    "i": [inno_setup_rule53,],
    "j": [inno_setup_rule53,],
    "k": [inno_setup_rule53,],
    "l": [inno_setup_rule53,],
    "m": [inno_setup_rule53,],
    "n": [inno_setup_rule53,],
    "o": [inno_setup_rule53,],
    "p": [inno_setup_rule53,],
    "q": [inno_setup_rule53,],
    "r": [inno_setup_rule53,],
    "s": [inno_setup_rule53,],
    "t": [inno_setup_rule53,],
    "u": [inno_setup_rule53,],
    "v": [inno_setup_rule53,],
    "w": [inno_setup_rule53,],
    "x": [inno_setup_rule53,],
    "y": [inno_setup_rule53,],
    "z": [inno_setup_rule53,],
}

# x.rulesDictDict for inno_setup mode.
rulesDictDict = {
    "inno_setup_constant": rulesDict3,
    "inno_setup_directive": rulesDict4,
    "inno_setup_main": rulesDict1,
    "inno_setup_string": rulesDict2,
}

# Import dict for inno_setup mode.
importDict = {}

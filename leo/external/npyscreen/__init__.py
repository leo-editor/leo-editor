#@+leo-ver=5-thin
#@+node:ekr.20170428084208.443: * @file ../external/npyscreen/__init__.py
#!/usr/bin/python
#@+others
#@+node:ekr.20170428084208.444: ** Declarations
from .globals                   import DEBUG, DISABLE_RESIZE_SYSTEM

from .wgwidget                  import TEST_SETTINGS, ExhaustedTestInput, add_test_input_from_iterable, add_test_input_ch

from .npyssafewrapper           import wrapper, wrapper_basic

from   .npysThemeManagers       import ThemeManager, disableColor, enableColor
from   . import npysThemes      as     Themes 
from   .apNPSApplication        import NPSApp
from   .apNPSApplicationManaged import NPSAppManaged
from   .proto_fm_screen_area    import setTheme
from   .fmForm                  import FormBaseNew, Form, TitleForm, TitleFooterForm, SplitForm, FormExpanded, FormBaseNewExpanded, blank_terminal
from   .fmActionForm            import ActionForm, ActionFormExpanded
from   .fmActionFormV2          import ActionFormV2, ActionFormExpandedV2, ActionFormMinimal
from   .fmFormWithMenus         import FormWithMenus, ActionFormWithMenus, \
                                       FormBaseNewWithMenus, SplitFormWithMenus, \
                                       ActionFormV2WithMenus
from   .fmPopup                 import Popup, MessagePopup, ActionPopup, PopupWide, ActionPopupWide
from   .fmFormMutt              import FormMutt, FormMuttWithMenus
from   .fmFileSelector          import FileSelector, selectFile

from .fmFormMuttActive          import ActionControllerSimple, TextCommandBox, \
                                       FormMuttActive, FormMuttActiveWithMenus
from .fmFormMuttActive          import FormMuttActiveTraditional, FormMuttActiveTraditionalWithMenus


from .fmFormMultiPage           import FormMultiPage, FormMultiPageAction,\
                                       FormMultiPageActionWithMenus, FormMultiPageWithMenus

from .npysNPSFilteredData       import NPSFilteredDataBase, NPSFilteredDataList

from .wgbutton                  import MiniButton
from .wgbutton                  import MiniButtonPress
from .wgbutton                  import MiniButton      as Button
from .wgbutton                  import MiniButtonPress as ButtonPress

from .wgtextbox                 import Textfield, FixedText
from .wgtitlefield              import TitleText, TitleFixedText
from .wgpassword                import PasswordEntry, TitlePassword
from .wgannotatetextbox         import AnnotateTextboxBase
from .wgannotatetextbox         import AnnotateTextboxBaseRight

from .wgslider                  import Slider, TitleSlider
from .wgslider                  import SliderNoLabel, TitleSliderNoLabel
from .wgslider                  import SliderPercent, TitleSliderPercent

from .wgwidget                  import DummyWidget, NotEnoughSpaceForWidget
from . import wgwidget as widget

from .wgmultiline               import MultiLine, Pager, TitleMultiLine, TitlePager, MultiLineAction, BufferPager, TitleBufferPager
from .wgmultiselect             import MultiSelect, TitleMultiSelect, MultiSelectFixed, \
                                       TitleMultiSelectFixed, MultiSelectAction
from .wgeditmultiline           import MultiLineEdit
from .wgcombobox                import ComboBox, TitleCombo
from .wgcheckbox                import Checkbox, RoundCheckBox, CheckBoxMultiline, RoundCheckBoxMultiline, CheckBox, CheckboxBare
from .wgFormControlCheckbox     import FormControlCheckbox
from .wgautocomplete            import TitleFilename, Filename, Autocomplete
from .muMenu                    import Menu
from .wgselectone               import SelectOne, TitleSelectOne
from .wgdatecombo               import DateCombo, TitleDateCombo

from .npysTree import TreeData
from .wgmultilinetree           import MLTree, MLTreeAnnotated, MLTreeAction, MLTreeAnnotatedAction
from .wgmultilinetreeselectable import MLTreeMultiSelect, TreeLineSelectable
from .wgmultilinetreeselectable import MLTreeMultiSelectAnnotated, TreeLineSelectableAnnotated


# The following are maintained for compatibility with old code only. ##########################################

from .compatibility_code.oldtreeclasses import MultiLineTree, SelectOneTree
from .compatibility_code.oldtreeclasses import MultiLineTreeNew, MultiLineTreeNewAction, TreeLine, TreeLineAnnotated # Experimental
from .compatibility_code.oldtreeclasses import MultiLineTreeNewAnnotatedAction, MultiLineTreeNewAnnotated # Experimental
from .compatibility_code.npysNPSTree import NPSTreeData

# End compatibility. ###########################################################################################

from .wgfilenamecombo           import FilenameCombo, TitleFilenameCombo
from .wgboxwidget               import BoxBasic, BoxTitle
from .wgmultiline               import MultiLineActionWithShortcuts
from .wgmultilineeditable       import MultiLineEditable, MultiLineEditableTitle, MultiLineEditableBoxed

from .wgmonthbox                import MonthBox
from .wggrid                    import SimpleGrid
from .wggridcoltitles           import GridColTitles

from .muNewMenu                 import NewMenu, MenuItem
from .wgNMenuDisplay            import MenuDisplay, MenuDisplayScreen

from .npyspmfuncs               import CallSubShell

from .utilNotify                 import notify, notify_confirm, notify_wait, notify_ok_cancel, notify_yes_no

# Base classes for overriding:

# Standard Forms:
from . import stdfmemail

# Experimental Only
from .wgtextboxunicode import TextfieldUnicode
from .wgtexttokens     import TextTokens, TitleTextTokens

# Very experimental. Don't use for anything serious
from .apOptions import SimpleOptionForm
from .apOptions import OptionListDisplay, OptionChanger, OptionList, OptionLimitedChoices, OptionListDisplayLine
from .apOptions import OptionFreeText, OptionSingleChoice, OptionMultiChoice, OptionMultiFreeList, \
                       OptionBoolean, OptionFilename, OptionDate, OptionMultiFreeText


# This really is about as experimental as it gets
from .apNPSApplicationEvents import StandardApp
from .eveventhandler import Event


#@+node:vitalije.20170717124737.1: ** pyflake silencer
assert (DEBUG, DISABLE_RESIZE_SYSTEM, TEST_SETTINGS) != (ExhaustedTestInput,
    add_test_input_from_iterable, add_test_input_ch, wrapper, wrapper_basic,
    ThemeManager, disableColor, enableColor, Themes, NPSApp, NPSAppManaged,
    setTheme, FormBaseNew, Form, TitleForm, TitleFooterForm, SplitForm,
    FormExpanded, FormBaseNewExpanded, blank_terminal, ActionForm,
    ActionFormExpanded, ActionFormV2, ActionFormExpandedV2,
    ActionFormMinimal, FormWithMenus, ActionFormWithMenus, Popup,
    MessagePopup, ActionPopup, PopupWide, ActionPopupWide, FormMutt,
    FormMuttWithMenus, FileSelector, selectFile, ActionControllerSimple,
    TextCommandBox, FormMuttActiveTraditional,
    FormMuttActiveTraditionalWithMenus, FormMultiPage, FormMultiPageAction,
    NPSFilteredDataBase, NPSFilteredDataList, MiniButton, MiniButtonPress,
    Button, ButtonPress, Textfield, FixedText, TitleText, TitleFixedText,
    PasswordEntry, TitlePassword, AnnotateTextboxBase,
    AnnotateTextboxBaseRight, Slider, TitleSlider, SliderNoLabel,
    TitleSliderNoLabel, SliderPercent, TitleSliderPercent, DummyWidget,
    NotEnoughSpaceForWidget, widget, MultiLine, Pager, TitleMultiLine,
    TitlePager, MultiLineAction, BufferPager, TitleBufferPager, MultiSelect,
    TitleMultiSelect, MultiSelectFixed, MultiLineEdit, ComboBox,
    TitleCombo, Checkbox, RoundCheckBox, CheckBoxMultiline,
    RoundCheckBoxMultiline, CheckBox, CheckboxBare, FormControlCheckbox,
    TitleFilename, Filename, Autocomplete, Menu, SelectOne, TitleSelectOne,
    DateCombo, TitleDateCombo, TreeData, MLTree, MLTreeAnnotated,
    MLTreeAction, MLTreeAnnotatedAction, MLTreeMultiSelect,
    TreeLineSelectable, MLTreeMultiSelectAnnotated,
    TreeLineSelectableAnnotated, MultiLineTree, SelectOneTree,
    MultiLineTreeNew, MultiLineTreeNewAction, TreeLine, TreeLineAnnotated,
    MultiLineTreeNewAnnotatedAction, MultiLineTreeNewAnnotated, NPSTreeData,
    FilenameCombo, TitleFilenameCombo, BoxBasic, BoxTitle,
    MultiLineActionWithShortcuts, MultiLineEditable, MultiLineEditableTitle,
    MultiLineEditableBoxed, MonthBox, SimpleGrid, GridColTitles, NewMenu,
    MenuItem, MenuDisplay, MenuDisplayScreen, CallSubShell, notify,
    notify_confirm, notify_wait, notify_ok_cancel, notify_yes_no,
    stdfmemail, TextfieldUnicode, TextTokens, TitleTextTokens,
    SimpleOptionForm, OptionListDisplay, OptionChanger, OptionList,
    OptionLimitedChoices, OptionListDisplayLine, OptionFreeText,
    OptionSingleChoice, OptionMultiChoice, OptionMultiFreeList, StandardApp,
    Event, ActionFormV2WithMenus, SplitFormWithMenus, FormBaseNewWithMenus,
    FormMuttActiveWithMenus, FormMuttActive, FormMultiPageActionWithMenus,
    FormMultiPageWithMenus, TitleMultiSelectFixed, MultiSelectAction, 
    OptionBoolean, OptionMultiFreeText, OptionFilename, OptionDate)
#@-others
#@@language python
#@@tabwidth -4
#@-leo

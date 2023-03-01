#@+leo-ver=5-thin
#@+node:ekr.20040828105233: * @file ../plugins/examples/chinese_menu.py

"""
Translate a few menu items into Simplified Chinese
本插件将部分Leo菜单翻译成简体中文
   By Zhang Le <ejoy@xinhuanet.com>

"""
# Chinese translation completed by Zhang Le, May 2004
# based on the french_fm.py
# NOTE: The accelerated key (&) failed to work on Chinese text, probably because
# the width of one Chinese character is 2 not 1, which confuses Tk. I'm not sure
# whether this is a bug of Tk or a bug of Leo. Although I do not use & in the
# Chinese menu, Tk places an underline below the first character of each menu
# entry. Another bug in Tk?
# Note 2 (EKR):  The menu names themselves did not translate on my XP machine.
# All the headlines appear as "??".
from leo.core import leoGlobals as g

#@+others
#@+node:ekr.20111104210837.9689: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    ok = not g.unitTesting  # Unpleasant for unit testing.
    if ok:
        g.registerHandler("menu2", onMenu)
        g.plugin_signon(__name__)
    return ok
#@+node:ekr.20040828105233.1: ** onMenu
def onMenu(tag, keywords):

    c = keywords.get("c")
    table = (
        #@+others
        #@+node:ekr.20040828105233.2: *3* file menu
        ("File", "File文件"),
            ("New", "新建"),
            ("Open...", "打开"),
            ("Open With...", "用程序打开..."),
            ("Close", "关闭"),
            ("Save", "保存"),
            ("Save As", "另存为..."),
            ("Save To", "另存到..."),
            ("Revert To Saved", "恢复到保存的文件"),
            ("Recent Files...", "最近访问的文件..."),
                ("Clear Recent Files", "清除最近访问文件列表"),
            ("Read/Write...", "读取/写入..."),
                ("Read Outline Only", "只读取大纲"),
                ("Read @file Nodes", "读取 @file 结点"),
                ("Write Dirty @file Nodes", "保存改动的 @file 结点"),
                ("Write missing @file Nodes", "保存缺少的(missing) @file 结点"),
                ("Write Outline Only", "仅保存大纲"),
                ("Write @file Nodes", "保存 @file 结点"),
                ("Write 4.x Derived Files", "保存 4.x 版本的文件"),
                ("Write 3.x Derived Files", "保存 3.x 版本的文件"),
            ("Tangle...", "Tangle 操作..."),
                ("Tangle All", "全部 Tangle"),
                ("Tangle Marked", "只 Tangle 书签结点"),
                ("Tangle", "Tangle 当前结点"),
            ("Untangle...", "Untangle 操作..."),
                ("Untangle All", "全部 Untangle"),
                ("Untangle Marked", "只 Untangle 书签结点"),
                ("Untangle", "Untangle 当前结点"),
            ("Import...", "导入..."),
                ("Import Derived File", "导入生成的文件"),
                ("Import To @file", "导入到 @file"),
                ("Import To @root", "导入到 @root"),
                ("Import CWEB Files", "导入 CWEB 文件"),
                ("Import noweb Files", "导入 noweb 文件"),
                ("Import Flattened Outline", "导入平坦 (Flattened) 大纲文件 (MORE 格式)"),
            ("Export...", "导出..."),
                ("Export Headlines", "导出标题 (Headlines)"),
                ("Outline To CWEB", "导出大纲到 CWEB"),
                ("Outline To Noweb", "导出大纲到 Noweb"),
                ("Flatten Outline", "导出平坦 (Flattened) 大纲 (MORE 格式)"),
                ("Remove Sentinels", "删除导出文件中的特殊大纲标记 (Sentinelles)"),
                ("Weave", "导出为 Weave 格式 (Listing)"),
                ("Export all to AsciiDoc", "全部导出为 AsciiDoc 文件"),
                ("Export current tree to AsciiDoc", "将当前树导出为 AsciiDoc 文件"),
            ("Exit", "退出"),
        #@+node:ekr.20040828105233.3: *3* edit menu
        ("Edit", "Edit编辑"),
            ("Undo Typing", "撤销键入"),
            ("Undo Cut Node", "撤销剪切结点"),
            ("Redo Typing", "重做键入"),
            ("Can't Undo", "无法撤销"),
            ("Can't Redo", "无法重做"),
            ("Cut", "剪切"),
            ("Copy", "复制"),
            ("Paste", "粘贴"),
            ("Delete", "删除"),
            ("Select All", "全选"),
            ("Edit Body...", "编辑文本域..."),
                ("Extract Section", "Extract Section"),
                ("Extract Names", "Extract Names"),
                ("Extract", "Extract"),
                ("Convert All Blanks", "Convert All Blanks"),
                ("Convert All Tabs", "Convert All Tabs"),
                ("Convert Blanks", "Convert Blanks"),
                ("Convert Tabs", "Convert Tabs"),
                ("Insert Body Time/Date", "插入当前日期/时间"),
                ("Reformat Paragraph", "重新格式化段落"),
                ("Indent", "增加缩进"),
                ("Unindent", "减少缩进"),
                ("Match Brackets", "括号匹配"),  #  <({["), #EKR
            ("Edit Headline...", "编辑标题..."),
                ("Edit Headline", "编辑标题"),
                ("End Edit Headline", "结束编辑标题"),
                ("Abort Edit Headline", "放弃编辑标题"),
                ("Insert Headline Time/Date", "插入当前日期/时间"),
                ("Toggle Angle Brackets", "切换尖括号标记"),
            ("Find...", "查找..."),
                ("Find Panel", "查找对话框"),
                ("Find Next", "查找下一个"),
                ("Find Previous", "查找前一个"),
                ("Replace", "替换"),
                ("Replace, Then Find", "替换后查找"),
            ("Go To Line Number", "跳转到行..."),
            ("Execute Script", "执行Python脚本"),
            ("Set Font...", "设置字体..."),
            ("Set Colors...", "设置颜色..."),
            ("Show Invisibles", "显示不可见域"),
            ("Hide Invisibles", "隐藏不可见域"),
            ("Preferences", "偏好设置"),
        #@+node:ekr.20040828105233.4: *3* outline menu
        ("Outline", "Outline大纲"),
            ("Cut Node", "剪切结点"),
            ("Copy Node", "拷贝结点"),
            ("Paste Node", "粘贴结点"),
            ("Delete Node", "删除结点"),
            ("Insert Node", "插入结点"),
            ("Clone Node", "克隆结点"),
            ("Sort Children", "排序孩子结点"),
            ("Sort Siblings", "排序兄弟结点"),
            ("Check Outline", "校验大纲"),
            ("Dump Outline", "大纲转储 (Dump)"),
            ("Hoist", "提升结点 (Hoist)"),
            ("De-Hoist", "下降结点 (De-Hoist)"),
            ("Expand/Contract...", "扩展/收缩"),
                ("Contract All", "全部收缩"),
                ("Contract Node", "收缩当前结点"),
                ("Contract Parent", "收缩父结点"),
                ("Expand Prev Level", "扩展到上一级"),
                ("Expand Next Level", "扩展到下一级"),
                ("Expand To Level 1", "扩展到第1级"),
                ("Expand To Level 2", "扩展到第2级"),
                ("Expand To Level 3", "扩展到第3级"),
                ("Expand To Level 4", "扩展到第4级"),
                ("Expand To Level 5", "扩展到第5级"),
                ("Expand To Level 6", "扩展到第6级"),
                ("Expand To Level 7", "扩展到第7级"),
                ("Expand To Level 8", "扩展到第8级"),
                ("Expand All", "扩展全部"),
                ("Expand Node", "扩展当前结点"),
            ("Move...", "移动..."),
                ("Move Down", "下移"),
                ("Move Left", "左移"),
                ("Move Right", "右移"),
                ("Move Up", "上移"),
                ("Promote", "Promote"),
                ("Demote", "Demote"),
            ("Mark/Unmark...", "书签功能..."),
                ("Mark", "标记书签"),
                ("Unmark", "删除书签"),
                ("Mark Subheads", "标记子标题"),
                ("Mark Changed Items", "标记已修改的结点"),
                ("Mark Changed Roots", "标记已修改的根结点 (Roots)"),
                ("Mark Clones", "标记克隆"),
                ("Unmark All", "删除所有书签"),
            ("Go To...", "跳转到..."),
                ("Go Back", "后退"),
                ("Go Forward", "前进"),
                ("Go To Next Marked", "跳转到下一个书签"),
                ("Go To Next Changed", "跳转到下一个已修改结点"),
                ("Go To Next Clone", "跳转到下一个克隆结点"),
                ("Go To First Node", "跳转到第一个结点"),
                ("Go To Last Node", "跳转到最后一个结点"),
                ("Go To Parent", "跳转到父结点"),
                ("Go To Prev Sibling", "跳转到上一个兄弟结点"),
                ("Go To Next Sibling", "跳转到下一个兄弟结点"),
                ("Go To Prev Visible", "跳转到上一个可见结点"),
                ("Go To Next Visible", "跳转到下一个可见结点"),
                ("Go To Prev Node", "跳转到上一结点"),
                ("Go To Next Node", "跳转到下一结点"),
        #@+node:ekr.20040828105233.5: *3* plugins menu
        ("Plugins", "Plugins插件"),
            ("chinese", "Chinese (汉化)"),
        #@+node:ekr.20040828105233.6: *3* window menu
        ("Window", "Window窗口"),
            ("Equal Sized Panes", "使各面板大小相等"),
            ("Toggle Active Pane", "切换激活面板"),
            ("Toggle Split Direction", "切换面板分割方向"),
            ("Cascade", "级联排列窗体"),
            ("Minimize All", "全部最小化"),
            ("Open Compare Window", "打开文件比较窗口..."),
            ("Open Python Window", "打开Python集成环境(IDLE)..."),
        #@+node:ekr.20040828105233.7: *3* help menu
        ("Help", "Help帮助"),
            ("About Leo...", "关于Leo..."),
            ("Online Home Page", "访问在线主页"),
            ("Open Online Tutorial", "访问在线教程"),
            ("Open Offline Tutorial", "访问离线教程 (CHM文件)"),
            ("Open LeoDocs.leo", "打开 LeoDocs.leo"),
            ("Open LeoConfig.leo", "打开 LeoConfig.leo"),
            ("Apply Settings", "应用设置")
        #@-others
    )

    # Call the convenience routine to do the work.
    c.frame.menu.setRealMenuNamesFromTable(table)
#@-others
#@@language python
#@@tabwidth -4
#@-leo

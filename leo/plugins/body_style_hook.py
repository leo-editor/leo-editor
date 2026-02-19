#@+leo-ver=5-thin
#@+node:swot.20250715091430.1: * @file /Users/swot/app/leo-editor/leo/plugins/body_style_hook.py
#@@language python
"""
body_style_plugin.py
"""

from leo.core import leoGlobals as g
from PyQt6.QtGui import QTextBlockFormat, QTextCursor, QFont, QTextCharFormat
from PyQt6.QtCore import QTimer

# 消除 Pyflakes 在保存时的误报
try:
    c
except NameError:
    c = None

# 配置区
STYLE_CONFIG = {
    "family": "JetBrains Mono",
    "size": 16,
    "line_height": 125,      # 125% = 1.25倍行距
    "line_height_type": 1,   # 1 = ProportionalHeight
    "letter_spacing": 105    # 105% 字间距
}

def init():
    """插件入口"""
    # 1. 针对新打开的窗口 (Ctrl+O, Ctrl+N)
    g.registerHandler('open2', on_window_init)
    
    # 2. 针对 Leo 启动时的第一个窗口
    g.registerHandler('start2', on_window_init)
    
    # 3. [关键修复] 针对插件重载时，已经存在的窗口
    # 如果你执行 reload 命令，这个循环会立即修复所有已打开的窗口
    if g.app.commanders():
        for existing_c in g.app.commanders():
            on_window_init('reload', {'c': existing_c})

    g.es("Body Style Plugin loaded (New Window Fix).")
    return True

def on_window_init(tag, keywords):
    """通用的窗口初始化函数，无论是启动、新建还是重载都走这里"""
    c = keywords.get('c')
    if not c:
        return

    # 防止重复挂载 (单例模式)
    if hasattr(c, '_body_styler'):
        # 如果是重载插件的情况，我们可能想强制刷新一下样式
        # 但不需要重新创建 Controller，直接调用 apply 即可
        c._body_styler.apply_style()
        return

    # 首次挂载
    c._body_styler = BodyStyleController(c)

class BodyStyleController:
    """
    每个 Commander 独立的样式控制器。
    """
    def __init__(self, c):
        self.c = c
        
        # 监听节点切换
        g.registerHandler('select1', self.on_select)
        
        # 启动时延时应用
        QTimer.singleShot(100, self.apply_style)

    def on_select(self, tag, keywords):
        """切换节点时应用样式"""
        if keywords.get('c') != self.c:
            return
            
        # [Fix]: 使用 0ms 延时，确保在 Leo 完成文本加载后执行
        QTimer.singleShot(0, self.apply_style)

    def get_editor(self):
        """获取 Qt editor widget"""
        try:
            return self.c.frame.body.wrapper.widget
        except AttributeError:
            return None

    def apply_style(self):
        """入口：准备字体对象并调用格式应用"""
        editor = self.get_editor()
        if not editor:
            return

        doc = editor.document()
        if not doc:
            return

        # 1. 设置 Widget 级的基础字体
        current_font = editor.font()
        # 即使字体没变，为了确保逻辑一致，也可以强制刷一次
        # 这里保留判断是为了性能，但如果发现热重载配置不生效，可以去掉这个 if
        if (current_font.family() != STYLE_CONFIG["family"] or 
            current_font.pointSize() != STYLE_CONFIG["size"]):
            
            font = QFont(STYLE_CONFIG["family"])
            font.setPointSize(STYLE_CONFIG["size"])
            font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, STYLE_CONFIG["letter_spacing"])
            
            editor.setFont(font)
            doc.setDefaultFont(font)

        # 2. 强行应用 Block 和 Char 格式
        self._apply_formats(editor, doc)

    def _apply_formats(self, editor, doc):
        """同时应用段落(行高)和字符(字间距)格式"""
        cursor = QTextCursor(doc)
        cursor.select(QTextCursor.SelectionType.Document)

        # A. 设置段落格式 (行高)
        block_fmt = QTextBlockFormat()
        block_fmt.setLineHeight(
            STYLE_CONFIG["line_height"], 
            STYLE_CONFIG["line_height_type"]
        )
        cursor.mergeBlockFormat(block_fmt)

        # B. 设置字符格式 (字间距)
        char_fmt = QTextCharFormat()
        char_fmt.setFontLetterSpacingType(QFont.SpacingType.PercentageSpacing)
        char_fmt.setFontLetterSpacing(STYLE_CONFIG["letter_spacing"])
        
        cursor.mergeCharFormat(char_fmt)
        
        # 清除选中状态
        cursor.clearSelection()
#@-leo

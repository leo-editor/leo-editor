#@+leo-ver=5-thin
#@+node:swot.20250715091430.1: * @file /Users/swot/app/leo-editor/leo/plugins/body_style_hook.py
#@@language python
"""
body_style_plugin.py
为 Leo 的 Body 区域提供一致的字体、行高和字间距设置。
修复了切换节点时行高重置的问题。
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
    "line_height": 120,      # 200% = 2.0倍行距
    "line_height_type": 1,   # 1 = ProportionalHeight
    "letter_spacing": 105    # 115% 字间距
}

def init():
    """插件入口"""
    g.registerHandler('start2', on_start)
    g.es("Body Style Plugin loaded (Timer fixed).")
    return True

def on_start(tag, keywords):
    """当新的 Commander 创建时调用"""
    c = keywords.get('c')
    if c:
        # 建议检查是否已经存在实例，防止重复绑定（虽然一般不会发生）
        if not hasattr(c, '_body_styler'):
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

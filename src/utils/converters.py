import html
import json
import re

from pydantic import BaseModel


class Converter(object):
    @classmethod
    def txt_to_html(cls, txt: str) -> str:
        # 转义 HTML 特殊字符
        escaped_txt = html.escape(txt)

        # 按段落拆分（两行换行符视为段落）
        paragraphs = [p.strip() for p in escaped_txt.split('\n\n') if p.strip()]

        # 构造 HTML 段落
        html_paragraphs = []
        for para in paragraphs:
            replaced = para.replace('\n', '<br>')
            html_paragraphs.append(f"<p>{replaced}</p>")

        return '\n'.join(html_paragraphs)

    @staticmethod
    def nano_to_milli_seconds(nanoseconds: int) -> float:
        milliseconds = nanoseconds / 1_000_000
        return round(milliseconds, 2)

    @staticmethod
    def deepseek_format(text: str) -> str:
        """
        清除 <think> 标签及其内容
        示例："<think>这里是思考内容</think>\n\n你好" => "你好"
        """
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    @staticmethod
    def clean_text(text: str) -> str:
        # 保留中文、英文字母、数字、空格、换行符，以及中英文常见标点
        return re.sub(r"[^\u4e00-\u9fffA-Za-z0-9，。！？：；、“”‘’\"'.,?!:;\s\n]", "", text)

    @staticmethod
    def format_list(_l: list) -> str:
        return "\n".join([str(i) for i in _l])


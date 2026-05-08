from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, PyMuPDFLoader, PDFPlumberLoader
import difflib
import html
#这个地址替换成你下载的论文位置，论文地址：https://arxiv.org/pdf/1706.03762
file_path = "../data/1706.03762v7.pdf"

# 加载文档
loaders = {
    'PyPDFLoader': PyPDFLoader(file_path),
    'PyMuPDFLoader': PyMuPDFLoader(file_path),
    'PDFPlumberLoader': PDFPlumberLoader(file_path)
}

docs = {name: loader.load() for name, loader in loaders.items()}

# 三列并排时每个 loader 的强调色（边框 / 标签）
LOADER_THEME = (
    ("#2563eb", "#dbeafe", "PyPDF"),
    ("#7c3aed", "#ede9fe", "MuPDF"),
    ("#0d9488", "#ccfbf1", "Plumber"),
)


COMPARE_REPORT_CSS = """
    <style>
        .pdf-compare {
            font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
            max-width: 1440px;
            margin: 0 auto;
            padding: 28px 24px 48px;
            color: #0f172a;
            background: linear-gradient(165deg, #f8fafc 0%, #eef2ff 45%, #f1f5f9 100%);
            min-height: 100vh;
            box-sizing: border-box;
        }
        .pdf-hero {
            background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #1e3a5f 100%);
            color: #f8fafc;
            padding: 22px 26px;
            border-radius: 14px;
            margin-bottom: 28px;
            box-shadow: 0 12px 40px rgba(15, 23, 42, 0.25);
        }
        .pdf-hero h1 { margin: 0 0 6px; font-size: 1.35rem; font-weight: 700; letter-spacing: -0.02em; }
        .pdf-hero p { margin: 0; opacity: 0.88; font-size: 0.9rem; }
        .pdf-hero .warn { margin-top: 10px; font-size: 0.78rem; color: #fde68a; opacity: 1; }
        .page-toc {
            background: #fff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 14px 18px;
            margin-bottom: 28px;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
        }
        .page-toc-title { font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b; margin-bottom: 10px; }
        .page-toc-links { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
        .page-toc a {
            display: inline-block;
            padding: 6px 11px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
            text-decoration: none;
            background: #f1f5f9;
            color: #334155;
            border: 1px solid #e2e8f0;
        }
        .page-toc a:hover { background: #e2e8f0; color: #0f172a; }
        .page-sheet {
            margin-bottom: 40px;
            padding-bottom: 32px;
            border-bottom: 2px dashed #cbd5e1;
            scroll-margin-top: 16px;
        }
        .page-sheet:last-of-type { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
        .page-sheet-title {
            font-size: 1.15rem;
            font-weight: 800;
            margin: 0 0 20px;
            padding: 12px 16px;
            background: linear-gradient(90deg, #e0e7ff 0%, #fff 55%);
            border-radius: 10px;
            border-left: 5px solid #6366f1;
            color: #1e1b4b;
            letter-spacing: -0.02em;
        }
        .section { margin-bottom: 32px; }
        .section-title {
            font-size: 1.05rem;
            font-weight: 700;
            margin: 0 0 14px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e2e8f0;
            color: #1e293b;
            letter-spacing: -0.02em;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
        }
        @media (max-width: 900px) {
            .stats-grid { grid-template-columns: 1fr; }
        }
        .stat-card {
            background: #fff;
            padding: 18px 18px 16px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
            border-top: 4px solid var(--accent, #64748b);
        }
        .stat-card .stat-label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; color: #64748b; font-weight: 600; }
        .stat-card .stat-name { font-size: 0.95rem; font-weight: 700; color: #0f172a; margin: 6px 0 12px; }
        .stat-value { font-size: 1.85rem; font-weight: 800; color: var(--accent, #2563eb); letter-spacing: -0.03em; line-height: 1.1; }
        .stat-meta { font-size: 0.8rem; color: #64748b; margin-top: 10px; line-height: 1.5; }
        .triple-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
            align-items: stretch;
        }
        @media (max-width: 1100px) {
            .triple-grid { grid-template-columns: 1fr; }
        }
        .triple-col {
            background: #fff;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 6px 20px rgba(15, 23, 42, 0.07);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            min-height: 320px;
            border-top: 4px solid var(--accent);
        }
        .triple-head {
            padding: 12px 14px;
            background: var(--head-bg);
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
        }
        .triple-head strong { font-size: 0.82rem; color: #0f172a; }
        .triple-badge {
            font-size: 0.68rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 999px;
            background: #fff;
            color: var(--accent);
            border: 1px solid rgba(0,0,0,0.06);
        }
        .triple-body {
            flex: 1;
            margin: 0;
            padding: 14px;
            font-family: ui-monospace, "Cascadia Code", "SF Mono", Consolas, monospace;
            font-size: 11.5px;
            line-height: 1.55;
            white-space: pre-wrap;
            word-break: break-word;
            overflow: auto;
            max-height: 520px;
            background: linear-gradient(180deg, #fafafa 0%, #fff 24px);
            color: #334155;
            border-top: none;
        }
        .triple-foot {
            padding: 8px 14px;
            font-size: 0.72rem;
            color: #94a3b8;
            background: #f8fafc;
            border-top: 1px solid #f1f5f9;
        }
        .diff-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
        }
        @media (max-width: 1100px) {
            .diff-grid { grid-template-columns: 1fr; }
        }
        .diff-panel {
            background: #fff;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            overflow: hidden;
            box-shadow: 0 6px 20px rgba(15, 23, 42, 0.06);
        }
        .diff-header {
            background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%);
            padding: 12px 14px;
            font-weight: 700;
            font-size: 0.82rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
            border-bottom: 1px solid #cbd5e1;
        }
        .diff-count { color: #dc2626; font-variant-numeric: tabular-nums; font-weight: 800; }
        .diff-body { padding: 12px; max-height: 420px; overflow: auto; background: #0f172a; }
        .diff-same { color: #86efac; font-size: 0.88rem; padding: 8px; text-align: center; }
        .diff-lines { font-family: ui-monospace, Consolas, monospace; font-size: 11px; line-height: 1.45; }
        .diff-line { padding: 2px 8px; white-space: pre-wrap; word-break: break-all; border-left: 3px solid transparent; }
        .diff-add { background: rgba(34, 197, 94, 0.18); color: #bbf7d0; border-left-color: #22c55e; }
        .diff-del { background: rgba(239, 68, 68, 0.2); color: #fecaca; border-left-color: #ef4444; }
        .diff-hunk { background: rgba(250, 204, 21, 0.15); color: #fde047; border-left-color: #eab308; font-weight: 600; }
        .diff-ctx { color: #94a3b8; border-left-color: #475569; }
        .details-wrap { background: #fff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 2px 12px rgba(15, 23, 42, 0.04); }
        details.details-wrap summary {
            padding: 14px 18px;
            cursor: pointer;
            font-weight: 700;
            font-size: 0.88rem;
            background: #f8fafc;
            list-style: none;
        }
        details.details-wrap summary::-webkit-details-marker { display: none; }
        .text-preview { white-space: pre-wrap; font-family: ui-monospace, Consolas, monospace; font-size: 11px; line-height: 1.55; padding: 16px 18px; color: #334155; max-height: 400px; overflow: auto; }
    </style>
"""


def doc_page_count(docs_dict: dict) -> tuple[int, dict[str, int]]:
    """返回用于对比的安全页数（各 loader 文档页数的最小值）及各自页数。"""
    counts = {name: len(docs) for name, docs in docs_dict.items()}
    n = min(counts.values()) if counts else 0
    return n, counts


def create_diff_view(text1, text2, label1="A", label2="B") -> str:
    """生成两个文本的 HTML 差异对比（高对比行样式）。"""
    diff = list(
        difflib.unified_diff(
            text1.splitlines(keepends=True),
            text2.splitlines(keepends=True),
            fromfile=label1,
            tofile=label2,
            lineterm="",
        )
    )

    if not diff:
        return (
            f'<div class="diff-same">✓ <strong>{html.escape(label1)}</strong> 与 '
            f'<strong>{html.escape(label2)}</strong> 完全一致</div>'
        )

    html_output = ['<div class="diff-lines">']
    for line in diff[2:]:
        escaped = html.escape(line)
        if line.startswith("+"):
            html_output.append(f'<div class="diff-line diff-add">{escaped}</div>')
        elif line.startswith("-"):
            html_output.append(f'<div class="diff-line diff-del">{escaped}</div>')
        elif line.startswith("@@"):
            html_output.append(f'<div class="diff-line diff-hunk">{escaped}</div>')
        else:
            html_output.append(f'<div class="diff-line diff-ctx">{escaped}</div>')
    html_output.append("</div>")
    return "".join(html_output)

def render_compare_page_sections(
    docs_dict: dict,
    page_idx: int,
    *,
    preview_len: int = 3500,
) -> str:
    """
    渲染单页的统计、并排预览、两两差异、折叠全文（不含外层样式与页眉）。

    @param docs_dict - 各 loader 名称到 Document 列表的映射
    @param page_idx - 页码（0-based）
    @param preview_len - 并排预览最大字符数
    @returns 单页 HTML 片段
    """
    names = list(docs_dict.keys())
    texts = {name: docs_dict[name][page_idx].page_content for name in names}

    stats = []
    for name, text in texts.items():
        stats.append(
            {
                "Loader": name,
                "字符数": len(text),
                "行数": len(text.splitlines()),
                "空行数": text.splitlines().count(""),
                "非空字符": len(text.replace("\n", "").replace(" ", "")),
            }
        )

    html_parts: list[str] = []

    html_parts.append(
        '<section class="section"><h2 class="section-title">统计概览（三列）</h2><div class="stats-grid">'
    )
    for idx, stat in enumerate(stats):
        accent, soft, short = LOADER_THEME[idx % len(LOADER_THEME)]
        html_parts.append(
            f"""
        <div class="stat-card" style="--accent:{accent}">
            <div class="stat-label">{html.escape(short)}</div>
            <div class="stat-name">{html.escape(stat["Loader"])}</div>
            <div class="stat-value">{stat["字符数"]:,}</div>
            <div class="stat-meta">字符总数<br/>{stat["行数"]:,} 行 · 有效字符 {stat["非空字符"]:,} · 空行 {stat["空行数"]:,}</div>
        </div>
        """
        )
    html_parts.append("</div></section>")

    html_parts.append(
        '<section class="section"><h2 class="section-title">并排原文预览（同一行三列）</h2><div class="triple-grid">'
    )
    for idx, name in enumerate(names):
        accent, soft, short = LOADER_THEME[idx % len(LOADER_THEME)]
        text = texts[name]
        preview = text[:preview_len] + ("… (截断)" if len(text) > preview_len else "")
        html_parts.append(
            f"""
        <div class="triple-col" style="--accent:{accent};--head-bg:{soft}">
            <div class="triple-head">
                <strong>{html.escape(name)}</strong>
                <span class="triple-badge">{html.escape(short)}</span>
            </div>
            <pre class="triple-body">{html.escape(preview)}</pre>
            <div class="triple-foot">共 {len(text):,} 字符 · 预览前 {min(len(text), preview_len):,} 字符</div>
        </div>
        """
        )
    html_parts.append("</div></section>")

    html_parts.append(
        '<section class="section"><h2 class="section-title">两两差异（三列一行）</h2><div class="diff-grid">'
    )
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            diff_lines = [
                ln
                for ln in difflib.unified_diff(
                    texts[names[i]].splitlines(),
                    texts[names[j]].splitlines(),
                )
                if ln.startswith("+") or ln.startswith("-")
            ]
            html_parts.append(
                f"""
            <div class="diff-panel">
                <div class="diff-header">
                    <span>{html.escape(names[i])} ↔ {html.escape(names[j])}</span>
                    <span class="diff-count">Δ {len(diff_lines)} 行</span>
                </div>
                <div class="diff-body">
                    {create_diff_view(texts[names[i]], texts[names[j]], names[i], names[j])}
                </div>
            </div>
            """
            )
    html_parts.append("</div></section>")

    html_parts.append('<section class="section"><h2 class="section-title">完整文本（折叠）</h2>')
    for idx, name in enumerate(names):
        text = texts[name]
        accent, _, short = LOADER_THEME[idx % len(LOADER_THEME)]
        html_parts.append(
            f"""
        <details class="details-wrap" style="margin-bottom:12px;border-top:3px solid {accent}">
            <summary>{html.escape(name)} · {html.escape(short)} · {len(text):,} 字符</summary>
            <div class="text-preview">{html.escape(text)}</div>
        </details>
        """
        )
    html_parts.append("</section>")
    return "".join(html_parts)


def compare_all(
    docs_dict: dict,
    page_idx: int = 0,
    *,
    preview_len: int = 3500,
) -> str:
    """
    单页对比报告 HTML 片段（兼容旧用法：默认只生成一页）。

    @param docs_dict - 各 loader 名称到 Document 列表的映射
    @param page_idx - 页码（0-based）
    @param preview_len - 并排预览最大字符数
    """
    return compare_report_html(
        docs_dict,
        page_indices=[page_idx],
        preview_len=preview_len,
    )


def compare_report_html(
    docs_dict: dict,
    *,
    page_indices: list[int] | None = None,
    preview_len: int = 3500,
) -> str:
    """
    生成完整对比报告 HTML 片段（含一份样式）。`page_indices` 为 None 时表示每一页都生成。

    @param docs_dict - 各 loader 名称到 Document 列表的映射
    @param page_indices - 要输出的页索引列表（0-based）；None 表示全部页
    @param preview_len - 并排预览最大字符数
    """
    names = list(docs_dict.keys())
    n_safe, counts = doc_page_count(docs_dict)

    if page_indices is None:
        pages = list(range(n_safe))
    else:
        pages = [p for p in page_indices if 0 <= p < n_safe]

    parts: list[str] = [COMPARE_REPORT_CSS, '<div class="pdf-compare">']

    mismatch = len(set(counts.values())) > 1
    warn_html = ""
    if mismatch:
        detail = " · ".join(f"{html.escape(k)} {v} 页" for k, v in counts.items())
        warn_html = (
            f'<p class="warn">各 Loader 页数不一致，已按最短 <strong>{n_safe}</strong> 页对齐对比。</p>'
            f'<p class="warn">{detail}</p>'
        )

    if len(pages) == 1:
        p0 = pages[0]
        parts.append(f"""
        <header class="pdf-hero">
            <h1>PDF 解析对比</h1>
            <p>第 <strong>{p0 + 1}</strong> 页 · 三种 Loader 同一行并排，便于肉眼对齐差异</p>
            {warn_html}
        </header>
        <article class="page-sheet" id="page-{p0 + 1}">
            {render_compare_page_sections(docs_dict, p0, preview_len=preview_len)}
        </article>
        """)
    else:
        parts.append(f"""
        <header class="pdf-hero">
            <h1>PDF 解析对比 · 全文</h1>
            <p>共 <strong>{len(pages)}</strong> 页（与各 Loader 对齐后的最短页数 <strong>{n_safe}</strong>）· 下方目录可跳转</p>
            {warn_html}
        </header>
        """)
        parts.append('<nav class="page-toc" aria-label="页码目录">')
        parts.append('<div class="page-toc-title">跳转页面</div><div class="page-toc-links">')
        for p in pages:
            parts.append(f'<a href="#page-{p + 1}">第 {p + 1} 页</a>')
        parts.append("</div></nav>")
        for p in pages:
            parts.append(f"""
            <article class="page-sheet" id="page-{p + 1}">
                <h2 class="page-sheet-title">第 {p + 1} 页</h2>
                {render_compare_page_sections(docs_dict, p, preview_len=preview_len)}
            </article>
            """)

    parts.append("</div>")
    return "".join(parts)


def write_compare_html(
    docs_dict: dict,
    page_idx: int | None = None,
    out_path: str | Path | None = None,
    *,
    preview_len: int = 3500,
) -> Path:
    """
    将对比结果写入独立可打开的 HTML 文件。

    @param docs_dict - 各 loader 名称到 Document 列表的映射
    @param page_idx - 仅输出该页（0-based）；为 None 时输出全部页
    @param out_path - 输出路径；默认单页为 `pdf_loader_compare_p{n}.html`，全文为 `pdf_loader_compare_all.html`
    @param preview_len - 并排预览最大字符数
    @returns 实际写入的文件路径
    """
    if page_idx is not None:
        body = compare_report_html(docs_dict, page_indices=[page_idx], preview_len=preview_len)
        title_page = page_idx + 1
        default_name = f"pdf_loader_compare_p{title_page}.html"
    else:
        body = compare_report_html(docs_dict, page_indices=None, preview_len=preview_len)
        title_page = None
        default_name = "pdf_loader_compare_all.html"

    path = Path(out_path) if out_path is not None else Path(__file__).resolve().parent / default_name

    title = (
        f"PDF 解析对比 - 第 {title_page} 页"
        if title_page is not None
        else "PDF 解析对比 - 全文"
    )
    full = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
</head>
<body>
{body}
</body>
</html>
"""
    path.write_text(full, encoding="utf-8")
    return path.resolve()


if __name__ == "__main__":
    out_file = write_compare_html(docs, page_idx=1)
    print(f"已写入（全文）: {out_file}")

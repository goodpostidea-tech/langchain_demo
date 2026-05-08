## PDF Loader 对比脚本说明

在同一 PDF 上并行使用 **PyPDFLoader**、**PyMuPDFLoader**、**PDFPlumberLoader** 加载文档，生成可在浏览器中打开的 **HTML 对比报告**。

**报告内容**

- **统计概览**：三种 Loader 当前页的字符数、行数、有效字符、空行等（三列并排）。
- **并排原文预览**：同一页正文三列对照，便于肉眼对齐差异（可按 `preview_len` 截断预览长度）。
- **两两差异**：统一 diff 样式展示 Loader 之间的文本差异（三列一组）。
- **完整文本**：按 Loader 折叠展示该页全文。

**全文模式**

- `write_compare_html(docs, page_idx=None)` 默认输出 **`pdf_loader_compare_all.html`**，逐页生成上述区块。
- 顶部提供 **页码锚点目录**（`#page-1` …）；各 Loader **页数不一致**时，按 **最短页数** 对齐并在页眉提示各 Loader 页数。

**单页模式**

- `write_compare_html(docs, page_idx=n)` 仅生成第 `n+1` 页，默认文件名为 **`pdf_loader_compare_p{n+1}.html`**。

**运行**

```bash
uv run python pdf_loader_parser.py
```

依赖项目中的 `langchain-community` 及对应 PDF 库（如 `pypdf`、`pymupdf`、`pdfplumber`）。长文档全文 HTML 体积可能较大，打开时请注意浏览器性能。

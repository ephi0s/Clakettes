import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_quill/flutter_quill.dart';

/// Extrae el texto plano de un contenido que puede ser JSON de Delta de Quill
/// o texto plano/markdown (compatibilidad con publicaciones existentes).
String plainTextFrom(String content) {
  try {
    final decoded = jsonDecode(content);
    if (decoded is List) {
      final doc = Document.fromJson(decoded);
      return doc.toPlainText();
    }
  } catch (_) {}
  return content;
}

/// Convierte cualquier texto (delta JSON o texto plano) en un [Document] de Quill.
Document documentFrom(String content) {
  try {
    final decoded = jsonDecode(content);
    if (decoded is List) {
      return Document.fromJson(decoded);
    }
  } catch (_) {}
  return Document()..insert(0, content);
}

/// Editor de texto enriquecido (WYSIWYG) basado en flutter_quill.
///
/// - `readOnly: false`: muestra barra de herramientas y permite editar.
/// - `readOnly: true`: solo lectura, para mostrar publicaciones existentes.
/// El contenido se intercambia como JSON de Delta de Quill (String).
class RichTextEditor extends StatefulWidget {
  final String initialContent;
  final bool readOnly;
  final ValueChanged<String>? onContentChanged;
  final FocusNode? focusNode;
  final bool autoFocus;

  const RichTextEditor({
    super.key,
    required this.initialContent,
    this.readOnly = false,
    this.onContentChanged,
    this.focusNode,
    this.autoFocus = false,
  });

  @override
  State<RichTextEditor> createState() => _RichTextEditorState();
}

class _RichTextEditorState extends State<RichTextEditor> {
  late QuillController _controller;
  late ScrollController _scrollController;

  @override
  void initState() {
    super.initState();
    _scrollController = ScrollController();
    _controller = QuillController(
      document: documentFrom(widget.initialContent),
      selection: const TextSelection.collapsed(offset: 0),
      readOnly: widget.readOnly,
    );
    _controller.addListener(() {
      if (widget.onContentChanged != null) {
        widget.onContentChanged!(jsonEncode(_controller.document.toDelta().toJson()));
      }
    });
    if (widget.autoFocus) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          widget.focusNode?.requestFocus();
        }
      });
    }
  }

  @override
  void didUpdateWidget(covariant RichTextEditor oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.initialContent != widget.initialContent) {
      _controller.document = documentFrom(widget.initialContent);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    final editor = QuillEditor.basic(
      controller: _controller,
      focusNode: widget.focusNode,
      scrollController: _scrollController,
    );

    if (widget.readOnly) {
      return Semantics(
        label: plainTextFrom(widget.initialContent),
        child: editor,
      );
    }

    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        QuillSimpleToolbar(
          controller: _controller,
          config: const QuillSimpleToolbarConfig(
            showFontFamily: false,
            showFontSize: false,
            showSmallButton: false,
            showLineHeightButton: false,
            showAlignmentButtons: false,
            showCodeBlock: false,
            showQuote: false,
            showIndent: false,
            showSubscript: false,
            showSuperscript: false,
            showSearchButton: false,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          decoration: BoxDecoration(
            border: Border.all(color: colorScheme.outlineVariant),
            borderRadius: BorderRadius.circular(8),
          ),
          child: editor,
        ),
      ],
    );
  }
}

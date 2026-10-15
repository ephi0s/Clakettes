import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

Future<void> _openLink(String url) async {
  var uri = Uri.tryParse(url.trim());
  if (uri != null && !uri.hasScheme) uri = Uri.parse('https://${url.trim()}');
  if (uri != null && await canLaunchUrl(uri)) {
    await launchUrl(uri, mode: LaunchMode.externalApplication);
  }
}

List<InlineSpan> _parseInline(String text, TextStyle? base, Color linkColor) {
  final spans = <InlineSpan>[];
  final pattern = RegExp(r'(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`|\[.+?\]\(.+?\))');
  int cursor = 0;
  for (final match in pattern.allMatches(text)) {
    if (match.start > cursor) {
      spans.add(TextSpan(text: text.substring(cursor, match.start), style: base));
    }
    final token = match.group(0)!;
    if (token.startsWith('**')) {
      spans.add(TextSpan(text: token.substring(2, token.length - 2), style: base?.copyWith(fontWeight: FontWeight.w700) ?? const TextStyle(fontWeight: FontWeight.w700)));
    } else if (token.startsWith('*')) {
      spans.add(TextSpan(text: token.substring(1, token.length - 1), style: base?.copyWith(fontStyle: FontStyle.italic) ?? const TextStyle(fontStyle: FontStyle.italic)));
    } else if (token.startsWith('`')) {
      spans.add(TextSpan(
        text: token.substring(1, token.length - 1),
        style: (base ?? const TextStyle()).copyWith(fontFamily: 'monospace', backgroundColor: linkColor.withAlpha(25)),
      ));
    } else {
      final linkMatch = RegExp(r'\[(.+?)\]\((.+?)\)').firstMatch(token);
      if (linkMatch != null) {
        final label = linkMatch.group(1)!;
        final url = linkMatch.group(2)!;
        spans.add(TextSpan(
          text: label,
          style: (base ?? const TextStyle()).copyWith(color: linkColor, decoration: TextDecoration.underline),
          recognizer: TapGestureRecognizer()..onTap = () => _openLink(url),
        ));
      } else {
        spans.add(TextSpan(text: token, style: base));
      }
    }
    cursor = match.end;
  }
  if (cursor < text.length) {
    spans.add(TextSpan(text: text.substring(cursor), style: base));
  }
  return spans;
}

class MarkdownText extends StatelessWidget {
  final String data;
  final TextStyle? style;
  final int? maxLines;

  const MarkdownText({super.key, required this.data, this.style, this.maxLines});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final base = style ?? theme.textTheme.bodyMedium;
    final linkColor = theme.colorScheme.primary;
    final blocks = <Widget>[];
    final urlPattern = RegExp(r'https?://\S+');
    for (final rawLine in data.split('\n')) {
      final line = rawLine.trimRight();
      if (line.trim().isEmpty) {
        blocks.add(const SizedBox(height: 6));
        continue;
      }
      if (line.startsWith('### ')) {
        blocks.add(Padding(
          padding: const EdgeInsets.only(top: 4),
          child: Text(line.substring(4), style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700)),
        ));
        continue;
      }
      if (line.startsWith('## ')) {
        blocks.add(Padding(
          padding: const EdgeInsets.only(top: 4),
          child: Text(line.substring(3), style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
        ));
        continue;
      }
      if (line.startsWith('# ')) {
        blocks.add(Padding(
          padding: const EdgeInsets.only(top: 4),
          child: Text(line.substring(2), style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w700)),
        ));
        continue;
      }
      if (line.trimLeft().startsWith('- ') || line.trimLeft().startsWith('* ')) {
        final item = line.trimLeft().substring(2);
        blocks.add(Padding(
          padding: const EdgeInsets.only(left: 8, top: 2),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('•  ', style: base?.copyWith(fontWeight: FontWeight.w700)),
              Expanded(child: _InlineLine(text: item, base: base, linkColor: linkColor)),
            ],
          ),
        ));
        continue;
      }
      blocks.add(_InlineLine(text: line, base: base, linkColor: linkColor, urlPattern: urlPattern));
    }
    return Semantics(
      label: data,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisSize: MainAxisSize.min, children: blocks),
    );
  }
}

class _InlineLine extends StatelessWidget {
  final String text;
  final TextStyle? base;
  final Color linkColor;
  final RegExp? urlPattern;

  const _InlineLine({required this.text, required this.base, required this.linkColor, this.urlPattern});

  @override
  Widget build(BuildContext context) {
    final spans = _parseInline(text, base, linkColor);
    final pattern = urlPattern ?? RegExp(r'https?://\S+');
    final expanded = <InlineSpan>[];
    for (final span in spans) {
      if (span is! TextSpan || span.text == null || span.recognizer != null) {
        expanded.add(span);
        continue;
      }
      final t = span.text!;
      int cursor = 0;
      for (final m in pattern.allMatches(t)) {
        if (m.start > cursor) expanded.add(TextSpan(text: t.substring(cursor, m.start), style: span.style));
        final url = m.group(0)!;
        expanded.add(TextSpan(
          text: url,
          style: (span.style ?? const TextStyle()).copyWith(color: linkColor, decoration: TextDecoration.underline),
          recognizer: TapGestureRecognizer()..onTap = () => _openLink(url),
        ));
        cursor = m.end;
      }
      if (cursor < t.length) expanded.add(TextSpan(text: t.substring(cursor), style: span.style));
    }
    return RichText(text: TextSpan(children: expanded, style: base));
  }
}

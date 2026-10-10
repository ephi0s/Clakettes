import 'package:flutter/material.dart';
import 'reusable_widgets.dart';

Future<void> showLoginPrompt(
  BuildContext context, {
  required VoidCallback onLogin,
  String? title,
  String? subtitle,
}) {
  return showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
    ),
    builder: (ctx) => LoginPromptSheet(
      onLogin: onLogin,
      title: title,
      subtitle: subtitle,
    ),
  );
}

import 'package:material_ui/material_ui.dart';
import 'main_scaffold.dart';

/// Widget raíz que muestra directamente el scaffold principal.
///
/// El login es opcional y se puede acceder desde dentro de la app.
class AuthWrapper extends StatefulWidget {
  const AuthWrapper({super.key});

  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  @override
  Widget build(BuildContext context) {
    return const MainScaffold();
  }
}

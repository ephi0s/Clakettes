import 'package:flutter/material.dart';

/// Envuelve un hijo con un efecto animado de brillo/esqueleto para marcadores de carga.
///
/// Aplica un degradado lineal en movimiento mediante ShaderMask sobre el hijo;
/// combínalo con bloques de esqueleto para indicar que el contenido aún se está cargando.
class ShimmerLoading extends StatefulWidget {
  final Widget child;

  const ShimmerLoading({super.key, required this.child});

  @override
  State<ShimmerLoading> createState() => _ShimmerLoadingState();
}

class _ShimmerLoadingState extends State<ShimmerLoading> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(vsync: this, duration: const Duration(milliseconds: 1500))..repeat();
    _animation = Tween<double>(begin: -2, end: 2).animate(CurvedAnimation(parent: _controller, curve: Curves.easeInOutSine));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return ListenableBuilder(
      listenable: _animation,
      builder: (context, child) {
        return ShaderMask(
          shaderCallback: (bounds) {
            return LinearGradient(
              begin: Alignment(_animation.value - 1, 0),
              end: Alignment(_animation.value, 0),
              colors: [
                colorScheme.surfaceContainerHighest.withAlpha(50),
                colorScheme.surfaceContainerHighest.withAlpha(120),
                colorScheme.surfaceContainerHighest.withAlpha(50),
              ],
              stops: const [0.3, 0.5, 0.7],
            ).createShader(bounds);
          },
          blendMode: BlendMode.srcOver,
          child: child,
        );
      },
      child: widget.child,
    );
  }
}

/// Esqueleto de lista de marcador con filas brillantes, con el tamaño de las tarjetas de elementos de lista.
///
/// Úsalo mientras una lista se está cargando para reducir el salto de layout;
/// el número de elementos es configurable mediante [itemCount].
class ListSkeleton extends StatelessWidget {
  final int itemCount;

  const ListSkeleton({super.key, this.itemCount = 5});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      itemCount: itemCount,
      itemBuilder: (context, i) => Padding(
        padding: const EdgeInsets.only(bottom: 8),
        child: ShimmerLoading(
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: colorScheme.surface,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: colorScheme.outlineVariant.withAlpha(30)),
            ),
            child: Row(
              children: [
                Container(
                  width: 44, height: 44,
                  decoration: BoxDecoration(
                    color: colorScheme.surfaceContainerHighest.withAlpha(100),
                    borderRadius: BorderRadius.circular(22),
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        height: 14, width: 160,
                        decoration: BoxDecoration(
                          color: colorScheme.surfaceContainerHighest.withAlpha(100),
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Container(
                        height: 10, width: 100,
                        decoration: BoxDecoration(
                          color: colorScheme.surfaceContainerHighest.withAlpha(80),
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  width: 20, height: 20,
                  decoration: BoxDecoration(
                    color: colorScheme.surfaceContainerHighest.withAlpha(100),
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

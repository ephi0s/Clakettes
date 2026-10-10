import 'dart:async';
import 'package:flutter/cupertino.dart' show CupertinoPageTransitionsBuilder;
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'l10n/app_localizations.dart';
import 'services/database_service.dart';
import 'services/offline_cache_service.dart';
import 'services/sync_queue_service.dart';
import 'services/connectivity_monitor.dart';
import 'services/locale_service.dart';
import 'services/notification_service.dart';
import 'auth_wrapper.dart';

/// Punto de entrada de la aplicación.
///
/// El orden de inicialización importa:
/// 1. DatabaseService.init() - abre las cajas de Hive (festivals, users, shortfilms, messages)
/// 2. OfflineCacheService.init() - prepara la caché local
/// 3. SyncQueueService.init() - restaura las operaciones de sincronización pendientes
/// 4. ConnectivityMonitor.start() - comienza a escuchar el estado de red
/// 5. LocaleService.load() - restaura el locale preferido del usuario desde SharedPreferences
/// 6. NotificationService.init() - prepara el plugin de notificaciones locales
/// 7. runApp() - inicia el árbol de widgets de Flutter
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await DatabaseService.init();
  await OfflineCacheService.instance.init();
  await SyncQueueService.instance.init();
  ConnectivityMonitor.instance.start();
  await LocaleService.instance.load();
  try {
    final locale = LocaleService.instance.currentLocale;
    final l10n = AppLocalizations(locale ?? const Locale('en'));
    await l10n.load();
    await NotificationService.instance.init(l10n: l10n);
  } catch (e) {
    debugPrint('NotificationService init error: $e');
  }
  runApp(const ClakettesApp());
}

/// Widget raíz de la aplicación que configura el tema y los locales.
class ClakettesApp extends StatefulWidget {
  const ClakettesApp({super.key});

  @override
  State<ClakettesApp> createState() => _ClakettesAppState();
}

class _ClakettesAppState extends State<ClakettesApp> {
  Locale? _locale;
  StreamSubscription<Locale>? _localeSub;

  @override
  void initState() {
    super.initState();
    _locale = LocaleService.instance.currentLocale;
    _localeSub = LocaleService.instance.onLocaleChanged.listen((locale) {
      setState(() => _locale = locale);
    });
  }

  @override
  void dispose() {
    _localeSub?.cancel();
    super.dispose();
  }

  /// Color semilla de marca (dorado/ámbar) para el esquema de color dinámico de Material 3
  static const Color _seedColor = Color(0xFFB8956E);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Clakettes',
      locale: _locale,
      theme: _buildLightTheme(),
      darkTheme: _buildDarkTheme(),
      themeMode: ThemeMode.system,
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: LocaleService.supportedLocales,
      home: const AuthWrapper(),
    );
  }

  /// Tema claro usando el ColorScheme de Material 3 a partir del color semilla
  ThemeData _buildLightTheme() {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: _seedColor,
      brightness: Brightness.light,
      surface: const Color(0xFFFDFBF9), // Warm off-white surface
    );
    return _baseTheme(colorScheme);
  }

  /// Tema oscuro usando el ColorScheme de Material 3 a partir del color semilla
  ThemeData _buildDarkTheme() {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: _seedColor,
      brightness: Brightness.dark,
      surface: const Color(0xFF121212), // Standard Material dark surface
    );
    return _baseTheme(colorScheme);
  }

  /// Configuración de tema compartida para los modos claro/oscuro.
  ///
  /// Centraliza el theming de todos los componentes para garantizar consistencia.
  /// Usa transiciones de página estilo Cupertino en todas las plataformas para una
  /// sensación nativa.
  ThemeData _baseTheme(ColorScheme colorScheme) {
    final surfaceContainer = colorScheme.surfaceContainerHighest.withAlpha(60);

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      visualDensity: VisualDensity.comfortable,
      // Cupertino transitions on all platforms (iOS-style slide)
      pageTransitionsTheme: const PageTransitionsTheme(
        builders: {
          TargetPlatform.android: CupertinoPageTransitionsBuilder(),
          TargetPlatform.iOS: CupertinoPageTransitionsBuilder(),
          TargetPlatform.windows: CupertinoPageTransitionsBuilder(),
        },
      ),

      // Card: flat, subtle border, comfortable margins
      cardTheme: CardThemeData(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(color: colorScheme.outlineVariant.withAlpha(40)),
        ),
        clipBehavior: Clip.antiAlias,
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
        color: colorScheme.surface,
      ),

      // AppBar: flat, scrolledUnderElevation for shadow when scrolling
      appBarTheme: AppBarTheme(
        centerTitle: false,
        elevation: 0,
        scrolledUnderElevation: 1,
        backgroundColor: colorScheme.surface,
        foregroundColor: colorScheme.onSurface,
        titleSpacing: 0,
        titleTextStyle: TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.w600,
          letterSpacing: -0.3,
          color: colorScheme.onSurface,
        ),
      ),

      // NavigationBar (mobile): pill indicator, only selected label shown
      navigationBarTheme: NavigationBarThemeData(
        indicatorColor: colorScheme.primaryContainer,
        indicatorShape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        labelBehavior: NavigationDestinationLabelBehavior.onlyShowSelected,
        height: 68,
        labelTextStyle: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: colorScheme.primary);
          }
          return TextStyle(fontSize: 12, fontWeight: FontWeight.w500, color: colorScheme.onSurfaceVariant);
        }),
        iconTheme: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return IconThemeData(size: 24, color: colorScheme.primary);
          }
          return IconThemeData(size: 22, color: colorScheme.onSurfaceVariant);
        }),
      ),

      // NavigationRail (desktop): full labels, wider when extended
      navigationRailTheme: NavigationRailThemeData(
        indicatorColor: colorScheme.primaryContainer,
        indicatorShape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        labelType: NavigationRailLabelType.all,
        minExtendedWidth: 220,
        groupAlignment: 0.0,
        backgroundColor: colorScheme.surface,
      ),

      floatingActionButtonTheme: FloatingActionButtonThemeData(
        elevation: 2,
        highlightElevation: 4,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        backgroundColor: colorScheme.primary,
        foregroundColor: colorScheme.onPrimary,
        extendedPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      ),

      // Input fields: filled, rounded, subtle borders
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surfaceContainer,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(color: colorScheme.outline.withAlpha(30)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(color: colorScheme.primary, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(color: colorScheme.error, width: 1),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(color: colorScheme.error, width: 1.5),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        labelStyle: TextStyle(color: colorScheme.onSurfaceVariant, fontWeight: FontWeight.w500),
        hintStyle: TextStyle(color: colorScheme.onSurfaceVariant.withAlpha(120)),
      ),

      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 16),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          textStyle: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600, letterSpacing: 0.3),
        ),
      ),

      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          elevation: 0,
          shadowColor: Colors.transparent,
        ),
      ),

      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      ),

      // SnackBar: floating for better visibility (WCAG)
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        insetPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      ),

      dialogTheme: DialogThemeData(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        titleTextStyle: TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.w600,
          letterSpacing: -0.3,
          color: colorScheme.onSurface,
        ),
        backgroundColor: colorScheme.surface,
      ),

      bottomSheetTheme: BottomSheetThemeData(
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        backgroundColor: colorScheme.surface,
        elevation: 2,
      ),

      dividerTheme: DividerThemeData(
        color: colorScheme.outlineVariant.withAlpha(60),
        thickness: 0.5,
        space: 1,
      ),

      chipTheme: ChipThemeData(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
      ),

      listTileTheme: ListTileThemeData(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 2),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        titleTextStyle: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: colorScheme.onSurface),
        subtitleTextStyle: TextStyle(fontSize: 13, color: colorScheme.onSurfaceVariant),
      ),

      drawerTheme: DrawerThemeData(
        backgroundColor: colorScheme.surface,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.only(topRight: Radius.circular(24), bottomRight: Radius.circular(24)),
        ),
      ),

      popupMenuTheme: PopupMenuThemeData(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        elevation: 4,
      ),

      scrollbarTheme: ScrollbarThemeData(
        thickness: WidgetStateProperty.all(4),
        radius: const Radius.circular(8),
        thumbColor: WidgetStateProperty.all(colorScheme.outlineVariant),
      ),

      sliderTheme: SliderThemeData(
        activeTrackColor: colorScheme.primary,
        inactiveTrackColor: colorScheme.primaryContainer,
        thumbColor: colorScheme.primary,
        overlayColor: colorScheme.primary.withAlpha(20),
      ),

      progressIndicatorTheme: ProgressIndicatorThemeData(
        color: colorScheme.primary,
        circularTrackColor: colorScheme.surfaceContainerHighest,
        linearTrackColor: colorScheme.surfaceContainerHighest,
      ),

      switchTheme: SwitchThemeData(
        thumbColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) return colorScheme.onPrimary;
          return colorScheme.onSurfaceVariant;
        }),
        trackColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) return colorScheme.primary;
          return colorScheme.surfaceContainerHighest;
        }),
      ),

      checkboxTheme: CheckboxThemeData(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
        fillColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) return colorScheme.primary;
          return null;
        }),
      ),

      radioTheme: RadioThemeData(
        fillColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) return colorScheme.primary;
          return colorScheme.onSurfaceVariant;
        }),
      ),

      tabBarTheme: TabBarThemeData(
        labelColor: colorScheme.primary,
        unselectedLabelColor: colorScheme.onSurfaceVariant,
        indicatorColor: colorScheme.primary,
        indicatorSize: TabBarIndicatorSize.tab,
      ),

      searchBarTheme: SearchBarThemeData(
        backgroundColor: WidgetStateProperty.all(surfaceContainer),
        shape: WidgetStateProperty.all(
          RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        ),
        elevation: WidgetStateProperty.all(0),
      ),

      badgeTheme: BadgeThemeData(
        backgroundColor: colorScheme.error,
        textColor: colorScheme.onError,
      ),

      segmentedButtonTheme: SegmentedButtonThemeData(
        style: SegmentedButton.styleFrom(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        ),
      ),
    );
  }
}

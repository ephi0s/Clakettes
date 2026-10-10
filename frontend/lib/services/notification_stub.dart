// Primitivas vacías para plataformas sin Notification API del navegador.
// Se usan en escritorio y móvil mediante import condicional; el servicio
// decide por plataforma si las invoca.

/// Siempre false: sin navegador no hay permiso que pedir.
Future<bool> requestWebNotificationPermission() async => false;

/// Sin efecto fuera del navegador.
void scheduleWebNotification({
  required int id,
  required DateTime fireTime,
  required String title,
  required String body,
}) {}

/// Sin efecto fuera del navegador.
void cancelWebNotification(int id) {}

/// Sin efecto fuera del navegador.
void clearWebNotifications() {}

import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../services/api_service.dart';
import '../services/file_downloader.dart';
import '../models/event_model.dart';
import '../models/calendar_model.dart';
import '../models/role_model.dart';
import '../widgets/reusable_widgets.dart';
import '../widgets/event_visibility_picker.dart';
import '../widgets/empty_state_widget.dart';
import '../widgets/loading_skeleton.dart';
import '../widgets/error_state_widget.dart';
import '../widgets/confirm_dialog.dart';
import 'event_detail_screen.dart';

/// Pantalla que gestiona los eventos de un festival (crear, eliminar, abrir detalle).
class EventsManagementScreen extends StatefulWidget {
  final int festivalId;
  final String festivalName;
  const EventsManagementScreen({super.key, required this.festivalId, required this.festivalName});

  @override
  State<EventsManagementScreen> createState() => _EventsManagementScreenState();
}

/// Mantiene la lista de eventos cargada del festival; se carga en el primer build.
class _EventsManagementScreenState extends State<EventsManagementScreen> {
  final ApiService api = ApiService();
  List<FestivalEvent> _events = [];
  bool _isLoading = true;
  bool _hasError = false;
  bool _isExporting = false;
  bool _initialized = false;
  late AppLocalizations l10n;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    l10n = AppLocalizations.of(context)!;
    if (!_initialized) {
      _initialized = true;
      _loadData();
    }
  }

  /// Obtiene los eventos del festival de la API y gestiona los errores.
  Future<void> _loadData() async {
    if (!mounted) return;
    setState(() { _isLoading = true; _hasError = false; });
    try {
      final result = await api.getEvents(widget.festivalId, size: 100);
      if (!mounted) return;
      setState(() { _events = result.items; _isLoading = false; });
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() { _isLoading = false; _hasError = true; });
    }
  }

  /// Muestra un diálogo para crear un nuevo evento y recarga la lista al tener éxito.
  Future<void> _createEvent() async {
    final titleCtl = TextEditingController();
    final locCtl = TextEditingController();
    final capCtl = TextEditingController();
    var scope = EventVisibilityScope.public;
    var roleIds = <int>{};

    List<RoleSummary> roles = const [];
    try {
      roles = await api.getFestivalRoles(widget.festivalId);
    } catch (e) {
      debugPrint('EventsManagementScreen roles error: $e');
    }
    if (!mounted) return;

    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          title: Text(l10n.newEvent),
          content: SingleChildScrollView(
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              SemanticTextField(controller: titleCtl, label: l10n.titleRequired, semanticLabel: l10n.eventTitle, helperText: l10n.eventTitle),
              SemanticTextField(controller: locCtl, label: l10n.location, semanticLabel: l10n.location, helperText: l10n.venueOrLink),
              SemanticTextField(controller: capCtl, label: l10n.capacity, semanticLabel: l10n.capacity, helperText: l10n.maxAttendees),
              const Divider(height: 24),
              EventVisibilityPicker(
                scope: scope,
                roleIds: roleIds,
                roles: roles,
                onScopeChanged: (v) => setDialogState(() => scope = v),
                onRolesChanged: (v) => setDialogState(() => roleIds = v),
              ),
            ]),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: Text(l10n.cancel)),
            FilledButton(onPressed: () => Navigator.pop(ctx, true), child: Text(l10n.create)),
          ],
        ),
      ),
    );
    final title = titleCtl.text;
    final location = locCtl.text;
    final capacity = int.tryParse(capCtl.text);
    titleCtl.dispose();
    locCtl.dispose();
    capCtl.dispose();

    if (result == true && title.isNotEmpty) {
      try {
        await api.createEvent(
          widget.festivalId,
          FestivalEvent(
            festivalId: widget.festivalId,
            title: title,
            location: location,
            capacity: capacity,
            isPublic: scope == EventVisibilityScope.public,
            visibilityScope: scope.value,
            visibleRoleIds: roleIds.toList(),
          ),
        );
        _loadData();
      } catch (e) {
        if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating));
      }
    }
  }

  /// Elimina el evento indicado tras un diálogo de confirmación.
  Future<void> _deleteEvent(FestivalEvent e) async {
    if (e.id == null) return;
    final confirm = await showConfirmDialog(context, title: l10n.deleteEvent, message: l10n.deleteEntityMessage(e.title));
    if (confirm == true) {
      await api.deleteEvent(e.id!);
      _loadData();
    }
  }

  /// Descarga el calendario ICS de los eventos del festival y notifica el resultado.
  Future<void> _exportCalendar() async {
    if (_isExporting) return;
    setState(() { _isExporting = true; });
    try {
      final bytes = await api.getBytes('/festivals/${widget.festivalId}/events/export/ics');
      await downloadFile(bytes, 'calendar.ics');
      if (!mounted) return;
      setState(() { _isExporting = false; });
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.exportSuccess), behavior: SnackBarBehavior.floating));
    } catch (e) {
      debugPrint('Error: $e');
      if (!mounted) return;
      setState(() { _isExporting = false; });
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.errorFormatWith('$e')), behavior: SnackBarBehavior.floating));
    }
  }

  @override
  Widget build(BuildContext context) {
    l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text('${l10n.events} — ${widget.festivalName}'),
        actions: [
          IconButton(
            icon: _isExporting
                ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.calendar_month_outlined),
            tooltip: l10n.exportCalendar,
            onPressed: _isExporting ? null : _exportCalendar,
          ),
        ],
      ),
      body: _isLoading
          ? const ListSkeleton()
          : _hasError
              ? ErrorStateWidget(onRetry: _loadData)
              : RefreshIndicator(
                  onRefresh: _loadData,
                  child: _events.isEmpty
                      ? EmptyStateWidget(icon: Icons.event_outlined, title: l10n.noEvents, subtitle: l10n.createEventSubtitle)
                      : ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _events.length,
                          itemBuilder: (ctx, i) {
                            final e = _events[i];
                              return Card(
                              margin: const EdgeInsets.only(bottom: 12),
                              child: ListTile(
                                leading: CircleAvatar(child: Icon(e.eventType == 'gala' ? Icons.star : Icons.movie, color: Colors.white)),
                                title: Text(e.title, style: const TextStyle(fontWeight: FontWeight.w600)),
                                subtitle: Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisSize: MainAxisSize.min, children: [
                                  if (e.location != null) Text(e.location!, style: Theme.of(context).textTheme.bodySmall),
                                  if (e.venue != null) Text('Sede: ${e.venue!}', style: Theme.of(context).textTheme.bodySmall),
                                  if (e.eventType == 'screening') Text('Proyección${e.screeningShortfilmIds.isNotEmpty ? ' · ${e.screeningShortfilmIds.length} cortos' : ''}', style: Theme.of(context).textTheme.bodySmall),
                                  if (e.startDate != null) Text('${e.startDate!.toLocal()}'.substring(0, 16), style: Theme.of(context).textTheme.bodySmall),
Row(children: [
                                     StatusIndicator(isActive: e.isActive, activeLabel: l10n.open, inactiveLabel: l10n.closed),
                                     const SizedBox(width: 8),
                                     Text(l10n.capacityFormat(e.capacity), style: Theme.of(context).textTheme.bodySmall),
                                     if (e.isRestricted) ...[
                                       const SizedBox(width: 8),
                                       Tooltip(
                                         message: l10n.restrictedVisibility,
                                         child: Icon(Icons.lock_outline_rounded, size: 14, color: Theme.of(context).colorScheme.onSurfaceVariant),
                                       ),
                                     ],
                                   ]),
                                ]),
                                trailing: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    if (e.id != null)
                                      IconButton(icon: const Icon(Icons.edit_outlined), tooltip: l10n.edit, onPressed: () {
                                        Navigator.push(context, MaterialPageRoute(builder: (_) => EventDetailScreen(eventId: e.id!, festivalName: widget.festivalName)));
                                      }),
                                    IconButton(icon: const Icon(Icons.delete_outline), tooltip: l10n.delete, onPressed: () => _deleteEvent(e)),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                ),
      floatingActionButton: FloatingActionButton(onPressed: _createEvent, tooltip: l10n.createEvent, child: const Icon(Icons.add)),
    );
  }
}

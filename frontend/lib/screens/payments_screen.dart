import 'package:flutter/material.dart';
import '../models/payment_model.dart';
import '../services/api_service.dart';

class PaymentsScreen extends StatefulWidget {
  final int? registrationId;
  final int? eventId;

  const PaymentsScreen({super.key, this.registrationId, this.eventId});

  @override
  State<PaymentsScreen> createState() => _PaymentsScreenState();
}

class _PaymentsScreenState extends State<PaymentsScreen> {
  final ApiService _api = ApiService();
  List<Payment> _items = [];
  bool _isLoading = true;
  bool _isPaying = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _isLoading = true; _error = null; });
    try {
      final res = await _api.getPayments(size: 50);
      if (mounted) setState(() { _items = res.items; _isLoading = false; });
    } catch (e) {
      if (mounted) setState(() { _isLoading = false; _error = '$e'; });
    }
  }

  Future<void> _checkout() async {
    setState(() => _isPaying = true);
    try {
      var payment = await _api.createPaymentCheckout(
        registrationId: widget.registrationId,
        eventId: widget.eventId,
      );
      payment = await _api.confirmPayment(payment.id!);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Mock ${payment.providerRef}: ${payment.status}')),
        );
      }
      await _load();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Pago mock fallido: $e')));
      }
    } finally {
      if (mounted) setState(() => _isPaying = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Pagos (mock)')),
      body: RefreshIndicator(
        onRefresh: _load,
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  FilledButton.icon(
                    onPressed: _isPaying ? null : _checkout,
                    icon: const Icon(Icons.payments_outlined),
                    label: Text(_isPaying ? 'Procesando…' : 'Pagar con proveedor mock'),
                  ),
                  const SizedBox(height: 8),
                  const Text('Sin pasarela real: simula checkout, confirmación y reembolso.', style: TextStyle(fontSize: 12)),
                  const SizedBox(height: 16),
                  if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
                  for (final p in _items)
                    ListTile(
                      leading: Icon(
                        p.isPaid ? Icons.check_circle : p.isFailed ? Icons.error : Icons.pending,
                      ),
                      title: Text('${p.amount.toStringAsFixed(2)} ${p.currency} · ${p.status}'),
                      subtitle: Text('${p.provider} · ${p.providerRef ?? ''}'),
                      trailing: p.isPaid
                          ? IconButton(
                              icon: const Icon(Icons.undo_rounded),
                              tooltip: 'Reembolsar (mock)',
                              onPressed: () async {
                                await _api.refundPayment(p.id!);
                                await _load();
                              },
                            )
                          : null,
                    ),
                ],
              ),
      ),
    );
  }
}

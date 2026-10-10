class Payment {
  final int? id;
  final int? registrationId;
  final int? eventId;
  final double amount;
  final String currency;
  final String provider;
  final String status;
  final String? providerRef;
  final String? checkoutUrl;

  const Payment({
    this.id,
    this.registrationId,
    this.eventId,
    this.amount = 0,
    this.currency = 'EUR',
    this.provider = 'mock',
    this.status = 'pending',
    this.providerRef,
    this.checkoutUrl,
  });

  factory Payment.fromJson(Map<String, dynamic> json) {
    return Payment(
      id: json['id'],
      registrationId: json['registration_id'],
      eventId: json['event_id'],
      amount: (json['amount'] as num?)?.toDouble() ?? 0,
      currency: json['currency'] ?? 'EUR',
      provider: json['provider'] ?? 'mock',
      status: json['status'] ?? 'pending',
      providerRef: json['provider_ref'],
      checkoutUrl: json['checkout_url'],
    );
  }

  bool get isPaid => status == 'paid';
  bool get isPending => status == 'pending';
  bool get isFailed => status == 'failed';
}

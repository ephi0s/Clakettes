import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/models/event_model.dart';

void main() {
  group('FestivalEvent', () {
    final json = <String, dynamic>{
      'id': 1,
      'festival_id': 1,
      'title': 'Opening Night',
      'description': 'The opening ceremony',
      'event_type': 'ceremony',
      'start_date': '2026-07-01T20:00:00.000Z',
      'end_date': '2026-07-01T23:00:00.000Z',
      'location': 'Main Hall',
      'capacity': 500,
      'is_public': true,
      'is_active': true,
      'external_url': 'http://example.com/event',
      'internal_notes': 'VIP only',
      'color_code': '#FF5733',
    };

    test('fromJson creates correct object', () {
      final event = FestivalEvent.fromJson(json);

      expect(event.id, equals(1));
      expect(event.festivalId, equals(1));
      expect(event.title, equals('Opening Night'));
      expect(event.description, equals('The opening ceremony'));
      expect(event.eventType, equals('ceremony'));
      expect(event.startDate, equals(DateTime.utc(2026, 7, 1, 20)));
      expect(event.endDate, equals(DateTime.utc(2026, 7, 1, 23)));
      expect(event.location, equals('Main Hall'));
      expect(event.capacity, equals(500));
      expect(event.isPublic, isTrue);
      expect(event.isActive, isTrue);
      expect(event.externalUrl, equals('http://example.com/event'));
      expect(event.internalNotes, equals('VIP only'));
      expect(event.colorCode, equals('#FF5733'));
    });

    test('toJson returns correct snake_case map', () {
      final event = FestivalEvent(
        id: 1,
        festivalId: 1,
        title: 'Opening Night',
        description: 'The opening ceremony',
        eventType: 'ceremony',
        startDate: DateTime.utc(2026, 7, 1, 20),
        endDate: DateTime.utc(2026, 7, 1, 23),
        location: 'Main Hall',
        capacity: 500,
        isPublic: true,
        isActive: true,
        externalUrl: 'http://example.com/event',
        internalNotes: 'VIP only',
        colorCode: '#FF5733',
      );

      final map = event.toJson();

      expect(map['festival_id'], equals(1));
      expect(map['title'], equals('Opening Night'));
      expect(map['description'], equals('The opening ceremony'));
      expect(map['event_type'], equals('ceremony'));
      expect(map['start_date'], equals('2026-07-01T20:00:00.000Z'));
      expect(map['end_date'], equals('2026-07-01T23:00:00.000Z'));
      expect(map['location'], equals('Main Hall'));
      expect(map['capacity'], equals(500));
      expect(map['is_public'], isTrue);
      expect(map['is_active'], isTrue);
      expect(map['external_url'], equals('http://example.com/event'));
      expect(map['internal_notes'], equals('VIP only'));
      expect(map['color_code'], equals('#FF5733'));
    });

    test('fromJson handles null values', () {
      final minimal = <String, dynamic>{
        'festival_id': 1,
        'title': 'Minimal Event',
      };

      final event = FestivalEvent.fromJson(minimal);

      expect(event.id, isNull);
      expect(event.festivalId, equals(1));
      expect(event.title, equals('Minimal Event'));
      expect(event.description, isNull);
      expect(event.eventType, isNull);
      expect(event.startDate, isNull);
      expect(event.endDate, isNull);
      expect(event.location, isNull);
      expect(event.capacity, isNull);
      expect(event.isPublic, isTrue);
      expect(event.isActive, isTrue);
      expect(event.externalUrl, isNull);
      expect(event.internalNotes, isNull);
      expect(event.colorCode, isNull);
    });
  });

  group('EventTicketType', () {
    final json = <String, dynamic>{
      'id': 1,
      'event_id': 1,
      'name': 'VIP',
      'price': 50.0,
      'capacity': 100,
      'max_per_user': 2,
      'description': 'VIP access',
      'is_active': true,
      'color_code': '#FFD700',
    };

    test('fromJson creates correct object', () {
      final t = EventTicketType.fromJson(json);

      expect(t.id, equals(1));
      expect(t.eventId, equals(1));
      expect(t.name, equals('VIP'));
      expect(t.price, equals(50.0));
      expect(t.capacity, equals(100));
      expect(t.maxPerUser, equals(2));
      expect(t.description, equals('VIP access'));
      expect(t.isActive, isTrue);
      expect(t.colorCode, equals('#FFD700'));
    });

    test('toJson returns correct snake_case map', () {
      final t = EventTicketType(
        id: 1,
        eventId: 1,
        name: 'VIP',
        price: 50.0,
        capacity: 100,
        maxPerUser: 2,
        description: 'VIP access',
        isActive: true,
        colorCode: '#FFD700',
      );

      final map = t.toJson();

      expect(map['event_id'], equals(1));
      expect(map['name'], equals('VIP'));
      expect(map['price'], equals(50.0));
      expect(map['capacity'], equals(100));
      expect(map['max_per_user'], equals(2));
      expect(map['description'], equals('VIP access'));
      expect(map['is_active'], isTrue);
      expect(map['color_code'], equals('#FFD700'));
    });

    test('fromJson handles null values', () {
      final minimal = <String, dynamic>{
        'event_id': 1,
        'name': 'General',
      };

      final t = EventTicketType.fromJson(minimal);

      expect(t.id, isNull);
      expect(t.eventId, equals(1));
      expect(t.name, equals('General'));
      expect(t.price, isNull);
      expect(t.capacity, isNull);
      expect(t.maxPerUser, isNull);
      expect(t.description, isNull);
      expect(t.isActive, isTrue);
      expect(t.colorCode, isNull);
    });
  });

  group('EventSeat', () {
    final json = <String, dynamic>{
      'id': 1,
      'event_id': 1,
      'ticket_type_id': 1,
      'section': 'A',
      'row_label': '1',
      'number': 15,
      'status': 'available',
      'x': 100.0,
      'y': 200.0,
      'is_accessible': false,
    };

    test('fromJson creates correct object', () {
      final seat = EventSeat.fromJson(json);

      expect(seat.id, equals(1));
      expect(seat.eventId, equals(1));
      expect(seat.ticketTypeId, equals(1));
      expect(seat.section, equals('A'));
      expect(seat.rowLabel, equals('1'));
      expect(seat.number, equals(15));
      expect(seat.status, equals('available'));
      expect(seat.x, equals(100.0));
      expect(seat.y, equals(200.0));
      expect(seat.isAccessible, isFalse);
    });

    test('toJson returns correct snake_case map', () {
      final seat = EventSeat(
        id: 1,
        eventId: 1,
        ticketTypeId: 1,
        section: 'A',
        rowLabel: '1',
        number: 15,
        status: 'available',
        x: 100.0,
        y: 200.0,
        isAccessible: false,
      );

      final map = seat.toJson();

      expect(map['event_id'], equals(1));
      expect(map['ticket_type_id'], equals(1));
      expect(map['section'], equals('A'));
      expect(map['row_label'], equals('1'));
      expect(map['number'], equals(15));
      expect(map['status'], equals('available'));
      expect(map['x'], equals(100.0));
      expect(map['y'], equals(200.0));
      expect(map['is_accessible'], isFalse);
    });

    test('fromJson handles null values', () {
      final minimal = <String, dynamic>{
        'event_id': 1,
        'section': 'B',
      };

      final seat = EventSeat.fromJson(minimal);

      expect(seat.id, isNull);
      expect(seat.eventId, equals(1));
      expect(seat.ticketTypeId, isNull);
      expect(seat.section, equals('B'));
      expect(seat.rowLabel, isNull);
      expect(seat.number, isNull);
      expect(seat.status, equals('available'));
      expect(seat.x, isNull);
      expect(seat.y, isNull);
      expect(seat.isAccessible, isFalse);
    });
  });

  group('EventReservation', () {
    final json = <String, dynamic>{
      'id': 1,
      'event_id': 1,
      'user_id': 1,
      'status': 'confirmed',
      'total_quantity': 2,
      'notes': 'Vegetarian meal',
    };

    test('fromJson creates correct object', () {
      final r = EventReservation.fromJson(json);

      expect(r.id, equals(1));
      expect(r.eventId, equals(1));
      expect(r.userId, equals(1));
      expect(r.status, equals('confirmed'));
      expect(r.totalQuantity, equals(2));
      expect(r.notes, equals('Vegetarian meal'));
    });

    test('toJson returns correct snake_case map', () {
      final r = EventReservation(
        id: 1,
        eventId: 1,
        userId: 1,
        status: 'confirmed',
        totalQuantity: 2,
        notes: 'Vegetarian meal',
      );

      final map = r.toJson();

      expect(map['event_id'], equals(1));
      expect(map['user_id'], equals(1));
      expect(map['status'], equals('confirmed'));
      expect(map['total_quantity'], equals(2));
      expect(map['notes'], equals('Vegetarian meal'));
    });

    test('fromJson handles null values', () {
      final minimal = <String, dynamic>{
        'event_id': 1,
      };

      final r = EventReservation.fromJson(minimal);

      expect(r.id, isNull);
      expect(r.eventId, equals(1));
      expect(r.userId, isNull);
      expect(r.status, equals('pending'));
      expect(r.totalQuantity, equals(1));
      expect(r.notes, isNull);
    });
  });
}

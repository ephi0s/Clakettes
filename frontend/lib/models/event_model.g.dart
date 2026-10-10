// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'event_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class FestivalEventAdapter extends TypeAdapter<FestivalEvent> {
  @override
  final int typeId = 5;

  @override
  FestivalEvent read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return FestivalEvent(
      id: fields[0] as int?,
      festivalId: fields[1] as int,
      title: fields[2] as String,
      description: fields[3] as String?,
      eventType: fields[4] as String?,
      startDate: fields[5] as DateTime?,
      endDate: fields[6] as DateTime?,
      location: fields[7] as String?,
      capacity: fields[8] as int?,
      isPublic: fields[9] as bool,
      isActive: fields[10] as bool,
      externalUrl: fields[11] as String?,
      internalNotes: fields[12] as String?,
      colorCode: fields[13] as String?,
      showSeatMap: fields[14] as bool,
      venue: fields[15] as String?,
      venueLatitude: fields[16] as double?,
      venueLongitude: fields[17] as double?,
      visibilityScope: fields[18] as String,
      visibleRoleIds: (fields[19] as List).cast<int>(),
    );
  }

  @override
  void write(BinaryWriter writer, FestivalEvent obj) {
    writer
      ..writeByte(20)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.festivalId)
      ..writeByte(2)
      ..write(obj.title)
      ..writeByte(3)
      ..write(obj.description)
      ..writeByte(4)
      ..write(obj.eventType)
      ..writeByte(5)
      ..write(obj.startDate)
      ..writeByte(6)
      ..write(obj.endDate)
      ..writeByte(7)
      ..write(obj.location)
      ..writeByte(8)
      ..write(obj.capacity)
      ..writeByte(9)
      ..write(obj.isPublic)
      ..writeByte(10)
      ..write(obj.isActive)
      ..writeByte(11)
      ..write(obj.externalUrl)
      ..writeByte(12)
      ..write(obj.internalNotes)
      ..writeByte(13)
      ..write(obj.colorCode)
      ..writeByte(14)
      ..write(obj.showSeatMap)
      ..writeByte(15)
      ..write(obj.venue)
      ..writeByte(16)
      ..write(obj.venueLatitude)
      ..writeByte(17)
      ..write(obj.venueLongitude)
      ..writeByte(18)
      ..write(obj.visibilityScope)
      ..writeByte(19)
      ..write(obj.visibleRoleIds);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FestivalEventAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class EventTicketTypeAdapter extends TypeAdapter<EventTicketType> {
  @override
  final int typeId = 6;

  @override
  EventTicketType read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return EventTicketType(
      id: fields[0] as int?,
      eventId: fields[1] as int,
      name: fields[2] as String,
      price: fields[3] as double?,
      capacity: fields[4] as int?,
      maxPerUser: fields[5] as int?,
      description: fields[6] as String?,
      isActive: fields[7] as bool,
      colorCode: fields[8] as String?,
    );
  }

  @override
  void write(BinaryWriter writer, EventTicketType obj) {
    writer
      ..writeByte(9)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.eventId)
      ..writeByte(2)
      ..write(obj.name)
      ..writeByte(3)
      ..write(obj.price)
      ..writeByte(4)
      ..write(obj.capacity)
      ..writeByte(5)
      ..write(obj.maxPerUser)
      ..writeByte(6)
      ..write(obj.description)
      ..writeByte(7)
      ..write(obj.isActive)
      ..writeByte(8)
      ..write(obj.colorCode);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is EventTicketTypeAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class EventSeatAdapter extends TypeAdapter<EventSeat> {
  @override
  final int typeId = 7;

  @override
  EventSeat read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return EventSeat(
      id: fields[0] as int?,
      eventId: fields[1] as int,
      ticketTypeId: fields[2] as int?,
      section: fields[3] as String,
      rowLabel: fields[4] as String?,
      number: fields[5] as int?,
      status: fields[6] as String,
      x: fields[7] as double?,
      y: fields[8] as double?,
      isAccessible: fields[9] as bool,
    );
  }

  @override
  void write(BinaryWriter writer, EventSeat obj) {
    writer
      ..writeByte(10)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.eventId)
      ..writeByte(2)
      ..write(obj.ticketTypeId)
      ..writeByte(3)
      ..write(obj.section)
      ..writeByte(4)
      ..write(obj.rowLabel)
      ..writeByte(5)
      ..write(obj.number)
      ..writeByte(6)
      ..write(obj.status)
      ..writeByte(7)
      ..write(obj.x)
      ..writeByte(8)
      ..write(obj.y)
      ..writeByte(9)
      ..write(obj.isAccessible);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is EventSeatAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class EventReservationAdapter extends TypeAdapter<EventReservation> {
  @override
  final int typeId = 8;

  @override
  EventReservation read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return EventReservation(
      id: fields[0] as int?,
      eventId: fields[1] as int,
      userId: fields[2] as int?,
      status: fields[3] as String,
      totalQuantity: fields[4] as int,
      notes: fields[5] as String?,
      createdBy: fields[6] as int?,
      confirmedAt: fields[7] as DateTime?,
      cancelledAt: fields[8] as DateTime?,
      attendees: (fields[9] as List?)?.cast<EventAttendee>(),
    );
  }

  @override
  void write(BinaryWriter writer, EventReservation obj) {
    writer
      ..writeByte(10)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.eventId)
      ..writeByte(2)
      ..write(obj.userId)
      ..writeByte(3)
      ..write(obj.status)
      ..writeByte(4)
      ..write(obj.totalQuantity)
      ..writeByte(5)
      ..write(obj.notes)
      ..writeByte(6)
      ..write(obj.createdBy)
      ..writeByte(7)
      ..write(obj.confirmedAt)
      ..writeByte(8)
      ..write(obj.cancelledAt)
      ..writeByte(9)
      ..write(obj.attendees);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is EventReservationAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

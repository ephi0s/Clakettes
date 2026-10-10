// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'location_tag_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class LocationTagAdapter extends TypeAdapter<LocationTag> {
  @override
  final int typeId = 23;

  @override
  LocationTag read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return LocationTag(
      id: fields[0] as int?,
      locationId: fields[1] as int,
      tag: fields[2] as String,
      proposedBy: fields[3] as int,
      status: fields[4] as String,
      createdAt: fields[5] as DateTime?,
    );
  }

  @override
  void write(BinaryWriter writer, LocationTag obj) {
    writer
      ..writeByte(6)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.locationId)
      ..writeByte(2)
      ..write(obj.tag)
      ..writeByte(3)
      ..write(obj.proposedBy)
      ..writeByte(4)
      ..write(obj.status)
      ..writeByte(5)
      ..write(obj.createdAt);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is LocationTagAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

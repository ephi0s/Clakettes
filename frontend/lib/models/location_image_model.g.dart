// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'location_image_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class LocationImageAdapter extends TypeAdapter<LocationImage> {
  @override
  final int typeId = 24;

  @override
  LocationImage read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return LocationImage(
      id: fields[0] as int?,
      locationId: fields[1] as int,
      url: fields[2] as String,
      source: fields[3] as String,
      addedBy: fields[4] as int,
      createdAt: fields[5] as DateTime?,
    );
  }

  @override
  void write(BinaryWriter writer, LocationImage obj) {
    writer
      ..writeByte(6)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.locationId)
      ..writeByte(2)
      ..write(obj.url)
      ..writeByte(3)
      ..write(obj.source)
      ..writeByte(4)
      ..write(obj.addedBy)
      ..writeByte(5)
      ..write(obj.createdAt);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is LocationImageAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

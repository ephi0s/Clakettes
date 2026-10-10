// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'location_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class LocationAdapter extends TypeAdapter<Location> {
  @override
  final int typeId = 25;

  @override
  Location read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return Location(
      id: fields[0] as int?,
      name: fields[1] as String,
      description: fields[2] as String?,
      address: fields[3] as String?,
      latitude: fields[4] as double,
      longitude: fields[5] as double,
      tags: (fields[6] as List).cast<String>(),
      images: (fields[7] as List).cast<String>(),
      isActive: fields[8] as bool,
      createdAt: fields[9] as DateTime?,
      updatedAt: fields[10] as DateTime?,
      addedBy: fields[12] as int?,
      badge: fields[13] as String?,
      locationTags: (fields[14] as List).cast<LocationTag>(),
      locationImages: (fields[15] as List).cast<LocationImage>(),
      relatedLocationIds: (fields[16] as List).cast<int>(),
      filmLocations: (fields[17] as List).cast<FilmLocation>(),
    );
  }

  @override
  void write(BinaryWriter writer, Location obj) {
    writer
      ..writeByte(17)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.name)
      ..writeByte(2)
      ..write(obj.description)
      ..writeByte(3)
      ..write(obj.address)
      ..writeByte(4)
      ..write(obj.latitude)
      ..writeByte(5)
      ..write(obj.longitude)
      ..writeByte(6)
      ..write(obj.tags)
      ..writeByte(7)
      ..write(obj.images)
      ..writeByte(8)
      ..write(obj.isActive)
      ..writeByte(9)
      ..write(obj.createdAt)
      ..writeByte(10)
      ..write(obj.updatedAt)
      ..writeByte(12)
      ..write(obj.addedBy)
      ..writeByte(13)
      ..write(obj.badge)
      ..writeByte(14)
      ..write(obj.locationTags)
      ..writeByte(15)
      ..write(obj.locationImages)
      ..writeByte(16)
      ..write(obj.relatedLocationIds)
      ..writeByte(17)
      ..write(obj.filmLocations);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is LocationAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

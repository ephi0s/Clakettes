// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'film_location_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class FilmLocationAdapter extends TypeAdapter<FilmLocation> {
  @override
  final int typeId = 27;

  @override
  FilmLocation read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return FilmLocation(
      id: fields[0] as int?,
      shortfilmId: fields[1] as int,
      locationId: fields[2] as int,
      role: fields[3] as String,
      startTime: fields[4] as double?,
      endTime: fields[5] as double?,
      notes: fields[6] as String?,
      createdBy: fields[7] as int,
      createdAt: fields[8] as DateTime?,
    );
  }

  @override
  void write(BinaryWriter writer, FilmLocation obj) {
    writer
      ..writeByte(9)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.shortfilmId)
      ..writeByte(2)
      ..write(obj.locationId)
      ..writeByte(3)
      ..write(obj.role)
      ..writeByte(4)
      ..write(obj.startTime)
      ..writeByte(5)
      ..write(obj.endTime)
      ..writeByte(6)
      ..write(obj.notes)
      ..writeByte(7)
      ..write(obj.createdBy)
      ..writeByte(8)
      ..write(obj.createdAt);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FilmLocationAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'festival_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class FestivalAdapter extends TypeAdapter<Festival> {
  @override
  final int typeId = 9;

  @override
  Festival read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return Festival(
      id: fields[0] as int?,
      name: fields[1] as String,
      description: fields[2] as String?,
      location: fields[3] as String?,
      latitude: fields[4] as double?,
      longitude: fields[5] as double?,
      isActive: fields[6] as bool,
      website: fields[7] as String?,
      logoUrl: fields[8] as String?,
      createdAt: fields[9] as DateTime?,
      updatedAt: fields[10] as DateTime?,
      images: (fields[11] as List).cast<String>(),
      allowAliasDisplay: fields[12] as bool,
      showInCalendar: fields[13] as bool,
    );
  }

  @override
  void write(BinaryWriter writer, Festival obj) {
    writer
      ..writeByte(14)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.name)
      ..writeByte(2)
      ..write(obj.description)
      ..writeByte(3)
      ..write(obj.location)
      ..writeByte(4)
      ..write(obj.latitude)
      ..writeByte(5)
      ..write(obj.longitude)
      ..writeByte(6)
      ..write(obj.isActive)
      ..writeByte(7)
      ..write(obj.website)
      ..writeByte(8)
      ..write(obj.logoUrl)
      ..writeByte(9)
      ..write(obj.createdAt)
      ..writeByte(10)
      ..write(obj.updatedAt)
      ..writeByte(11)
      ..write(obj.images)
      ..writeByte(12)
      ..write(obj.allowAliasDisplay)
      ..writeByte(13)
      ..write(obj.showInCalendar);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FestivalAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'award_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class AwardAdapter extends TypeAdapter<Award> {
  @override
  final int typeId = 0;

  @override
  Award read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return Award(
      id: fields[0] as int?,
      festivalId: fields[1] as int,
      awardName: fields[2] as String,
      awardCategory: fields[3] as String?,
      eventId: fields[4] as int?,
      shortfilmId: fields[5] as int?,
      userId: fields[6] as int?,
      position: fields[7] as int?,
      isWinner: fields[8] as bool,
      prizeAmount: fields[9] as String?,
      description: fields[10] as String?,
      isPublic: fields[11] as bool,
      isVerified: fields[12] as bool,
      year: fields[13] as int?,
    );
  }

  @override
  void write(BinaryWriter writer, Award obj) {
    writer
      ..writeByte(14)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.festivalId)
      ..writeByte(2)
      ..write(obj.awardName)
      ..writeByte(3)
      ..write(obj.awardCategory)
      ..writeByte(4)
      ..write(obj.eventId)
      ..writeByte(5)
      ..write(obj.shortfilmId)
      ..writeByte(6)
      ..write(obj.userId)
      ..writeByte(7)
      ..write(obj.position)
      ..writeByte(8)
      ..write(obj.isWinner)
      ..writeByte(9)
      ..write(obj.prizeAmount)
      ..writeByte(10)
      ..write(obj.description)
      ..writeByte(11)
      ..write(obj.isPublic)
      ..writeByte(12)
      ..write(obj.isVerified)
      ..writeByte(13)
      ..write(obj.year);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is AwardAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

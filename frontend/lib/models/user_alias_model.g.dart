// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_alias_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class UserAliasAdapter extends TypeAdapter<UserAlias> {
  @override
  final int typeId = 21;

  @override
  UserAlias read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return UserAlias(
      id: fields[0] as int?,
      userId: fields[1] as int,
      alias: fields[2] as String,
      context: fields[3] as String,
      contextId: fields[4] as int?,
      isPrimary: fields[5] as bool,
      isPublic: fields[6] as bool,
      showAwards: fields[7] as bool,
      profileToken: fields[8] as String?,
      visibilityScope: fields[9] as String,
      notes: fields[10] as String?,
    );
  }

  @override
  void write(BinaryWriter writer, UserAlias obj) {
    writer
      ..writeByte(11)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.userId)
      ..writeByte(2)
      ..write(obj.alias)
      ..writeByte(3)
      ..write(obj.context)
      ..writeByte(4)
      ..write(obj.contextId)
      ..writeByte(5)
      ..write(obj.isPrimary)
      ..writeByte(6)
      ..write(obj.isPublic)
      ..writeByte(7)
      ..write(obj.showAwards)
      ..writeByte(8)
      ..write(obj.profileToken)
      ..writeByte(9)
      ..write(obj.visibilityScope)
      ..writeByte(10)
      ..write(obj.notes);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is UserAliasAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'role_transition_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class RoleTransitionAdapter extends TypeAdapter<RoleTransition> {
  @override
  final int typeId = 18;

  @override
  RoleTransition read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return RoleTransition(
      id: fields[0] as int?,
      userId: fields[1] as int,
      fromRoleId: fields[2] as int?,
      toRoleId: fields[3] as int,
      fromFestivalId: fields[4] as int?,
      toFestivalId: fields[5] as int?,
      transitionType: fields[6] as String,
      changedBy: fields[7] as int,
      reason: fields[8] as String?,
      fromRoleName: fields[9] as String?,
      toRoleName: fields[10] as String?,
    );
  }

  @override
  void write(BinaryWriter writer, RoleTransition obj) {
    writer
      ..writeByte(11)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.userId)
      ..writeByte(2)
      ..write(obj.fromRoleId)
      ..writeByte(3)
      ..write(obj.toRoleId)
      ..writeByte(4)
      ..write(obj.fromFestivalId)
      ..writeByte(5)
      ..write(obj.toFestivalId)
      ..writeByte(6)
      ..write(obj.transitionType)
      ..writeByte(7)
      ..write(obj.changedBy)
      ..writeByte(8)
      ..write(obj.reason)
      ..writeByte(9)
      ..write(obj.fromRoleName)
      ..writeByte(10)
      ..write(obj.toRoleName);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is RoleTransitionAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

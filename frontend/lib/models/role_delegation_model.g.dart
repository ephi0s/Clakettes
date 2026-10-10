// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'role_delegation_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class RoleDelegationAdapter extends TypeAdapter<RoleDelegation> {
  @override
  final int typeId = 15;

  @override
  RoleDelegation read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return RoleDelegation(
      id: fields[0] as int?,
      delegatorId: fields[1] as int,
      delegateId: fields[2] as int,
      roleId: fields[3] as int,
      festivalId: fields[4] as int?,
      status: fields[5] as String,
      reason: fields[6] as String?,
      scopeLimitations: fields[7] as String?,
      revokedBy: fields[8] as int?,
      revokedReason: fields[9] as String?,
      delegatorName: fields[10] as String?,
      delegateName: fields[11] as String?,
      roleName: fields[12] as String?,
    );
  }

  @override
  void write(BinaryWriter writer, RoleDelegation obj) {
    writer
      ..writeByte(13)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.delegatorId)
      ..writeByte(2)
      ..write(obj.delegateId)
      ..writeByte(3)
      ..write(obj.roleId)
      ..writeByte(4)
      ..write(obj.festivalId)
      ..writeByte(5)
      ..write(obj.status)
      ..writeByte(6)
      ..write(obj.reason)
      ..writeByte(7)
      ..write(obj.scopeLimitations)
      ..writeByte(8)
      ..write(obj.revokedBy)
      ..writeByte(9)
      ..write(obj.revokedReason)
      ..writeByte(10)
      ..write(obj.delegatorName)
      ..writeByte(11)
      ..write(obj.delegateName)
      ..writeByte(12)
      ..write(obj.roleName);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is RoleDelegationAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

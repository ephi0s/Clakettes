// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'role_group_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class RoleGroupAdapter extends TypeAdapter<RoleGroup> {
  @override
  final int typeId = 16;

  @override
  RoleGroup read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return RoleGroup(
      id: fields[0] as int?,
      name: fields[1] as String,
      displayName: fields[2] as String,
      description: fields[3] as String?,
      sortOrder: fields[4] as int,
      isActive: fields[5] as bool,
    );
  }

  @override
  void write(BinaryWriter writer, RoleGroup obj) {
    writer
      ..writeByte(6)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.name)
      ..writeByte(2)
      ..write(obj.displayName)
      ..writeByte(3)
      ..write(obj.description)
      ..writeByte(4)
      ..write(obj.sortOrder)
      ..writeByte(5)
      ..write(obj.isActive);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is RoleGroupAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class RoleGroupMembershipAdapter extends TypeAdapter<RoleGroupMembership> {
  @override
  final int typeId = 17;

  @override
  RoleGroupMembership read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return RoleGroupMembership(
      id: fields[0] as int?,
      groupId: fields[1] as int,
      roleId: fields[2] as int,
      level: fields[3] as int,
      isLeader: fields[4] as bool,
      isActive: fields[5] as bool,
      roleName: fields[6] as String?,
    );
  }

  @override
  void write(BinaryWriter writer, RoleGroupMembership obj) {
    writer
      ..writeByte(7)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.groupId)
      ..writeByte(2)
      ..write(obj.roleId)
      ..writeByte(3)
      ..write(obj.level)
      ..writeByte(4)
      ..write(obj.isLeader)
      ..writeByte(5)
      ..write(obj.isActive)
      ..writeByte(6)
      ..write(obj.roleName);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is RoleGroupMembershipAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

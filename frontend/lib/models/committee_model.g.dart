// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'committee_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class CommitteeAdapter extends TypeAdapter<Committee> {
  @override
  final int typeId = 3;

  @override
  Committee read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return Committee(
      id: fields[0] as int?,
      festivalId: fields[1] as int,
      name: fields[2] as String,
      description: fields[3] as String?,
      roleId: fields[4] as int?,
      isActive: fields[5] as bool,
      maxMembers: fields[6] as int?,
      externalVisible: fields[7] as bool,
      memberCount: fields[8] as int,
    );
  }

  @override
  void write(BinaryWriter writer, Committee obj) {
    writer
      ..writeByte(9)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.festivalId)
      ..writeByte(2)
      ..write(obj.name)
      ..writeByte(3)
      ..write(obj.description)
      ..writeByte(4)
      ..write(obj.roleId)
      ..writeByte(5)
      ..write(obj.isActive)
      ..writeByte(6)
      ..write(obj.maxMembers)
      ..writeByte(7)
      ..write(obj.externalVisible)
      ..writeByte(8)
      ..write(obj.memberCount);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is CommitteeAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class CommitteeMemberAdapter extends TypeAdapter<CommitteeMember> {
  @override
  final int typeId = 4;

  @override
  CommitteeMember read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return CommitteeMember(
      id: fields[0] as int?,
      committeeId: fields[1] as int,
      userId: fields[2] as int,
      roleInCommittee: fields[3] as String,
      assignedBy: fields[4] as int?,
      isActive: fields[5] as bool,
      notes: fields[6] as String?,
      userName: fields[7] as String?,
      userAvatar: fields[8] as String?,
    );
  }

  @override
  void write(BinaryWriter writer, CommitteeMember obj) {
    writer
      ..writeByte(9)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.committeeId)
      ..writeByte(2)
      ..write(obj.userId)
      ..writeByte(3)
      ..write(obj.roleInCommittee)
      ..writeByte(4)
      ..write(obj.assignedBy)
      ..writeByte(5)
      ..write(obj.isActive)
      ..writeByte(6)
      ..write(obj.notes)
      ..writeByte(7)
      ..write(obj.userName)
      ..writeByte(8)
      ..write(obj.userAvatar);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is CommitteeMemberAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

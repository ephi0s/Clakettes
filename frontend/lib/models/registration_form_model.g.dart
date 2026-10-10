// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'registration_form_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class RegistrationFormAdapter extends TypeAdapter<RegistrationForm> {
  @override
  final int typeId = 12;

  @override
  RegistrationForm read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return RegistrationForm(
      id: fields[0] as int?,
      festivalId: fields[1] as int,
      title: fields[2] as String,
      description: fields[3] as String?,
      isActive: fields[4] as bool,
      requireExistingAccount: fields[5] as bool,
      startsAt: fields[6] as DateTime?,
      endsAt: fields[7] as DateTime?,
      maxRegistrations: fields[8] as int?,
      allowRoleSelection: fields[9] as bool,
      allowTagSelection: fields[10] as bool,
      sections: (fields[11] as List).cast<RegistrationFormSection>(),
      createdAt: fields[12] as DateTime?,
      feeAmount: fields[13] as double?,
      currency: fields[14] as String,
    );
  }

  @override
  void write(BinaryWriter writer, RegistrationForm obj) {
    writer
      ..writeByte(15)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.festivalId)
      ..writeByte(2)
      ..write(obj.title)
      ..writeByte(3)
      ..write(obj.description)
      ..writeByte(4)
      ..write(obj.isActive)
      ..writeByte(5)
      ..write(obj.requireExistingAccount)
      ..writeByte(6)
      ..write(obj.startsAt)
      ..writeByte(7)
      ..write(obj.endsAt)
      ..writeByte(8)
      ..write(obj.maxRegistrations)
      ..writeByte(9)
      ..write(obj.allowRoleSelection)
      ..writeByte(10)
      ..write(obj.allowTagSelection)
      ..writeByte(11)
      ..write(obj.sections)
      ..writeByte(12)
      ..write(obj.createdAt)
      ..writeByte(13)
      ..write(obj.feeAmount)
      ..writeByte(14)
      ..write(obj.currency);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is RegistrationFormAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class RegistrationFormSectionAdapter
    extends TypeAdapter<RegistrationFormSection> {
  @override
  final int typeId = 13;

  @override
  RegistrationFormSection read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return RegistrationFormSection(
      id: fields[0] as int?,
      formId: fields[1] as int,
      title: fields[2] as String,
      description: fields[3] as String?,
      sortOrder: fields[4] as int,
      allowMultipleRoles: fields[5] as bool,
      maxSelections: fields[6] as int?,
      isRequired: fields[7] as bool,
      roleIds: (fields[8] as List).cast<int>(),
      tagIds: (fields[9] as List).cast<int>(),
    );
  }

  @override
  void write(BinaryWriter writer, RegistrationFormSection obj) {
    writer
      ..writeByte(10)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.formId)
      ..writeByte(2)
      ..write(obj.title)
      ..writeByte(3)
      ..write(obj.description)
      ..writeByte(4)
      ..write(obj.sortOrder)
      ..writeByte(5)
      ..write(obj.allowMultipleRoles)
      ..writeByte(6)
      ..write(obj.maxSelections)
      ..writeByte(7)
      ..write(obj.isRequired)
      ..writeByte(8)
      ..write(obj.roleIds)
      ..writeByte(9)
      ..write(obj.tagIds);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is RegistrationFormSectionAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class FestivalRegistrationAdapter extends TypeAdapter<FestivalRegistration> {
  @override
  final int typeId = 14;

  @override
  FestivalRegistration read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return FestivalRegistration(
      id: fields[0] as int?,
      formId: fields[1] as int,
      userId: fields[2] as int,
      festivalId: fields[3] as int?,
      status: fields[4] as String,
      assignedBy: fields[5] as int?,
      approvedBy: fields[6] as int?,
      notes: fields[7] as String?,
      userName: fields[8] as String?,
      userEmail: fields[9] as String?,
      paymentStatus: fields[10] as String?,
      paidAt: fields[11] as DateTime?,
      paymentMethod: fields[12] as String?,
      transactionId: fields[13] as String?,
    );
  }

  @override
  void write(BinaryWriter writer, FestivalRegistration obj) {
    writer
      ..writeByte(14)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.formId)
      ..writeByte(2)
      ..write(obj.userId)
      ..writeByte(3)
      ..write(obj.festivalId)
      ..writeByte(4)
      ..write(obj.status)
      ..writeByte(5)
      ..write(obj.assignedBy)
      ..writeByte(6)
      ..write(obj.approvedBy)
      ..writeByte(7)
      ..write(obj.notes)
      ..writeByte(8)
      ..write(obj.userName)
      ..writeByte(9)
      ..write(obj.userEmail)
      ..writeByte(10)
      ..write(obj.paymentStatus)
      ..writeByte(11)
      ..write(obj.paidAt)
      ..writeByte(12)
      ..write(obj.paymentMethod)
      ..writeByte(13)
      ..write(obj.transactionId);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FestivalRegistrationAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class RegistrationFormLinkAdapter extends TypeAdapter<RegistrationFormLink> {
  @override
  final int typeId = 26;

  @override
  RegistrationFormLink read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return RegistrationFormLink(
      id: fields[0] as int?,
      formId: fields[1] as int,
      token: fields[2] as String,
      isUnique: fields[3] as bool,
      isPublic: fields[4] as bool,
      isActive: fields[5] as bool,
      expiresAt: fields[6] as DateTime?,
      maxUses: fields[7] as int?,
      useCount: fields[8] as int,
      assignedUserId: fields[9] as int?,
      notes: fields[10] as String?,
      createdAt: fields[11] as DateTime?,
    );
  }

  @override
  void write(BinaryWriter writer, RegistrationFormLink obj) {
    writer
      ..writeByte(12)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.formId)
      ..writeByte(2)
      ..write(obj.token)
      ..writeByte(3)
      ..write(obj.isUnique)
      ..writeByte(4)
      ..write(obj.isPublic)
      ..writeByte(5)
      ..write(obj.isActive)
      ..writeByte(6)
      ..write(obj.expiresAt)
      ..writeByte(7)
      ..write(obj.maxUses)
      ..writeByte(8)
      ..write(obj.useCount)
      ..writeByte(9)
      ..write(obj.assignedUserId)
      ..writeByte(10)
      ..write(obj.notes)
      ..writeByte(11)
      ..write(obj.createdAt);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is RegistrationFormLinkAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

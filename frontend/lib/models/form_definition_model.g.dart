// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'form_definition_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class FormFieldOptionAdapter extends TypeAdapter<FormFieldOption> {
  @override
  final int typeId = 31;

  @override
  FormFieldOption read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return FormFieldOption(
      id: fields[0] as int?,
      value: fields[1] as String,
      label: fields[2] as String,
      sortOrder: fields[3] as int,
      createdAt: fields[4] as DateTime?,
      updatedAt: fields[5] as DateTime?,
    );
  }

  @override
  void write(BinaryWriter writer, FormFieldOption obj) {
    writer
      ..writeByte(6)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.value)
      ..writeByte(2)
      ..write(obj.label)
      ..writeByte(3)
      ..write(obj.sortOrder)
      ..writeByte(4)
      ..write(obj.createdAt)
      ..writeByte(5)
      ..write(obj.updatedAt);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FormFieldOptionAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class FormFieldAdapter extends TypeAdapter<FormField> {
  @override
  final int typeId = 32;

  @override
  FormField read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return FormField(
      id: fields[0] as int?,
      pageId: fields[1] as int,
      fieldType: fields[2] as String,
      label: fields[3] as String,
      helpText: fields[4] as String?,
      placeholder: fields[5] as String?,
      isRequired: fields[6] as bool,
      isVisible: fields[7] as bool,
      isReadOnly: fields[8] as bool,
      sortOrder: fields[9] as int,
      defaultValue: fields[10] as String?,
      minLength: fields[11] as int?,
      maxLength: fields[12] as int?,
      minValue: fields[13] as num?,
      maxValue: fields[14] as num?,
      regexPattern: fields[15] as String?,
      errorMessage: fields[16] as String?,
      allowedValues: (fields[17] as List?)?.cast<String>(),
      dependsOnFieldId: fields[18] as int?,
      dependsOnValue: fields[19] as String?,
      roleFilter: (fields[20] as List?)?.cast<int>(),
      settings: (fields[21] as Map?)?.cast<String, dynamic>(),
      widthClass: fields[22] as String?,
      options: (fields[23] as List).cast<FormFieldOption>(),
      createdAt: fields[24] as DateTime?,
      updatedAt: fields[25] as DateTime?,
    );
  }

  @override
  void write(BinaryWriter writer, FormField obj) {
    writer
      ..writeByte(26)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.pageId)
      ..writeByte(2)
      ..write(obj.fieldType)
      ..writeByte(3)
      ..write(obj.label)
      ..writeByte(4)
      ..write(obj.helpText)
      ..writeByte(5)
      ..write(obj.placeholder)
      ..writeByte(6)
      ..write(obj.isRequired)
      ..writeByte(7)
      ..write(obj.isVisible)
      ..writeByte(8)
      ..write(obj.isReadOnly)
      ..writeByte(9)
      ..write(obj.sortOrder)
      ..writeByte(10)
      ..write(obj.defaultValue)
      ..writeByte(11)
      ..write(obj.minLength)
      ..writeByte(12)
      ..write(obj.maxLength)
      ..writeByte(13)
      ..write(obj.minValue)
      ..writeByte(14)
      ..write(obj.maxValue)
      ..writeByte(15)
      ..write(obj.regexPattern)
      ..writeByte(16)
      ..write(obj.errorMessage)
      ..writeByte(17)
      ..write(obj.allowedValues)
      ..writeByte(18)
      ..write(obj.dependsOnFieldId)
      ..writeByte(19)
      ..write(obj.dependsOnValue)
      ..writeByte(20)
      ..write(obj.roleFilter)
      ..writeByte(21)
      ..write(obj.settings)
      ..writeByte(22)
      ..write(obj.widthClass)
      ..writeByte(23)
      ..write(obj.options)
      ..writeByte(24)
      ..write(obj.createdAt)
      ..writeByte(25)
      ..write(obj.updatedAt);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FormFieldAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class FormPageAdapter extends TypeAdapter<FormPage> {
  @override
  final int typeId = 33;

  @override
  FormPage read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return FormPage(
      id: fields[0] as int?,
      formId: fields[1] as int,
      title: fields[2] as String,
      description: fields[3] as String?,
      sortOrder: fields[4] as int,
      isRepeatable: fields[5] as bool,
      fields: (fields[6] as List).cast<FormField>(),
      createdAt: fields[7] as DateTime?,
      updatedAt: fields[8] as DateTime?,
    );
  }

  @override
  void write(BinaryWriter writer, FormPage obj) {
    writer
      ..writeByte(9)
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
      ..write(obj.isRepeatable)
      ..writeByte(6)
      ..write(obj.fields)
      ..writeByte(7)
      ..write(obj.createdAt)
      ..writeByte(8)
      ..write(obj.updatedAt);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FormPageAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class FormDefinitionAdapter extends TypeAdapter<FormDefinition> {
  @override
  final int typeId = 34;

  @override
  FormDefinition read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return FormDefinition(
      id: fields[0] as int?,
      title: fields[1] as String,
      description: fields[2] as String?,
      formType: fields[3] as String,
      festivalId: fields[4] as int?,
      isActive: fields[5] as bool,
      isPublic: fields[6] as bool,
      startsAt: fields[7] as DateTime?,
      endsAt: fields[8] as DateTime?,
      maxSubmissions: fields[9] as int?,
      requireAuth: fields[10] as bool,
      requiresApproval: fields[11] as bool,
      successMessage: fields[12] as String?,
      submitButtonText: fields[13] as String?,
      createdBy: fields[14] as int?,
      settings: (fields[15] as Map?)?.cast<String, dynamic>(),
      sortOrder: fields[16] as int,
      pages: (fields[17] as List).cast<FormPage>(),
      createdAt: fields[18] as DateTime?,
      updatedAt: fields[19] as DateTime?,
    );
  }

  @override
  void write(BinaryWriter writer, FormDefinition obj) {
    writer
      ..writeByte(20)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.title)
      ..writeByte(2)
      ..write(obj.description)
      ..writeByte(3)
      ..write(obj.formType)
      ..writeByte(4)
      ..write(obj.festivalId)
      ..writeByte(5)
      ..write(obj.isActive)
      ..writeByte(6)
      ..write(obj.isPublic)
      ..writeByte(7)
      ..write(obj.startsAt)
      ..writeByte(8)
      ..write(obj.endsAt)
      ..writeByte(9)
      ..write(obj.maxSubmissions)
      ..writeByte(10)
      ..write(obj.requireAuth)
      ..writeByte(11)
      ..write(obj.requiresApproval)
      ..writeByte(12)
      ..write(obj.successMessage)
      ..writeByte(13)
      ..write(obj.submitButtonText)
      ..writeByte(14)
      ..write(obj.createdBy)
      ..writeByte(15)
      ..write(obj.settings)
      ..writeByte(16)
      ..write(obj.sortOrder)
      ..writeByte(17)
      ..write(obj.pages)
      ..writeByte(18)
      ..write(obj.createdAt)
      ..writeByte(19)
      ..write(obj.updatedAt);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FormDefinitionAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class FormLinkAdapter extends TypeAdapter<FormLink> {
  @override
  final int typeId = 35;

  @override
  FormLink read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return FormLink(
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
      updatedAt: fields[12] as DateTime?,
    );
  }

  @override
  void write(BinaryWriter writer, FormLink obj) {
    writer
      ..writeByte(13)
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
      ..write(obj.createdAt)
      ..writeByte(12)
      ..write(obj.updatedAt);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FormLinkAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class FormFieldResponseAdapter extends TypeAdapter<FormFieldResponse> {
  @override
  final int typeId = 36;

  @override
  FormFieldResponse read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return FormFieldResponse(
      id: fields[0] as int?,
      responseId: fields[1] as int,
      fieldId: fields[2] as int,
      value: fields[3] as dynamic,
      fileUrl: fields[4] as String?,
      createdAt: fields[5] as DateTime?,
      updatedAt: fields[6] as DateTime?,
    );
  }

  @override
  void write(BinaryWriter writer, FormFieldResponse obj) {
    writer
      ..writeByte(7)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.responseId)
      ..writeByte(2)
      ..write(obj.fieldId)
      ..writeByte(3)
      ..write(obj.value)
      ..writeByte(4)
      ..write(obj.fileUrl)
      ..writeByte(5)
      ..write(obj.createdAt)
      ..writeByte(6)
      ..write(obj.updatedAt);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FormFieldResponseAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class FormResponseAdapter extends TypeAdapter<FormResponse> {
  @override
  final int typeId = 37;

  @override
  FormResponse read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return FormResponse(
      id: fields[0] as int?,
      formId: fields[1] as int,
      userId: fields[2] as int?,
      festivalId: fields[3] as int?,
      status: fields[4] as String,
      submittedAt: fields[5] as DateTime?,
      reviewerId: fields[6] as int?,
      reviewedAt: fields[7] as DateTime?,
      reviewNotes: fields[8] as String?,
      linkToken: fields[9] as String?,
      fieldResponses: (fields[10] as List).cast<FormFieldResponse>(),
      createdAt: fields[11] as DateTime?,
      updatedAt: fields[12] as DateTime?,
    );
  }

  @override
  void write(BinaryWriter writer, FormResponse obj) {
    writer
      ..writeByte(13)
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
      ..write(obj.submittedAt)
      ..writeByte(6)
      ..write(obj.reviewerId)
      ..writeByte(7)
      ..write(obj.reviewedAt)
      ..writeByte(8)
      ..write(obj.reviewNotes)
      ..writeByte(9)
      ..write(obj.linkToken)
      ..writeByte(10)
      ..write(obj.fieldResponses)
      ..writeByte(11)
      ..write(obj.createdAt)
      ..writeByte(12)
      ..write(obj.updatedAt);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FormResponseAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class FormAccessRuleAdapter extends TypeAdapter<FormAccessRule> {
  @override
  final int typeId = 38;

  @override
  FormAccessRule read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return FormAccessRule(
      id: fields[0] as int?,
      formId: fields[1] as int,
      roleId: fields[2] as int,
      accessLevel: fields[3] as String,
      isDeny: fields[4] as bool,
      createdAt: fields[5] as DateTime?,
      updatedAt: fields[6] as DateTime?,
    );
  }

  @override
  void write(BinaryWriter writer, FormAccessRule obj) {
    writer
      ..writeByte(7)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.formId)
      ..writeByte(2)
      ..write(obj.roleId)
      ..writeByte(3)
      ..write(obj.accessLevel)
      ..writeByte(4)
      ..write(obj.isDeny)
      ..writeByte(5)
      ..write(obj.createdAt)
      ..writeByte(6)
      ..write(obj.updatedAt);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FormAccessRuleAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

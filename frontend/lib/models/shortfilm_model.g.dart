// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'shortfilm_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class ShortFilmAdapter extends TypeAdapter<ShortFilm> {
  @override
  final int typeId = 20;

  @override
  ShortFilm read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return ShortFilm(
      id: fields[0] as int?,
      title: fields[1] as String,
      description: fields[2] as String?,
      duration: fields[3] as int?,
      videoUrl: fields[4] as String?,
      thumbnailUrl: fields[5] as String?,
      festivalId: fields[6] as int?,
      userId: fields[7] as int,
      isPublic: fields[8] as bool,
      tags: fields[9] as String?,
      createdAt: fields[10] as DateTime?,
      updatedAt: fields[11] as DateTime?,
      filmLocations: (fields[12] as List).cast<FilmLocation>(),
    );
  }

  @override
  void write(BinaryWriter writer, ShortFilm obj) {
    writer
      ..writeByte(13)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.title)
      ..writeByte(2)
      ..write(obj.description)
      ..writeByte(3)
      ..write(obj.duration)
      ..writeByte(4)
      ..write(obj.videoUrl)
      ..writeByte(5)
      ..write(obj.thumbnailUrl)
      ..writeByte(6)
      ..write(obj.festivalId)
      ..writeByte(7)
      ..write(obj.userId)
      ..writeByte(8)
      ..write(obj.isPublic)
      ..writeByte(9)
      ..write(obj.tags)
      ..writeByte(10)
      ..write(obj.createdAt)
      ..writeByte(11)
      ..write(obj.updatedAt)
      ..writeByte(12)
      ..write(obj.filmLocations);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ShortFilmAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

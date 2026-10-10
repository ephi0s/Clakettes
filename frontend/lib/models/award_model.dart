import 'package:hive/hive.dart';

part 'award_model.g.dart';

/// Modelo de datos de un premio o galardón de un festival.
///
/// Mapea entre el JSON snake_case del backend y los campos camelCase de Dart.
@HiveType(typeId: 0)
class Award {
  @HiveField(0)
  final int? id;
  @HiveField(1)
  final int festivalId;
  @HiveField(2)
  final String awardName;
  @HiveField(3)
  final String? awardCategory;
  @HiveField(4)
  final int? eventId;
  @HiveField(5)
  final int? shortfilmId;
  @HiveField(6)
  final int? userId;
  /// Posición en la clasificación del ganador, si corresponde.
  @HiveField(7)
  final int? position;
  /// Indica si el premio fue ganado (true) o solo nominado.
  @HiveField(8)
  final bool isWinner;
  /// Dotación económica del premio como cadena formateada (p. ej. «1.000 €»).
  @HiveField(9)
  final String? prizeAmount;
  @HiveField(10)
  final String? description;
  @HiveField(11)
  final bool isPublic;
  /// Indica si el premio ha sido verificado por el personal del festival.
  @HiveField(12)
  final bool isVerified;
  @HiveField(13)
  final int? year;

  Award({
    this.id,
    required this.festivalId,
    required this.awardName,
    this.awardCategory,
    this.eventId,
    this.shortfilmId,
    this.userId,
    this.position,
    this.isWinner = false,
    this.prizeAmount,
    this.description,
    this.isPublic = true,
    this.isVerified = false,
    this.year,
  });

  /// Crea un [Award] a partir de un mapa JSON (claves snake_case del backend).
  factory Award.fromJson(Map<String, dynamic> json) {
    return Award(
      id: json['id'],
      festivalId: json['festival_id'],
      awardName: json['award_name'],
      awardCategory: json['award_category'],
      eventId: json['event_id'],
      shortfilmId: json['shortfilm_id'],
      userId: json['user_id'],
      position: json['position'],
      isWinner: json['is_winner'] ?? false,
      prizeAmount: json['prize_amount'],
      description: json['description'],
      isPublic: json['is_public'] ?? true,
      isVerified: json['is_verified'] ?? false,
      year: json['year'],
    );
  }

  /// Serializa este [Award] a un mapa JSON (claves snake_case).
  Map<String, dynamic> toJson() => {
    'festival_id': festivalId,
    'award_name': awardName,
    'award_category': awardCategory,
    'event_id': eventId,
    'shortfilm_id': shortfilmId,
    'user_id': userId,
    'position': position,
    'is_winner': isWinner,
    'prize_amount': prizeAmount,
    'description': description,
    'is_public': isPublic,
    'is_verified': isVerified,
    'year': year,
  };
}

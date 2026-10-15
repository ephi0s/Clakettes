class ProfileBadge {
  final int? id;
  final String name;
  final String? description;
  final String? imageUrl;
  final String scope;
  final String? category;
  final int? festivalId;
  final Map<String, dynamic>? conditions;
  final bool requireConditions;
  final bool isActive;
  final int? createdBy;

  ProfileBadge({
    this.id,
    required this.name,
    this.description,
    this.imageUrl,
    this.scope = 'platform',
    this.category,
    this.festivalId,
    this.conditions,
    this.requireConditions = true,
    this.isActive = true,
    this.createdBy,
  });

  bool get isSvg => (imageUrl ?? '').toLowerCase().endsWith('.svg');

  factory ProfileBadge.fromJson(Map<String, dynamic> json) {
    return ProfileBadge(
      id: json['id'],
      name: json['name'] ?? '',
      description: json['description'],
      imageUrl: json['image_url'],
      scope: json['scope'] ?? 'platform',
      category: json['category'],
      festivalId: json['festival_id'],
      conditions: json['conditions'] != null ? Map<String, dynamic>.from(json['conditions']) : null,
      requireConditions: json['require_conditions'] ?? true,
      isActive: json['is_active'] ?? true,
      createdBy: json['created_by'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      if (description != null) 'description': description,
      if (imageUrl != null) 'image_url': imageUrl,
      'scope': scope,
      if (category != null) 'category': category,
      if (festivalId != null) 'festival_id': festivalId,
      if (conditions != null) 'conditions': conditions,
      'require_conditions': requireConditions,
      'is_active': isActive,
    };
  }
}

class BadgeAssignment {
  final int? id;
  final int badgeId;
  final int? targetUserId;
  final int? targetFestivalId;
  final int grantedBy;
  final int? grantFestivalId;
  final String? reason;
  final DateTime? createdAt;
  final ProfileBadge? badge;

  BadgeAssignment({
    this.id,
    required this.badgeId,
    this.targetUserId,
    this.targetFestivalId,
    required this.grantedBy,
    this.grantFestivalId,
    this.reason,
    this.createdAt,
    this.badge,
  });

  factory BadgeAssignment.fromJson(Map<String, dynamic> json) {
    return BadgeAssignment(
      id: json['id'],
      badgeId: json['badge_id'] ?? 0,
      targetUserId: json['target_user_id'],
      targetFestivalId: json['target_festival_id'],
      grantedBy: json['granted_by'] ?? 0,
      grantFestivalId: json['grant_festival_id'],
      reason: json['reason'],
      createdAt: json['created_at'] != null ? DateTime.tryParse(json['created_at'].toString()) : null,
      badge: json['badge'] != null ? ProfileBadge.fromJson(Map<String, dynamic>.from(json['badge'])) : null,
    );
  }
}

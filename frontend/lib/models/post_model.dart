class Post {
  final int? id;
  final int authorId;
  final int? targetUserId;
  final int? festivalId;
  final int? parentPostId;
  final String content;
  final String? embedUrl;
  final String? embedType;
  final bool allowReplies;
  final bool isPinned;
  final bool isHidden;
  final int replyCount;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  Post({
    this.id,
    required this.authorId,
    this.targetUserId,
    this.festivalId,
    this.parentPostId,
    required this.content,
    this.embedUrl,
    this.embedType,
    this.allowReplies = true,
    this.isPinned = false,
    this.isHidden = false,
    this.replyCount = 0,
    this.createdAt,
    this.updatedAt,
  });

  factory Post.fromJson(Map<String, dynamic> json) {
    return Post(
      id: json['id'],
      authorId: json['author_id'] ?? 0,
      targetUserId: json['target_user_id'],
      festivalId: json['festival_id'],
      parentPostId: json['parent_post_id'],
      content: json['content'] ?? '',
      embedUrl: json['embed_url'],
      embedType: json['embed_type'],
      allowReplies: json['allow_replies'] ?? true,
      isPinned: json['is_pinned'] ?? false,
      isHidden: json['is_hidden'] ?? false,
      replyCount: json['reply_count'] ?? 0,
      createdAt: json['created_at'] != null ? DateTime.tryParse(json['created_at'].toString()) : null,
      updatedAt: json['updated_at'] != null ? DateTime.tryParse(json['updated_at'].toString()) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'content': content,
      if (embedUrl != null) 'embed_url': embedUrl,
      if (embedType != null) 'embed_type': embedType,
      'allow_replies': allowReplies,
    };
  }

  Post copyWith({
    int? id,
    int? authorId,
    String? content,
    String? embedUrl,
    String? embedType,
    bool? allowReplies,
    bool? isPinned,
    bool? isHidden,
    int? replyCount,
  }) {
    return Post(
      id: id ?? this.id,
      authorId: authorId ?? this.authorId,
      targetUserId: targetUserId,
      festivalId: festivalId,
      parentPostId: parentPostId,
      content: content ?? this.content,
      embedUrl: embedUrl ?? this.embedUrl,
      embedType: embedType ?? this.embedType,
      allowReplies: allowReplies ?? this.allowReplies,
      isPinned: isPinned ?? this.isPinned,
      isHidden: isHidden ?? this.isHidden,
      replyCount: replyCount ?? this.replyCount,
      createdAt: createdAt,
      updatedAt: updatedAt,
    );
  }
}

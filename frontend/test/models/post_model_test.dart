import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/models/post_model.dart';

void main() {
  test('Post fromJson creates correct object with all fields', () {
    final post = Post.fromJson({
      'id': 1,
      'author_id': 2,
      'target_user_id': 3,
      'festival_id': null,
      'parent_post_id': null,
      'content': 'Hello **world**',
      'embed_url': 'https://www.youtube.com/watch?v=abc123XYZ_-',
      'embed_type': 'youtube',
      'allow_replies': true,
      'is_pinned': false,
      'is_hidden': false,
      'reply_count': 2,
      'created_at': '2026-01-01T00:00:00.000Z',
    });
    expect(post.id, 1);
    expect(post.authorId, 2);
    expect(post.targetUserId, 3);
    expect(post.content, 'Hello **world**');
    expect(post.embedType, 'youtube');
    expect(post.replyCount, 2);
    expect(post.allowReplies, isTrue);
  });

  test('Post toJson returns create payload', () {
    final post = Post(authorId: 2, content: 'Hi', embedUrl: 'https://vimeo.com/123', embedType: 'vimeo');
    final json = post.toJson();
    expect(json['content'], 'Hi');
    expect(json['embed_url'], 'https://vimeo.com/123');
    expect(json['embed_type'], 'vimeo');
    expect(json['allow_replies'], isTrue);
    expect(json.containsKey('id'), isFalse);
  });

  test('Post fromJson handles null optionals', () {
    final post = Post.fromJson({'author_id': 5, 'content': 'x'});
    expect(post.id, isNull);
    expect(post.embedUrl, isNull);
    expect(post.allowReplies, isTrue);
    expect(post.isPinned, isFalse);
    expect(post.replyCount, 0);
  });

  test('Post copyWith preserves scope fields', () {
    final post = Post(id: 1, authorId: 2, targetUserId: 3, content: 'a');
    final updated = post.copyWith(content: 'b', isPinned: true);
    expect(updated.content, 'b');
    expect(updated.isPinned, isTrue);
    expect(updated.targetUserId, 3);
    expect(updated.authorId, 2);
  });
}

part of '../api_service.dart';

extension PostApi on ApiService {
  Future<PaginatedResult<Post>> getUserPosts(int userId, {int page = 1, int size = 20}) async {
    final data = await _get('/users/$userId/posts/', {'page': '$page', 'size': '$size'});
    return _paginated(data, Post.fromJson);
  }

  Future<Post> createUserPost(int userId, Post post) async {
    final data = await create('/users/$userId/posts/', post.toJson());
    return Post.fromJson(data);
  }

  Future<PaginatedResult<Post>> getFestivalPosts(int festivalId, {int page = 1, int size = 20}) async {
    final data = await _get('/festivals/$festivalId/posts/', {'page': '$page', 'size': '$size'});
    return _paginated(data, Post.fromJson);
  }

  Future<Post> createFestivalPost(int festivalId, Post post) async {
    final data = await create('/festivals/$festivalId/posts/', post.toJson());
    return Post.fromJson(data);
  }

  Future<Post> getPost(int postId) async {
    final data = await request('GET', '/posts/$postId');
    return Post.fromJson(data);
  }

  Future<Post> updatePost(int postId, Map<String, dynamic> fields) async {
    final data = await _put('/posts/$postId', fields);
    return Post.fromJson(data);
  }

  Future<void> deletePost(int postId) async {
    await request('DELETE', '/posts/$postId');
  }

  Future<PaginatedResult<Post>> getReplies(int postId, {int page = 1, int size = 20}) async {
    final data = await _get('/posts/$postId/replies/', {'page': '$page', 'size': '$size'});
    return _paginated(data, Post.fromJson);
  }

  Future<Post> createReply(int postId, Post reply) async {
    final data = await create('/posts/$postId/replies/', reply.toJson());
    return Post.fromJson(data);
  }

  Future<Post> moderatePost(int postId, Map<String, dynamic> fields) async {
    final data = await request('POST', '/posts/$postId/moderate', body: json.encode(fields));
    return Post.fromJson(data);
  }
}

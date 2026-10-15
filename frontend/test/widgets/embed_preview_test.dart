import 'package:flutter_test/flutter_test.dart';
import 'package:clakettes/widgets/embed_preview.dart';

void main() {
  test('detectEmbed recognizes YouTube variants', () {
    expect(detectEmbed('https://www.youtube.com/watch?v=dQw4w9WgXcQ')?.platform, 'youtube');
    expect(detectEmbed('https://youtu.be/dQw4w9WgXcQ')?.videoId, 'dQw4w9WgXcQ');
    expect(detectEmbed('https://www.youtube.com/shorts/abc123XYZ_-')?.platform, 'youtube');
    expect(detectEmbed('https://www.youtube.com/watch?v=dQw4w9WgXcQ')?.thumbnailUrl, contains('img.youtube.com'));
  });

  test('detectEmbed recognizes other audio/video platforms', () {
    expect(detectEmbed('https://vimeo.com/123456')?.platform, 'vimeo');
    expect(detectEmbed('https://www.dailymotion.com/video/x7abcde')?.platform, 'dailymotion');
    expect(detectEmbed('https://dai.ly/x7abcde')?.platform, 'dailymotion');
    expect(detectEmbed('https://odysee.com/@canal:1/video:2')?.platform, 'odysee');
    expect(detectEmbed('https://www.ivoox.com/podcast-episodio_sq_f123_1.html')?.platform, 'ivoox');
    expect(detectEmbed('https://open.podimo.com/episode/x')?.platform, 'podimo');
  });

  test('detectEmbed falls back to generic and rejects garbage', () {
    expect(detectEmbed('https://example.com/page')?.platform, 'generic');
    expect(detectEmbed('') , isNull);
    expect(detectEmbed('   '), isNull);
    expect(detectEmbed('not a url at all !!!'), isNull);
  });
}

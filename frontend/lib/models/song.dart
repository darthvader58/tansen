class Song {
  final String songId;
  final String title;
  final String artist;
  final String? album;
  final int duration; // seconds
  final String? genre;
  final String? difficulty;
  final String? originalKey;
  final int? tempo;
  final String? timeSignature;
  final SongMetadata metadata;
  final List<String> availableInstruments;
  final bool isFavorite;
  final bool isDownloaded;

  Song({
    required this.songId,
    required this.title,
    required this.artist,
    this.album,
    required this.duration,
    this.genre,
    this.difficulty,
    this.originalKey,
    this.tempo,
    this.timeSignature,
    required this.metadata,
    required this.availableInstruments,
    this.isFavorite = false,
    this.isDownloaded = false,
  });

  factory Song.fromJson(Map<String, dynamic> json) {
    return Song(
      songId: json['songId'] as String,
      title: json['title'] as String,
      artist: json['artist'] as String,
      album: json['album'] as String?,
      duration: json['duration'] as int,
      genre: json['genre'] as String?,
      difficulty: json['difficulty'] as String?,
      originalKey: json['originalKey'] as String?,
      tempo: json['tempo'] as int?,
      timeSignature: json['timeSignature'] as String?,
      metadata: SongMetadata.fromJson(json['metadata'] as Map<String, dynamic>),
      availableInstruments: (json['availableInstruments'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          [],
      isFavorite: json['isFavorite'] as bool? ?? false,
      isDownloaded: json['isDownloaded'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'songId': songId,
      'title': title,
      'artist': artist,
      'album': album,
      'duration': duration,
      'genre': genre,
      'difficulty': difficulty,
      'originalKey': originalKey,
      'tempo': tempo,
      'timeSignature': timeSignature,
      'metadata': metadata.toJson(),
      'availableInstruments': availableInstruments,
      'isFavorite': isFavorite,
      'isDownloaded': isDownloaded,
    };
  }

  String get formattedDuration {
    final minutes = duration ~/ 60;
    final seconds = duration % 60;
    return '$minutes:${seconds.toString().padLeft(2, '0')}';
  }

  Song copyWith({
    bool? isFavorite,
    bool? isDownloaded,
  }) {
    return Song(
      songId: songId,
      title: title,
      artist: artist,
      album: album,
      duration: duration,
      genre: genre,
      difficulty: difficulty,
      originalKey: originalKey,
      tempo: tempo,
      timeSignature: timeSignature,
      metadata: metadata,
      availableInstruments: availableInstruments,
      isFavorite: isFavorite ?? this.isFavorite,
      isDownloaded: isDownloaded ?? this.isDownloaded,
    );
  }
}

class SongMetadata {
  final String? spotifyId;
  final String? youtubeId;
  final String? musicbrainzId;
  final String? albumArt;
  final String source; // library, user_upload, youtube, spotify

  SongMetadata({
    this.spotifyId,
    this.youtubeId,
    this.musicbrainzId,
    this.albumArt,
    required this.source,
  });

  factory SongMetadata.fromJson(Map<String, dynamic> json) {
    return SongMetadata(
      spotifyId: json['spotifyId'] as String?,
      youtubeId: json['youtubeId'] as String?,
      musicbrainzId: json['musicbrainzId'] as String?,
      albumArt: json['albumArt'] as String?,
      source: json['source'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'spotifyId': spotifyId,
      'youtubeId': youtubeId,
      'musicbrainzId': musicbrainzId,
      'albumArt': albumArt,
      'source': source,
    };
  }
}

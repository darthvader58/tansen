class User {
  final String userId;
  final String email;
  final String displayName;
  final String? photoURL;
  final DateTime createdAt;
  final DateTime lastLoginAt;
  final UserPreferences preferences;
  final UserStats stats;
  final RateLimits rateLimits;

  User({
    required this.userId,
    required this.email,
    required this.displayName,
    this.photoURL,
    required this.createdAt,
    required this.lastLoginAt,
    required this.preferences,
    required this.stats,
    required this.rateLimits,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      userId: json['userId'] as String,
      email: json['email'] as String,
      displayName: json['displayName'] as String,
      photoURL: json['photoURL'] as String?,
      createdAt: DateTime.parse(json['createdAt'] as String),
      lastLoginAt: DateTime.parse(json['lastLoginAt'] as String),
      preferences: UserPreferences.fromJson(json['preferences'] as Map<String, dynamic>),
      stats: UserStats.fromJson(json['stats'] as Map<String, dynamic>),
      rateLimits: RateLimits.fromJson(json['rateLimits'] as Map<String, dynamic>),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'userId': userId,
      'email': email,
      'displayName': displayName,
      'photoURL': photoURL,
      'createdAt': createdAt.toIso8601String(),
      'lastLoginAt': lastLoginAt.toIso8601String(),
      'preferences': preferences.toJson(),
      'stats': stats.toJson(),
      'rateLimits': rateLimits.toJson(),
    };
  }
}

class UserPreferences {
  final String skillLevel; // beginner, intermediate, advanced
  final String primaryInstrument;
  final List<String> secondaryInstruments;
  final String notationFormat; // sargam, western, alphabetical
  final String sargamStyle; // hindustani, carnatic
  final String theme; // light, dark, system

  UserPreferences({
    required this.skillLevel,
    required this.primaryInstrument,
    required this.secondaryInstruments,
    required this.notationFormat,
    required this.sargamStyle,
    required this.theme,
  });

  factory UserPreferences.fromJson(Map<String, dynamic> json) {
    return UserPreferences(
      skillLevel: json['skillLevel'] as String,
      primaryInstrument: json['primaryInstrument'] as String,
      secondaryInstruments: (json['secondaryInstruments'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      notationFormat: json['notationFormat'] as String,
      sargamStyle: json['sargamStyle'] as String,
      theme: json['theme'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'skillLevel': skillLevel,
      'primaryInstrument': primaryInstrument,
      'secondaryInstruments': secondaryInstruments,
      'notationFormat': notationFormat,
      'sargamStyle': sargamStyle,
      'theme': theme,
    };
  }

  UserPreferences copyWith({
    String? skillLevel,
    String? primaryInstrument,
    List<String>? secondaryInstruments,
    String? notationFormat,
    String? sargamStyle,
    String? theme,
  }) {
    return UserPreferences(
      skillLevel: skillLevel ?? this.skillLevel,
      primaryInstrument: primaryInstrument ?? this.primaryInstrument,
      secondaryInstruments: secondaryInstruments ?? this.secondaryInstruments,
      notationFormat: notationFormat ?? this.notationFormat,
      sargamStyle: sargamStyle ?? this.sargamStyle,
      theme: theme ?? this.theme,
    );
  }
}

class UserStats {
  final int totalPracticeTime; // minutes
  final int songsLearned;
  final int currentStreak; // days
  final int longestStreak; // days

  UserStats({
    required this.totalPracticeTime,
    required this.songsLearned,
    required this.currentStreak,
    required this.longestStreak,
  });

  factory UserStats.fromJson(Map<String, dynamic> json) {
    return UserStats(
      totalPracticeTime: json['totalPracticeTime'] as int,
      songsLearned: json['songsLearned'] as int,
      currentStreak: json['currentStreak'] as int,
      longestStreak: json['longestStreak'] as int,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'totalPracticeTime': totalPracticeTime,
      'songsLearned': songsLearned,
      'currentStreak': currentStreak,
      'longestStreak': longestStreak,
    };
  }
}

class RateLimits {
  final int transcriptionsToday;
  final DateTime lastTranscriptionReset;
  final int activeJobs;

  RateLimits({
    required this.transcriptionsToday,
    required this.lastTranscriptionReset,
    required this.activeJobs,
  });

  factory RateLimits.fromJson(Map<String, dynamic> json) {
    return RateLimits(
      transcriptionsToday: json['transcriptionsToday'] as int,
      lastTranscriptionReset: DateTime.parse(json['lastTranscriptionReset'] as String),
      activeJobs: json['activeJobs'] as int,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'transcriptionsToday': transcriptionsToday,
      'lastTranscriptionReset': lastTranscriptionReset.toIso8601String(),
      'activeJobs': activeJobs,
    };
  }

  bool get canTranscribe => transcriptionsToday < 10 && activeJobs < 2;
  int get remainingTranscriptions => 10 - transcriptionsToday;
}

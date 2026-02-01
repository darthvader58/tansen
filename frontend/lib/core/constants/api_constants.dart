class ApiConstants {
  // Base URL - update this for production
  static const String baseUrl = 'http://localhost:8000/api/v1';
  
  // Auth endpoints
  static const String authGoogle = '/auth/google';
  static const String authLogout = '/auth/logout';
  
  // Transcription endpoints
  static const String transcriptionsUpload = '/transcriptions/upload';
  static const String transcriptionsYoutube = '/transcriptions/youtube';
  static String transcriptionStatus(String jobId) => '/transcriptions/$jobId/status';
  static String transcriptionGet(String transcriptionId) => '/transcriptions/$transcriptionId';
  
  // Song endpoints
  static const String songs = '/songs';
  static const String songsSearch = '/songs/search';
  static String songDetail(String songId) => '/songs/$songId';
  static String songInstrumental(String songId) => '/songs/$songId/instrumental';
  static String songInstrumentalStatus(String songId, String jobId) => 
      '/songs/$songId/instrumental/$jobId';
  
  // User endpoints
  static const String userMe = '/users/me';
  static const String userFavorites = '/users/me/favorites';
  static String userFavoriteAdd(String songId) => '/users/me/favorites/$songId';
  static String userFavoriteRemove(String songId) => '/users/me/favorites/$songId';
  static const String userHistory = '/users/me/history';
  
  // Download endpoints
  static const String downloads = '/downloads';
  static String downloadSong(String songId) => '/downloads/$songId';
  
  // Recommendations
  static const String recommendations = '/recommendations';
  
  // Timeouts
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  static const Duration sendTimeout = Duration(minutes: 5); // For file uploads
}

import 'package:flutter/foundation.dart';
import 'package:dio/dio.dart';
import '../core/services/api_service.dart';

class PracticeProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  bool _isLoading = false;
  bool _isRecording = false;
  bool _isAnalyzing = false;
  Map<String, dynamic>? _currentAnalysis;
  List<Map<String, dynamic>> _practiceHistory = [];
  Map<String, dynamic>? _practiceStats;
  String? _error;

  bool get isLoading => _isLoading;
  bool get isRecording => _isRecording;
  bool get isAnalyzing => _isAnalyzing;
  Map<String, dynamic>? get currentAnalysis => _currentAnalysis;
  List<Map<String, dynamic>> get practiceHistory => _practiceHistory;
  Map<String, dynamic>? get practiceStats => _practiceStats;
  String? get error => _error;

  /// Start recording practice session
  void startRecording() {
    _isRecording = true;
    _error = null;
    notifyListeners();
  }

  /// Stop recording practice session
  void stopRecording() {
    _isRecording = false;
    notifyListeners();
  }

  /// Analyze practice performance
  Future<void> analyzePractice({
    required String audioFilePath,
    required String songId,
    String instrument = 'piano',
  }) async {
    try {
      _isAnalyzing = true;
      _error = null;
      notifyListeners();

      // Create multipart form data
      FormData formData = FormData.fromMap({
        'user_audio': await MultipartFile.fromFile(
          audioFilePath,
          filename: 'practice_audio.wav',
        ),
        'song_id': songId,
        'instrument': instrument,
      });

      final response = await _apiService.post(
        '/practice/feedback',
        data: formData,
      );

      if (response.statusCode == 200 && response.data['success']) {
        _currentAnalysis = response.data['analysis'];
        
        // Refresh practice history and stats after new session
        await fetchPracticeHistory();
        await fetchPracticeStats();
      } else {
        _error = response.data['message'] ?? 'Failed to analyze practice';
      }
    } on DioException catch (e) {
      _error = e.response?.data['detail'] ?? 'Network error occurred';
      debugPrint('Error analyzing practice: $e');
    } catch (e) {
      _error = 'An unexpected error occurred';
      debugPrint('Error analyzing practice: $e');
    } finally {
      _isAnalyzing = false;
      notifyListeners();
    }
  }

  /// Fetch practice session history
  Future<void> fetchPracticeHistory({int limit = 20}) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final response = await _apiService.get(
        '/practice/history',
        queryParameters: {'limit': limit},
      );

      if (response.statusCode == 200 && response.data['success']) {
        _practiceHistory = List<Map<String, dynamic>>.from(
          response.data['sessions'] ?? [],
        );
      } else {
        _error = response.data['message'] ?? 'Failed to fetch practice history';
      }
    } on DioException catch (e) {
      _error = e.response?.data['detail'] ?? 'Network error occurred';
      debugPrint('Error fetching practice history: $e');
    } catch (e) {
      _error = 'An unexpected error occurred';
      debugPrint('Error fetching practice history: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Fetch practice statistics
  Future<void> fetchPracticeStats() async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final response = await _apiService.get('/practice/stats');

      if (response.statusCode == 200 && response.data['success']) {
        _practiceStats = response.data['stats'];
      } else {
        _error = response.data['message'] ?? 'Failed to fetch practice stats';
      }
    } on DioException catch (e) {
      _error = e.response?.data['detail'] ?? 'Network error occurred';
      debugPrint('Error fetching practice stats: $e');
    } catch (e) {
      _error = 'An unexpected error occurred';
      debugPrint('Error fetching practice stats: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Clear current analysis
  void clearAnalysis() {
    _currentAnalysis = null;
    notifyListeners();
  }

  /// Clear error
  void clearError() {
    _error = null;
    notifyListeners();
  }

  /// Get practice time for last 7 days (mock data for now)
  List<Map<String, dynamic>> getWeeklyPracticeData() {
    // This would ideally come from the backend
    // For now, return mock data
    return [
      {'day': 'Mon', 'minutes': 45},
      {'day': 'Tue', 'minutes': 60},
      {'day': 'Wed', 'minutes': 30},
      {'day': 'Thu', 'minutes': 75},
      {'day': 'Fri', 'minutes': 50},
      {'day': 'Sat', 'minutes': 90},
      {'day': 'Sun', 'minutes': 65},
    ];
  }

  /// Get instrument breakdown
  Map<String, int> getInstrumentBreakdown() {
    if (_practiceStats == null) {
      return {
        'Piano': 45,
        'Guitar': 32,
        'Vocals': 28,
        'Drums': 15,
      };
    }
    
    final instruments = _practiceStats!['instruments'] as Map<String, dynamic>?;
    if (instruments == null) return {};
    
    return instruments.map((key, value) => MapEntry(key, value as int));
  }

  /// Get total practice hours
  int getTotalPracticeHours() {
    if (_practiceStats == null) return 127;
    return (_practiceStats!['total_minutes'] as int? ?? 0) ~/ 60;
  }

  /// Get songs learned count
  int getSongsLearnedCount() {
    // This would come from backend
    return 23;
  }

  /// Get current streak
  int getCurrentStreak() {
    if (_practiceStats == null) return 15;
    return _practiceStats!['streak_days'] as int? ?? 0;
  }
}

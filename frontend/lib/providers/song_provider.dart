import 'package:flutter/foundation.dart';
import '../core/services/api_service.dart';
import '../core/constants/api_constants.dart';
import '../models/song.dart';

class SongProvider extends ChangeNotifier {
  final ApiService _apiService;

  List<Song> _songs = [];
  List<Song> _searchResults = [];
  bool _isLoading = false;
  String? _error;
  int _currentPage = 1;
  bool _hasMore = true;

  SongProvider({required ApiService apiService}) : _apiService = apiService;

  List<Song> get songs => _songs;
  List<Song> get searchResults => _searchResults;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasMore => _hasMore;

  Future<void> fetchSongs({
    int page = 1,
    int limit = 20,
    String? genre,
    String? difficulty,
    String? instrument,
    String sortBy = 'popularity',
  }) async {
    if (_isLoading) return;

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.get(
        ApiConstants.songs,
        queryParameters: {
          'page': page,
          'limit': limit,
          if (genre != null) 'genre': genre,
          if (difficulty != null) 'difficulty': difficulty,
          if (instrument != null) 'instrument': instrument,
          'sortBy': sortBy,
        },
      );

      final List<dynamic> songsData = response.data['songs'] as List<dynamic>;
      final newSongs = songsData.map((json) => Song.fromJson(json as Map<String, dynamic>)).toList();

      if (page == 1) {
        _songs = newSongs;
      } else {
        _songs.addAll(newSongs);
      }

      _currentPage = page;
      _hasMore = response.data['pagination']['hasNext'] as bool;
      _error = null;
    } on ApiException catch (e) {
      _error = e.getUserFriendlyMessage();
    } catch (e) {
      _error = 'Failed to load songs. Please try again.';
      debugPrint('Error fetching songs: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> searchSongs(String query, {String? source}) async {
    if (query.isEmpty) {
      _searchResults = [];
      notifyListeners();
      return;
    }

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.get(
        ApiConstants.songsSearch,
        queryParameters: {
          'q': query,
          if (source != null) 'source': source,
        },
      );

      final List<dynamic> resultsData = response.data['results'] as List<dynamic>;
      _searchResults = resultsData.map((json) => Song.fromJson(json as Map<String, dynamic>)).toList();
      _error = null;
    } on ApiException catch (e) {
      _error = e.getUserFriendlyMessage();
    } catch (e) {
      _error = 'Search failed. Please try again.';
      debugPrint('Error searching songs: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<Song?> getSongDetail(String songId) async {
    try {
      final response = await _apiService.get(ApiConstants.songDetail(songId));
      return Song.fromJson(response.data as Map<String, dynamic>);
    } on ApiException catch (e) {
      _error = e.getUserFriendlyMessage();
      notifyListeners();
      return null;
    } catch (e) {
      _error = 'Failed to load song details.';
      debugPrint('Error fetching song detail: $e');
      notifyListeners();
      return null;
    }
  }

  Future<void> loadMore() async {
    if (!_hasMore || _isLoading) return;
    await fetchSongs(page: _currentPage + 1);
  }

  void clearSearch() {
    _searchResults = [];
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}

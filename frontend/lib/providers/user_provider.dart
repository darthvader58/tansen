import 'package:flutter/foundation.dart';
import 'package:dio/dio.dart';
import '../core/services/api_service.dart';
import '../models/user.dart';

class UserProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  User? _currentUser;
  bool _isLoading = false;
  String? _error;

  User? get currentUser => _currentUser;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isAuthenticated => _currentUser != null;

  /// Fetch current user profile
  Future<void> fetchUserProfile() async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final response = await _apiService.get('/users/me');

      if (response.statusCode == 200) {
        _currentUser = User.fromJson(response.data);
      } else {
        _error = response.data['message'] ?? 'Failed to fetch user profile';
      }
    } on DioException catch (e) {
      _error = e.response?.data['detail'] ?? 'Network error occurred';
      debugPrint('Error fetching user profile: $e');
    } catch (e) {
      _error = 'An unexpected error occurred';
      debugPrint('Error fetching user profile: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Update user profile
  Future<bool> updateProfile({
    String? displayName,
    String? primaryInstrument,
    String? skillLevel,
    String? bio,
  }) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      // Build preferences object matching backend UserPreferences model
      final preferences = <String, dynamic>{};
      if (primaryInstrument != null) {
        preferences['primary_instrument'] = primaryInstrument;
      }
      if (skillLevel != null) {
        preferences['skill_level'] = skillLevel;
      }

      final data = {
        'preferences': preferences,
      };

      final response = await _apiService.patch('/users/me', data: data);

      if (response.statusCode == 200) {
        _currentUser = User.fromJson(response.data);
        notifyListeners();
        return true;
      } else {
        _error = response.data['message'] ?? 'Failed to update profile';
        return false;
      }
    } on DioException catch (e) {
      _error = e.response?.data['detail'] ?? 'Network error occurred';
      debugPrint('Error updating profile: $e');
      return false;
    } catch (e) {
      _error = 'An unexpected error occurred';
      debugPrint('Error updating profile: $e');
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Update notification preferences
  Future<bool> updateNotificationPreferences(Map<String, dynamic> preferences) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final response = await _apiService.patch(
        '/users/me/preferences',
        data: {'notifications': preferences},
      );

      if (response.statusCode == 200) {
        // Update local user data
        if (_currentUser != null) {
          // TODO: Update user notification preferences
        }
        notifyListeners();
        return true;
      } else {
        _error = response.data['message'] ?? 'Failed to update preferences';
        return false;
      }
    } on DioException catch (e) {
      _error = e.response?.data['detail'] ?? 'Network error occurred';
      debugPrint('Error updating preferences: $e');
      return false;
    } catch (e) {
      _error = 'An unexpected error occurred';
      debugPrint('Error updating preferences: $e');
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Sign out user
  Future<void> signOut() async {
    _currentUser = null;
    notifyListeners();
  }

  /// Clear error
  void clearError() {
    _error = null;
    notifyListeners();
  }
}

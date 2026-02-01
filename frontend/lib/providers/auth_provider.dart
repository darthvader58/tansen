import 'package:flutter/foundation.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../core/services/api_service.dart';
import '../core/constants/api_constants.dart';
import '../models/user.dart';

class AuthProvider extends ChangeNotifier {
  final ApiService _apiService;
  final GoogleSignIn _googleSignIn;
  final FlutterSecureStorage _secureStorage;

  User? _user;
  String? _sessionToken;
  bool _isLoading = false;
  String? _error;

  AuthProvider({
    required ApiService apiService,
    GoogleSignIn? googleSignIn,
    FlutterSecureStorage? secureStorage,
  })  : _apiService = apiService,
        _googleSignIn = googleSignIn ?? GoogleSignIn(scopes: ['email', 'profile']),
        _secureStorage = secureStorage ?? const FlutterSecureStorage();

  User? get user => _user;
  bool get isAuthenticated => _user != null && _sessionToken != null;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> initialize() async {
    _isLoading = true;
    notifyListeners();

    try {
      // Try to load saved session
      _sessionToken = await _secureStorage.read(key: 'session_token');
      if (_sessionToken != null) {
        _apiService.setSessionToken(_sessionToken);
        
        // Verify token by fetching user profile
        await fetchUserProfile();
      }
    } catch (e) {
      debugPrint('Error initializing auth: $e');
      await _clearSession();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> signInWithGoogle() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      // Sign in with Google
      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();
      if (googleUser == null) {
        // User cancelled
        _isLoading = false;
        notifyListeners();
        return;
      }

      final GoogleSignInAuthentication googleAuth = await googleUser.authentication;
      
      // Send ID token to backend
      final response = await _apiService.post(
        ApiConstants.authGoogle,
        data: {
          'idToken': googleAuth.idToken,
        },
      );

      // Save session
      _sessionToken = response.data['sessionToken'] as String;
      _user = User.fromJson(response.data['user'] as Map<String, dynamic>);
      
      await _secureStorage.write(key: 'session_token', value: _sessionToken);
      _apiService.setSessionToken(_sessionToken);

      _error = null;
    } on ApiException catch (e) {
      _error = e.getUserFriendlyMessage();
      await _clearSession();
    } catch (e) {
      _error = 'Failed to sign in. Please try again.';
      await _clearSession();
      debugPrint('Sign in error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> signOut() async {
    _isLoading = true;
    notifyListeners();

    try {
      // Sign out from backend
      if (_sessionToken != null) {
        await _apiService.post(ApiConstants.authLogout);
      }
    } catch (e) {
      debugPrint('Error signing out from backend: $e');
    }

    try {
      // Sign out from Google
      await _googleSignIn.signOut();
    } catch (e) {
      debugPrint('Error signing out from Google: $e');
    }

    await _clearSession();
    
    _isLoading = false;
    notifyListeners();
  }

  Future<void> fetchUserProfile() async {
    try {
      final response = await _apiService.get(ApiConstants.userMe);
      _user = User.fromJson(response.data as Map<String, dynamic>);
      notifyListeners();
    } on ApiException catch (e) {
      if (e.statusCode == 401) {
        // Token expired
        await _clearSession();
      }
      rethrow;
    }
  }

  Future<void> updatePreferences(UserPreferences preferences) async {
    try {
      await _apiService.patch(
        ApiConstants.userMe,
        data: {
          'preferences': preferences.toJson(),
        },
      );

      if (_user != null) {
        _user = User(
          userId: _user!.userId,
          email: _user!.email,
          displayName: _user!.displayName,
          photoURL: _user!.photoURL,
          createdAt: _user!.createdAt,
          lastLoginAt: _user!.lastLoginAt,
          preferences: preferences,
          stats: _user!.stats,
          rateLimits: _user!.rateLimits,
        );
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error updating preferences: $e');
      rethrow;
    }
  }

  Future<void> _clearSession() async {
    _user = null;
    _sessionToken = null;
    await _secureStorage.delete(key: 'session_token');
    _apiService.setSessionToken(null);
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}

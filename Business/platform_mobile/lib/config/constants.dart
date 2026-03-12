class ApiConstants {
  static const String baseUrl = 'http://localhost:3000/api/v1';
  static const String baseUrlAndroid = 'http://10.0.2.2:3000/api/v1'; // Android emulator

  // Auth
  static const String requestOtp = '/auth/otp/request';
  static const String verifyOtp = '/auth/otp/verify';
  static const String refreshToken = '/auth/refresh';

  // Users
  static const String me = '/users/me';
  static const String userProfile = '/users'; // + /:id

  // Profiles
  static const String profiles = '/profiles';

  // Categories
  static const String categories = '/categories';

  // Listings
  static const String listings = '/listings';
  static const String searchListings = '/listings/search';

  // Applications
  static const String applications = '/applications';

  // Reviews
  static const String reviews = '/reviews';

  // Chat
  static const String conversations = '/chat/conversations';

  // Notifications
  static const String notifications = '/notifications';

  // Upload
  static const String upload = '/upload';

  // Verification
  static const String verification = '/verification';
}

class AppConstants {
  static const String appName = 'Huduma Platform';
  static const int otpLength = 6;
  static const int otpExpirySeconds = 300;
  static const int defaultPageSize = 20;
  static const double defaultSearchRadiusKm = 20;
}

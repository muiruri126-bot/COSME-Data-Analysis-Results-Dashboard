class User {
  final String id;
  final String phone;
  final String? email;
  final String status;
  final bool isVerified;
  final List<String> roles;
  final Profile? profile;

  User({
    required this.id,
    required this.phone,
    this.email,
    required this.status,
    required this.isVerified,
    required this.roles,
    this.profile,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? '',
      phone: json['phone'] ?? '',
      email: json['email'],
      status: json['status'] ?? 'pending_profile',
      isVerified: json['isVerified'] ?? false,
      roles: (json['roles'] as List?)?.map((r) => r is String ? r : (r['roleType'] as String)).toList() ?? [],
      profile: json['profile'] != null ? Profile.fromJson(json['profile']) : null,
    );
  }

  bool get isProvider => roles.any((r) => r.startsWith('provider'));
  bool get isClient => roles.any((r) => r.startsWith('client'));
  bool get hasProfile => profile != null;
}

class Profile {
  final String id;
  final String firstName;
  final String lastName;
  final String? displayName;
  final String? bio;
  final String? avatarUrl;
  final DateTime? dateOfBirth;
  final String? gender;
  final double averageRating;
  final int totalReviews;
  final int totalCompletedJobs;
  final bool isAvailable;
  final Location? primaryLocation;

  Profile({
    required this.id,
    required this.firstName,
    required this.lastName,
    this.displayName,
    this.bio,
    this.avatarUrl,
    this.dateOfBirth,
    this.gender,
    required this.averageRating,
    required this.totalReviews,
    required this.totalCompletedJobs,
    required this.isAvailable,
    this.primaryLocation,
  });

  String get fullName => displayName ?? '$firstName $lastName';

  factory Profile.fromJson(Map<String, dynamic> json) {
    return Profile(
      id: json['id'] ?? '',
      firstName: json['firstName'] ?? '',
      lastName: json['lastName'] ?? '',
      displayName: json['displayName'],
      bio: json['bio'],
      avatarUrl: json['avatarUrl'],
      dateOfBirth: json['dateOfBirth'] != null ? DateTime.parse(json['dateOfBirth']) : null,
      gender: json['gender'],
      averageRating: double.tryParse('${json['averageRating'] ?? 0}') ?? 0.0,
      totalReviews: json['totalReviews'] is int ? json['totalReviews'] : int.tryParse('${json['totalReviews'] ?? 0}') ?? 0,
      totalCompletedJobs: json['totalCompletedJobs'] is int ? json['totalCompletedJobs'] : int.tryParse('${json['totalCompletedJobs'] ?? 0}') ?? 0,
      isAvailable: json['isAvailable'] ?? true,
      primaryLocation: json['primaryLocation'] != null
          ? Location.fromJson(json['primaryLocation'])
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
    'firstName': firstName,
    'lastName': lastName,
    'displayName': displayName,
    'bio': bio,
    'gender': gender,
    'dateOfBirth': dateOfBirth?.toIso8601String(),
  };
}

class Location {
  final String? id;
  final String county;
  final String? subCounty;
  final String? estateArea;
  final double? latitude;
  final double? longitude;

  Location({
    this.id,
    required this.county,
    this.subCounty,
    this.estateArea,
    this.latitude,
    this.longitude,
  });

  factory Location.fromJson(Map<String, dynamic> json) {
    return Location(
      id: json['id'],
      county: json['county'] ?? '',
      subCounty: json['subCounty'],
      estateArea: json['estateArea'],
      latitude: json['latitude'] != null ? double.tryParse('${json['latitude']}') : null,
      longitude: json['longitude'] != null ? double.tryParse('${json['longitude']}') : null,
    );
  }

  Map<String, dynamic> toJson() => {
    'county': county,
    'subCounty': subCounty,
    'estateArea': estateArea,
    'latitude': latitude,
    'longitude': longitude,
  };

  String get displayName {
    final parts = <String>[county];
    if (subCounty != null) parts.add(subCounty!);
    if (estateArea != null) parts.add(estateArea!);
    return parts.join(', ');
  }
}

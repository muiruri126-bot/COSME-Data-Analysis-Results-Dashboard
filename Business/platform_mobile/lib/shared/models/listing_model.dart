double? _toDouble(dynamic v) {
  if (v == null) return null;
  if (v is num) return v.toDouble();
  if (v is String) return double.tryParse(v);
  return null;
}

class Listing {
  final String id;
  final String title;
  final String? description;
  final String categoryId;
  final String userId;
  final String listingType;
  final String status;
  final double? budgetMin;
  final double? budgetMax;
  final String? budgetPeriod;
  final String? engagementType;
  final List<String> images;
  final Map<String, dynamic>? attributes;
  final DateTime createdAt;
  final DateTime? expiresAt;

  // Joined data
  final ListingCategory? category;
  final ListingLocation? location;
  final ListingUser? user;
  final int? applicationCount;
  final double? distance;

  Listing({
    required this.id,
    required this.title,
    this.description,
    required this.categoryId,
    required this.userId,
    required this.listingType,
    required this.status,
    this.budgetMin,
    this.budgetMax,
    this.budgetPeriod,
    this.engagementType,
    required this.images,
    this.attributes,
    required this.createdAt,
    this.expiresAt,
    this.category,
    this.location,
    this.user,
    this.applicationCount,
    this.distance,
  });

  factory Listing.fromJson(Map<String, dynamic> json) {
    return Listing(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      categoryId: json['categoryId'],
      userId: json['userId'],
      listingType: json['listingType'],
      status: json['status'],
      budgetMin: _toDouble(json['budgetMin']),
      budgetMax: _toDouble(json['budgetMax']),
      budgetPeriod: json['budgetPeriod'],
      engagementType: json['engagementType'],
      images: List<String>.from(json['images'] ?? []),
      attributes: json['attributes'],
      createdAt: DateTime.parse(json['createdAt']),
      expiresAt: json['expiresAt'] != null ? DateTime.parse(json['expiresAt']) : null,
      category: json['category'] != null ? ListingCategory.fromJson(json['category']) : null,
      location: json['location'] != null ? ListingLocation.fromJson(json['location']) : null,
      user: json['user'] != null ? ListingUser.fromJson(json['user']) : null,
      applicationCount: json['_count']?['applications'],
      distance: _toDouble(json['_distance']),
    );
  }

  String get budgetDisplay {
    if (budgetMin == null && budgetMax == null) return 'Negotiable';
    final min = budgetMin != null ? 'KES ${budgetMin!.toStringAsFixed(0)}' : '';
    final max = budgetMax != null ? 'KES ${budgetMax!.toStringAsFixed(0)}' : '';
    if (min.isNotEmpty && max.isNotEmpty) return '$min - $max';
    return min.isNotEmpty ? 'From $min' : 'Up to $max';
  }

  String get budgetPeriodDisplay {
    if (budgetPeriod == null) return '';
    return '/${budgetPeriod!.replaceAll('_', ' ')}';
  }

  String get timeAgo {
    final diff = DateTime.now().difference(createdAt);
    if (diff.inDays > 30) return '${(diff.inDays / 30).floor()}mo ago';
    if (diff.inDays > 0) return '${diff.inDays}d ago';
    if (diff.inHours > 0) return '${diff.inHours}h ago';
    if (diff.inMinutes > 0) return '${diff.inMinutes}m ago';
    return 'Just now';
  }
}

class ListingCategory {
  final String name;
  final String slug;
  final String? iconUrl;

  ListingCategory({required this.name, required this.slug, this.iconUrl});

  factory ListingCategory.fromJson(Map<String, dynamic> json) {
    return ListingCategory(
      name: json['name'],
      slug: json['slug'],
      iconUrl: json['iconUrl'],
    );
  }
}

class ListingLocation {
  final String county;
  final String? subCounty;
  final String? estateArea;

  ListingLocation({required this.county, this.subCounty, this.estateArea});

  factory ListingLocation.fromJson(Map<String, dynamic> json) {
    return ListingLocation(
      county: json['county'],
      subCounty: json['subCounty'],
      estateArea: json['estateArea'],
    );
  }

  String get displayName {
    final parts = <String>[];
    if (estateArea != null) parts.add(estateArea!);
    if (subCounty != null) parts.add(subCounty!);
    parts.add(county);
    return parts.join(', ');
  }
}

class ListingUser {
  final String id;
  final bool isVerified;
  final ListingUserProfile? profile;

  ListingUser({required this.id, required this.isVerified, this.profile});

  factory ListingUser.fromJson(Map<String, dynamic> json) {
    return ListingUser(
      id: json['id'],
      isVerified: json['isVerified'] ?? false,
      profile: json['profile'] != null ? ListingUserProfile.fromJson(json['profile']) : null,
    );
  }
}

class ListingUserProfile {
  final String? displayName;
  final String? avatarUrl;
  final double? averageRating;

  ListingUserProfile({this.displayName, this.avatarUrl, this.averageRating});

  factory ListingUserProfile.fromJson(Map<String, dynamic> json) {
    return ListingUserProfile(
      displayName: json['displayName'],
      avatarUrl: json['avatarUrl'],
      averageRating: _toDouble(json['averageRating']),
    );
  }
}

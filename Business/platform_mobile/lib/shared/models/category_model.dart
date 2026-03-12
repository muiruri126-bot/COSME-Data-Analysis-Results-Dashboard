class ServiceCategory {
  final String id;
  final String name;
  final String slug;
  final String? description;
  final String? iconUrl;
  final String listingType;
  final Map<String, dynamic>? attributeSchema;
  final int? listingCount;

  ServiceCategory({
    required this.id,
    required this.name,
    required this.slug,
    this.description,
    this.iconUrl,
    required this.listingType,
    this.attributeSchema,
    this.listingCount,
  });

  factory ServiceCategory.fromJson(Map<String, dynamic> json) {
    return ServiceCategory(
      id: json['id'],
      name: json['name'],
      slug: json['slug'],
      description: json['description'],
      iconUrl: json['iconUrl'],
      listingType: json['listingType'] ?? 'job',
      attributeSchema: json['attributeSchema'],
      listingCount: json['_count']?['listings'],
    );
  }

  /// Maps backend listingType enum to user-friendly group name
  String get parentGroup {
    switch (listingType) {
      case 'job':
        return 'Home & Domestic';
      case 'service_request':
        return 'Services & Trades';
      case 'rental':
        return 'Housing & Rentals';
      case 'space':
        return 'Spaces & Venues';
      default:
        return 'Other';
    }
  }

  String get emoji {
    switch (slug) {
      case 'house-help': return '🏠';
      case 'nanny': return '👶';
      case 'caregiver': return '👴';
      case 'cleaner': return '🧹';
      case 'gardener': return '🌿';
      case 'plumber': return '🔧';
      case 'electrician': return '⚡';
      case 'carpenter': return '🪚';
      case 'painter': return '🎨';
      case 'mason': return '🧱';
      case 'driver': return '🚗';
      case 'rental-apartment': return '🏢';
      case 'short-term-rental': return '🏨';
      case 'shared-housing': return '🏘️';
      case 'office-space': return '🏬';
      case 'event-venue': return '🎪';
      case 'tutor': return '📚';
      case 'freelancer': return '💻';
      case 'tech-support': return '🖥️';
      default: return '📋';
    }
  }
}

import 'package:flutter/material.dart';

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

  IconData get icon {
    switch (slug) {
      case 'house-help': return Icons.home_rounded;
      case 'nanny': return Icons.child_care_rounded;
      case 'caregiver': return Icons.health_and_safety_rounded;
      case 'cleaner': return Icons.cleaning_services_rounded;
      case 'gardener': return Icons.yard_rounded;
      case 'plumber': return Icons.plumbing_rounded;
      case 'electrician': return Icons.electrical_services_rounded;
      case 'carpenter': return Icons.handyman_rounded;
      case 'painter': return Icons.format_paint_rounded;
      case 'mason': return Icons.construction_rounded;
      case 'driver': return Icons.directions_car_rounded;
      case 'rental-apartment': return Icons.apartment_rounded;
      case 'short-term-rental': return Icons.hotel_rounded;
      case 'shared-housing': return Icons.holiday_village_rounded;
      case 'office-space': return Icons.business_rounded;
      case 'event-venue': return Icons.festival_rounded;
      case 'tutor': return Icons.menu_book_rounded;
      case 'freelancer': return Icons.laptop_rounded;
      case 'tech-support': return Icons.support_agent_rounded;
      default: return Icons.category_rounded;
    }
  }

  Color get iconColor {
    switch (slug) {
      case 'house-help': return const Color(0xFF4CAF50);
      case 'nanny': return const Color(0xFFE91E63);
      case 'caregiver': return const Color(0xFF9C27B0);
      case 'cleaner': return const Color(0xFF00BCD4);
      case 'gardener': return const Color(0xFF4CAF50);
      case 'plumber': return const Color(0xFF2196F3);
      case 'electrician': return const Color(0xFFFFC107);
      case 'carpenter': return const Color(0xFF795548);
      case 'painter': return const Color(0xFFFF5722);
      case 'mason': return const Color(0xFF607D8B);
      case 'driver': return const Color(0xFF3F51B5);
      case 'rental-apartment': return const Color(0xFF009688);
      case 'short-term-rental': return const Color(0xFF673AB7);
      case 'shared-housing': return const Color(0xFF8BC34A);
      case 'office-space': return const Color(0xFF03A9F4);
      case 'event-venue': return const Color(0xFFFF9800);
      case 'tutor': return const Color(0xFF3F51B5);
      case 'freelancer': return const Color(0xFF009688);
      case 'tech-support': return const Color(0xFF607D8B);
      default: return const Color(0xFF9E9E9E);
    }
  }
}

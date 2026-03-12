import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:platform_mobile/config/theme/app_theme.dart';
import 'package:platform_mobile/shared/models/listing_model.dart';

class ListingCard extends StatelessWidget {
  final Listing listing;
  final VoidCallback onTap;

  const ListingCard({super.key, required this.listing, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header row
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Category badge
                  if (listing.category != null)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: AppColors.primaryLight.withValues(alpha: 0.2),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        listing.category!.name,
                        style: const TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: AppColors.primaryDark,
                        ),
                      ),
                    ),
                  const Spacer(),
                  Text(
                    listing.timeAgo,
                    style: const TextStyle(
                      fontSize: 12,
                      color: AppColors.textTertiary,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 10),

              // Title
              Text(
                listing.title,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),

              if (listing.description != null) ...[
                const SizedBox(height: 6),
                Text(
                  listing.description!,
                  style: const TextStyle(
                    fontSize: 13,
                    color: AppColors.textSecondary,
                    height: 1.4,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],

              const SizedBox(height: 12),

              // Image row
              if (listing.images.isNotEmpty)
                SizedBox(
                  height: 80,
                  child: ListView.separated(
                    scrollDirection: Axis.horizontal,
                    itemCount: listing.images.length.clamp(0, 3),
                    separatorBuilder: (_, __) => const SizedBox(width: 8),
                    itemBuilder: (context, index) => ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: CachedNetworkImage(
                        imageUrl: listing.images[index],
                        width: 80,
                        height: 80,
                        fit: BoxFit.cover,
                        placeholder: (_, __) => Container(
                          color: AppColors.surfaceVariant,
                          child: const Icon(Icons.image, color: AppColors.textTertiary),
                        ),
                        errorWidget: (_, __, ___) => Container(
                          color: AppColors.surfaceVariant,
                          child: const Icon(Icons.broken_image, color: AppColors.textTertiary),
                        ),
                      ),
                    ),
                  ),
                ),

              if (listing.images.isNotEmpty) const SizedBox(height: 12),

              // Footer
              Row(
                children: [
                  // Budget
                  Icon(Icons.payments_outlined, size: 16, color: AppColors.success),
                  const SizedBox(width: 4),
                  Text(
                    '${listing.budgetDisplay}${listing.budgetPeriodDisplay}',
                    style: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: AppColors.success,
                    ),
                  ),

                  const Spacer(),

                  // Location
                  if (listing.location != null) ...[
                    const Icon(Icons.location_on_outlined, size: 14, color: AppColors.textTertiary),
                    const SizedBox(width: 2),
                    Flexible(
                      child: Text(
                        listing.location!.displayName,
                        style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],

                  if (listing.distance != null) ...[
                    const SizedBox(width: 8),
                    Text(
                      '${listing.distance!.toStringAsFixed(1)} km',
                      style: const TextStyle(fontSize: 12, color: AppColors.textTertiary),
                    ),
                  ],
                ],
              ),

              // User info
              if (listing.user?.profile != null) ...[
                const SizedBox(height: 10),
                const Divider(height: 1),
                const SizedBox(height: 10),
                Row(
                  children: [
                    CircleAvatar(
                      radius: 14,
                      backgroundColor: AppColors.surfaceVariant,
                      backgroundImage: listing.user!.profile!.avatarUrl != null
                          ? CachedNetworkImageProvider(listing.user!.profile!.avatarUrl!)
                          : null,
                      child: listing.user!.profile!.avatarUrl == null
                          ? const Icon(Icons.person, size: 16, color: AppColors.textTertiary)
                          : null,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        listing.user!.profile!.displayName ?? 'Anonymous',
                        style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500),
                      ),
                    ),
                    if (listing.user!.isVerified)
                      const Icon(Icons.verified, size: 16, color: AppColors.info),
                    if (listing.user!.profile!.averageRating != null &&
                        listing.user!.profile!.averageRating! > 0) ...[
                      const SizedBox(width: 8),
                      const Icon(Icons.star, size: 14, color: AppColors.starFilled),
                      const SizedBox(width: 2),
                      Text(
                        listing.user!.profile!.averageRating!.toStringAsFixed(1),
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                      ),
                    ],
                    if (listing.applicationCount != null) ...[
                      const SizedBox(width: 12),
                      Text(
                        '${listing.applicationCount} applied',
                        style: const TextStyle(fontSize: 12, color: AppColors.textTertiary),
                      ),
                    ],
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:platform_mobile/config/theme/app_theme.dart';
import 'package:platform_mobile/core/di/service_locator.dart';
import 'package:platform_mobile/features/applications/repository/applications_repository.dart';
import 'package:platform_mobile/features/listings/repository/listings_repository.dart';
import 'package:platform_mobile/shared/models/listing_model.dart';

class ListingDetailScreen extends StatefulWidget {
  final String listingId;
  const ListingDetailScreen({super.key, required this.listingId});

  @override
  State<ListingDetailScreen> createState() => _ListingDetailScreenState();
}

class _ListingDetailScreenState extends State<ListingDetailScreen> {
  late Future<Listing> _listingFuture;

  @override
  void initState() {
    super.initState();
    _listingFuture = sl<ListingsRepository>().getById(widget.listingId);
  }

  void _showApplyDialog(Listing listing) {
    final messageController = TextEditingController();
    final rateController = TextEditingController();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        bool isSubmitting = false;
        return StatefulBuilder(
          builder: (ctx, setSheetState) {
            return Padding(
              padding: EdgeInsets.fromLTRB(
                  24, 24, 24, MediaQuery.of(ctx).viewInsets.bottom + 24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Apply to: ${listing.title}',
                    style: const TextStyle(
                        fontSize: 18, fontWeight: FontWeight.bold),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 20),
                  TextField(
                    controller: messageController,
                    maxLines: 3,
                    maxLength: 500,
                    textCapitalization: TextCapitalization.sentences,
                    decoration: const InputDecoration(
                      labelText: 'Cover Message (optional)',
                      hintText: 'Why are you a good fit?',
                      alignLabelWithHint: true,
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: rateController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: 'Proposed Rate (KES, optional)',
                      hintText: 'e.g., 5000',
                      prefixIcon: Icon(Icons.payments_outlined),
                    ),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: isSubmitting
                        ? null
                        : () async {
                            setSheetState(() => isSubmitting = true);
                            final data = <String, dynamic>{
                              'listingId': listing.id,
                            };
                            final msg = messageController.text.trim();
                            if (msg.isNotEmpty) data['coverMessage'] = msg;
                            final rate =
                                double.tryParse(rateController.text.trim());
                            if (rate != null) data['proposedRate'] = rate;

                            try {
                              await sl<ApplicationsRepository>().apply(data);
                              if (ctx.mounted) {
                                Navigator.of(ctx).pop();
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text('Application submitted!'),
                                    backgroundColor: AppColors.success,
                                  ),
                                );
                              }
                            } catch (e) {
                              setSheetState(() => isSubmitting = false);
                              if (ctx.mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text('$e'),
                                    backgroundColor: AppColors.error,
                                  ),
                                );
                              }
                            }
                          },
                    child: isSubmitting
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(
                                strokeWidth: 2, color: Colors.white),
                          )
                        : const Text('Submit Application'),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Listing>(
      future: _listingFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        if (snapshot.hasError) {
          return Scaffold(
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text('${snapshot.error}', style: const TextStyle(color: AppColors.error)),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () {
                      setState(() {
                        _listingFuture = sl<ListingsRepository>().getById(widget.listingId);
                      });
                    },
                    child: const Text('Retry'),
                  ),
                ],
              ),
            ),
          );
        }

        final listing = snapshot.data!;
        return Scaffold(
          body: CustomScrollView(
            slivers: [
              // Image header
              SliverAppBar(
                expandedHeight: listing.images.isNotEmpty ? 280 : 0,
                pinned: true,
                leading: IconButton(
                  icon: const CircleAvatar(
                    backgroundColor: Colors.black26,
                    child: Icon(Icons.arrow_back, color: Colors.white),
                  ),
                  onPressed: () => context.pop(),
                ),
                flexibleSpace: listing.images.isNotEmpty
                    ? FlexibleSpaceBar(
                        background: PageView.builder(
                          itemCount: listing.images.length,
                          itemBuilder: (context, index) => CachedNetworkImage(
                            imageUrl: listing.images[index],
                            fit: BoxFit.cover,
                            placeholder: (_, __) => Container(color: AppColors.surfaceVariant),
                            errorWidget: (_, __, ___) => Container(
                              color: AppColors.surfaceVariant,
                              child: const Icon(Icons.broken_image, size: 48),
                            ),
                          ),
                        ),
                      )
                    : null,
              ),

              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Category badge
                      if (listing.category != null)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                          decoration: BoxDecoration(
                            color: AppColors.primaryLight.withValues(alpha: 0.2),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            listing.category!.name,
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: AppColors.primaryDark,
                            ),
                          ),
                        ),

                      const SizedBox(height: 12),

                      // Title
                      Text(
                        listing.title,
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      const SizedBox(height: 8),
                      Text(listing.timeAgo, style: TextStyle(color: AppColors.textTertiary)),

                      const SizedBox(height: 20),

                      // Budget
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: AppColors.success.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.payments_outlined, color: AppColors.success),
                            const SizedBox(width: 12),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'Budget',
                                  style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                                ),
                                Text(
                                  '${listing.budgetDisplay}${listing.budgetPeriodDisplay}',
                                  style: const TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                    color: AppColors.success,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),

                      const SizedBox(height: 20),

                      // Description
                      if (listing.description != null) ...[
                        Text(
                          'Description',
                          style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                fontWeight: FontWeight.w600,
                              ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          listing.description!,
                          style: TextStyle(color: AppColors.textSecondary, height: 1.6),
                        ),
                        const SizedBox(height: 20),
                      ],

                      // Details
                      if (listing.engagementType != null || listing.location != null)
                        Card(
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              children: [
                                if (listing.engagementType != null)
                                  _DetailRow(
                                    icon: Icons.work_outline,
                                    label: 'Engagement',
                                    value: listing.engagementType!.replaceAll('_', ' '),
                                  ),
                                if (listing.location != null)
                                  _DetailRow(
                                    icon: Icons.location_on_outlined,
                                    label: 'Location',
                                    value: listing.location!.displayName,
                                  ),
                                if (listing.applicationCount != null)
                                  _DetailRow(
                                    icon: Icons.people_outline,
                                    label: 'Applications',
                                    value: '${listing.applicationCount} applied',
                                  ),
                              ],
                            ),
                          ),
                        ),

                      const SizedBox(height: 20),

                      // Posted by
                      if (listing.user?.profile != null) ...[
                        Text(
                          'Posted by',
                          style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                fontWeight: FontWeight.w600,
                              ),
                        ),
                        const SizedBox(height: 12),
                        GestureDetector(
                          onTap: () => context.push('/user/${listing.userId}'),
                          child: Row(
                            children: [
                              CircleAvatar(
                                radius: 24,
                                backgroundColor: AppColors.surfaceVariant,
                                backgroundImage: listing.user!.profile!.avatarUrl != null
                                    ? CachedNetworkImageProvider(
                                        listing.user!.profile!.avatarUrl!)
                                    : null,
                                child: listing.user!.profile!.avatarUrl == null
                                    ? const Icon(Icons.person,
                                        color: AppColors.textTertiary)
                                    : null,
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      children: [
                                        Text(
                                          listing.user!.profile!.displayName ?? 'User',
                                          style: const TextStyle(fontWeight: FontWeight.w600),
                                        ),
                                        if (listing.user!.isVerified) ...[
                                          const SizedBox(width: 4),
                                          const Icon(Icons.verified,
                                              size: 16, color: AppColors.info),
                                        ],
                                      ],
                                    ),
                                    if (listing.user!.profile!.averageRating != null &&
                                        listing.user!.profile!.averageRating! > 0)
                                      Row(
                                        children: [
                                          const Icon(Icons.star,
                                              size: 14, color: AppColors.starFilled),
                                          const SizedBox(width: 4),
                                          Text(
                                            listing.user!.profile!.averageRating!
                                                .toStringAsFixed(1),
                                            style: const TextStyle(fontSize: 13),
                                          ),
                                        ],
                                      ),
                                  ],
                                ),
                              ),
                              const Icon(Icons.chevron_right, color: AppColors.textTertiary),
                            ],
                          ),
                        ),
                      ],

                      const SizedBox(height: 100),
                    ],
                  ),
                ),
              ),
            ],
          ),

          // Bottom action bar
          bottomNavigationBar: SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: ElevatedButton(
                onPressed: () => _showApplyDialog(listing),
                child: const Text('Apply Now'),
              ),
            ),
          ),
        );
      },
    );
  }
}

class _DetailRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _DetailRow({required this.icon, required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Icon(icon, size: 20, color: AppColors.textSecondary),
          const SizedBox(width: 12),
          Text(label, style: TextStyle(color: AppColors.textSecondary)),
          const Spacer(),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}

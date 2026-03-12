import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:platform_mobile/config/theme/app_theme.dart';
import 'package:platform_mobile/core/di/service_locator.dart';
import 'package:platform_mobile/features/applications/repository/applications_repository.dart';
import 'package:platform_mobile/shared/models/models.dart';

class ApplicationsScreen extends StatefulWidget {
  const ApplicationsScreen({super.key});

  @override
  State<ApplicationsScreen> createState() => _ApplicationsScreenState();
}

class _ApplicationsScreenState extends State<ApplicationsScreen> {
  late Future<List<Application>> _applicationsFuture;

  @override
  void initState() {
    super.initState();
    _applicationsFuture = sl<ApplicationsRepository>().getMyApplications();
  }

  void _refresh() {
    setState(() {
      _applicationsFuture = sl<ApplicationsRepository>().getMyApplications();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Applications')),
      body: FutureBuilder<List<Application>>(
        future: _applicationsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text('${snapshot.error}', style: const TextStyle(color: AppColors.error)),
                  const SizedBox(height: 16),
                  ElevatedButton(onPressed: _refresh, child: const Text('Retry')),
                ],
              ),
            );
          }

          final applications = snapshot.data ?? [];
          if (applications.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.work_off_outlined, size: 64, color: AppColors.textTertiary),
                  const SizedBox(height: 16),
                  Text(
                    'No applications yet',
                    style: TextStyle(color: AppColors.textSecondary, fontSize: 16),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Apply to listings to see them here',
                    style: TextStyle(color: AppColors.textTertiary),
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () async => _refresh(),
            child: ListView.separated(
              padding: const EdgeInsets.all(20),
              itemCount: applications.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                final app = applications[index];
                return _ApplicationCard(application: app);
              },
            ),
          );
        },
      ),
    );
  }
}

class _ApplicationCard extends StatelessWidget {
  final Application application;

  const _ApplicationCard({required this.application});

  Color get _statusColor {
    switch (application.status) {
      case 'pending':
        return AppColors.warning;
      case 'accepted':
        return AppColors.success;
      case 'rejected':
        return AppColors.error;
      case 'withdrawn':
        return AppColors.textTertiary;
      default:
        return AppColors.textSecondary;
    }
  }

  String get _statusLabel {
    switch (application.status) {
      case 'pending':
        return 'Pending';
      case 'accepted':
        return 'Accepted';
      case 'rejected':
        return 'Rejected';
      case 'withdrawn':
        return 'Withdrawn';
      default:
        return application.status;
    }
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => context.push('/listing/${application.listingId}'),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      application.listing?.title ?? 'Listing',
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: _statusColor.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      _statusLabel,
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: _statusColor,
                      ),
                    ),
                  ),
                ],
              ),
              if (application.listing?.categoryName != null) ...[
                const SizedBox(height: 8),
                Text(
                  application.listing!.categoryName!,
                  style: TextStyle(fontSize: 13, color: AppColors.textSecondary),
                ),
              ],
              if (application.proposedRate != null) ...[
                const SizedBox(height: 8),
                Row(
                  children: [
                    const Icon(Icons.payments_outlined, size: 16, color: AppColors.success),
                    const SizedBox(width: 4),
                    Text(
                      'KES ${application.proposedRate!.toStringAsFixed(0)}${application.ratePeriod != null ? '/${application.ratePeriod}' : ''}',
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        color: AppColors.success,
                      ),
                    ),
                  ],
                ),
              ],
              const SizedBox(height: 8),
              Text(
                _timeAgo(application.createdAt),
                style: TextStyle(fontSize: 12, color: AppColors.textTertiary),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _timeAgo(DateTime date) {
    final diff = DateTime.now().difference(date);
    if (diff.inDays > 30) return '${(diff.inDays / 30).floor()}mo ago';
    if (diff.inDays > 0) return '${diff.inDays}d ago';
    if (diff.inHours > 0) return '${diff.inHours}h ago';
    if (diff.inMinutes > 0) return '${diff.inMinutes}m ago';
    return 'Just now';
  }
}

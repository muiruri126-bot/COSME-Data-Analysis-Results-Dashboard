import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:platform_mobile/config/theme/app_theme.dart';
import 'package:platform_mobile/core/di/service_locator.dart';
import 'package:platform_mobile/features/chat/repository/chat_repository.dart';
import 'package:platform_mobile/features/profile/bloc/profile_bloc.dart';
import 'package:platform_mobile/features/profile/repository/profile_repository.dart';

class PublicProfileScreen extends StatelessWidget {
  final String userId;
  const PublicProfileScreen({super.key, required this.userId});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => ProfileBloc(sl<ProfileRepository>())..add(LoadPublicProfile(userId)),
      child: Scaffold(
        appBar: AppBar(
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            onPressed: () => context.pop(),
          ),
        ),
        body: BlocBuilder<ProfileBloc, ProfileState>(
          builder: (context, state) {
            if (state is ProfileLoading) {
              return const Center(child: CircularProgressIndicator());
            }
            if (state is ProfileError) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(state.message, style: const TextStyle(color: AppColors.error)),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () => context.read<ProfileBloc>().add(LoadPublicProfile(userId)),
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              );
            }
            if (state is PublicProfileLoaded) {
              final user = state.user;
              final profile = user.profile;
              return SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Column(
                  children: [
                    // Avatar
                    CircleAvatar(
                      radius: 50,
                      backgroundColor: AppColors.surfaceVariant,
                      backgroundImage: profile?.avatarUrl != null
                          ? CachedNetworkImageProvider(profile!.avatarUrl!)
                          : null,
                      child: profile?.avatarUrl == null
                          ? const Icon(Icons.person, size: 48, color: AppColors.textTertiary)
                          : null,
                    ),
                    const SizedBox(height: 16),

                    // Name
                    Text(
                      profile?.fullName ?? 'User',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),

                    if (user.isVerified) ...[
                      const SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.verified, size: 16, color: AppColors.info),
                          const SizedBox(width: 4),
                          Text(
                            'Verified',
                            style: TextStyle(color: AppColors.info, fontWeight: FontWeight.w500),
                          ),
                        ],
                      ),
                    ],

                    const SizedBox(height: 24),

                    // Stats
                    if (profile != null)
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          _StatItem(
                            value: profile.averageRating.toStringAsFixed(1),
                            label: 'Rating',
                            icon: Icons.star,
                            iconColor: AppColors.starFilled,
                          ),
                          _StatItem(
                            value: '${profile.totalReviews}',
                            label: 'Reviews',
                            icon: Icons.rate_review_outlined,
                            iconColor: AppColors.primary,
                          ),
                          _StatItem(
                            value: '${profile.totalCompletedJobs}',
                            label: 'Jobs Done',
                            icon: Icons.check_circle_outline,
                            iconColor: AppColors.success,
                          ),
                        ],
                      ),

                    if (profile?.bio != null && profile!.bio!.isNotEmpty) ...[
                      const SizedBox(height: 24),
                      const Divider(),
                      const SizedBox(height: 16),
                      Align(
                        alignment: Alignment.centerLeft,
                        child: Text(
                          'About',
                          style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                fontWeight: FontWeight.w600,
                              ),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Align(
                        alignment: Alignment.centerLeft,
                        child: Text(
                          profile.bio!,
                          style: TextStyle(color: AppColors.textSecondary, height: 1.5),
                        ),
                      ),
                    ],

                    if (profile?.primaryLocation != null) ...[
                      const SizedBox(height: 16),
                      ListTile(
                        contentPadding: EdgeInsets.zero,
                        leading: const Icon(Icons.location_on_outlined, color: AppColors.textSecondary),
                        title: const Text('Location', style: TextStyle(fontWeight: FontWeight.w500)),
                        subtitle: Text(
                          profile!.primaryLocation!.displayName,
                          style: TextStyle(color: AppColors.textSecondary),
                        ),
                      ),
                    ],

                    const SizedBox(height: 24),

                    // Contact button
                    ElevatedButton.icon(
                      onPressed: () async {
                        try {
                          final conversation = await sl<ChatRepository>()
                              .createConversation(user.id);
                          if (context.mounted) {
                            context.push('/chat/${conversation.id}');
                          }
                        } catch (e) {
                          if (context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text('Could not start conversation')),
                            );
                          }
                        }
                      },
                      icon: const Icon(Icons.chat_bubble_outline),
                      label: const Text('Send Message'),
                    ),
                  ],
                ),
              );
            }
            return const SizedBox.shrink();
          },
        ),
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final String value;
  final String label;
  final IconData icon;
  final Color iconColor;

  const _StatItem({
    required this.value,
    required this.label,
    required this.icon,
    required this.iconColor,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, color: iconColor, size: 24),
        const SizedBox(height: 4),
        Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        Text(label, style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
      ],
    );
  }
}

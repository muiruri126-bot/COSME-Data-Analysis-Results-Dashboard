import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:platform_mobile/config/theme/app_theme.dart';
import 'package:platform_mobile/core/di/service_locator.dart';
import 'package:platform_mobile/features/auth/bloc/auth_bloc.dart';
import 'package:platform_mobile/features/profile/bloc/profile_bloc.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => sl<ProfileBloc>()..add(LoadProfile()),
      child: const _ProfileView(),
    );
  }
}

class _ProfileView extends StatelessWidget {
  const _ProfileView();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit_outlined),
            onPressed: () => context.push('/edit-profile'),
          ),
        ],
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
                    onPressed: () => context.read<ProfileBloc>().add(LoadProfile()),
                    child: const Text('Retry'),
                  ),
                ],
              ),
            );
          }
          if (state is ProfileLoaded) {
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
                    profile?.fullName ?? 'No name set',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    user.phone,
                    style: TextStyle(color: AppColors.textSecondary),
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

                  const SizedBox(height: 24),
                  const Divider(),
                  const SizedBox(height: 8),

                  // Bio
                  if (profile?.bio != null && profile!.bio!.isNotEmpty) ...[
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
                    const SizedBox(height: 16),
                    const Divider(),
                    const SizedBox(height: 8),
                  ],

                  // Location
                  if (profile?.primaryLocation != null) ...[
                    _InfoTile(
                      icon: Icons.location_on_outlined,
                      title: 'Location',
                      subtitle: profile!.primaryLocation!.displayName,
                    ),
                  ],

                  // Member since
                  _InfoTile(
                    icon: Icons.calendar_today_outlined,
                    title: 'Member',
                    subtitle: 'Joined the platform',
                  ),

                  const SizedBox(height: 24),
                  const Divider(),
                  const SizedBox(height: 8),

                  // Actions
                  _ActionTile(
                    icon: Icons.notifications_outlined,
                    title: 'Notifications',
                    onTap: () => context.push('/notifications'),
                  ),
                  _ActionTile(
                    icon: Icons.help_outline,
                    title: 'Help & Support',
                    onTap: () {},
                  ),
                  _ActionTile(
                    icon: Icons.privacy_tip_outlined,
                    title: 'Privacy Policy',
                    onTap: () {},
                  ),

                  const SizedBox(height: 24),

                  // Logout
                  OutlinedButton.icon(
                    onPressed: () {
                      context.read<AuthBloc>().add(AuthLogoutRequested());
                      context.go('/onboarding');
                    },
                    icon: const Icon(Icons.logout, color: AppColors.error),
                    label: const Text('Log Out', style: TextStyle(color: AppColors.error)),
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: AppColors.error),
                      minimumSize: const Size(double.infinity, 52),
                    ),
                  ),
                  const SizedBox(height: 24),
                ],
              ),
            );
          }
          return const SizedBox.shrink();
        },
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

class _InfoTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;

  const _InfoTile({required this.icon, required this.title, required this.subtitle});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: Icon(icon, color: AppColors.textSecondary),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
      subtitle: Text(subtitle, style: TextStyle(color: AppColors.textSecondary)),
    );
  }
}

class _ActionTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final VoidCallback onTap;

  const _ActionTile({required this.icon, required this.title, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: Icon(icon, color: AppColors.textSecondary),
      title: Text(title),
      trailing: const Icon(Icons.chevron_right, color: AppColors.textTertiary),
      onTap: onTap,
    );
  }
}

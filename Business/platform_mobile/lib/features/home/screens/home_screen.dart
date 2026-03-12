import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:platform_mobile/config/theme/app_theme.dart';
import 'package:platform_mobile/core/di/service_locator.dart';
import 'package:platform_mobile/features/auth/bloc/auth_bloc.dart';
import 'package:platform_mobile/features/categories/bloc/categories_bloc.dart';
import 'package:platform_mobile/features/listings/bloc/listings_bloc.dart';
import 'package:platform_mobile/features/listings/repository/listings_repository.dart';
import 'package:platform_mobile/shared/models/category_model.dart';
import 'package:platform_mobile/shared/models/listing_model.dart';
import 'package:platform_mobile/shared/widgets/listing_card.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider(
          create: (_) => sl<CategoriesBloc>()..add(LoadCategories()),
        ),
        BlocProvider(
          create: (_) => ListingsBloc(sl<ListingsRepository>())..add(LoadRecentListings()),
        ),
      ],
      child: const _HomeView(),
    );
  }
}

class _HomeView extends StatelessWidget {
  const _HomeView();

  @override
  Widget build(BuildContext context) {
    final user = context.select((AuthBloc bloc) {
      final state = bloc.state;
      return state is AuthAuthenticated ? state.user : null;
    });

    return Scaffold(
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            // ── Header ──
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 16, 20, 0),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Hello${user?.profile != null ? ', ${user!.profile!.firstName}' : ''} 👋',
                            style: Theme.of(context)
                                .textTheme
                                .titleLarge
                                ?.copyWith(fontWeight: FontWeight.w600),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Find the perfect service today',
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                  color: AppColors.textSecondary,
                                ),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      onPressed: () => context.push('/notifications'),
                      icon: const Badge(
                        smallSize: 8,
                        child: Icon(Icons.notifications_outlined),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // ── Search Bar ──
            SliverToBoxAdapter(
              child: GestureDetector(
                onTap: () => context.push('/search'),
                child: Container(
                  margin: const EdgeInsets.fromLTRB(20, 20, 20, 0),
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                  decoration: BoxDecoration(
                    color: AppColors.surfaceVariant,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.search, color: AppColors.textTertiary),
                      const SizedBox(width: 12),
                      Text(
                        'Search services, housing, providers...',
                        style: TextStyle(
                          color: AppColors.textTertiary,
                          fontSize: 15,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),

            // ── Quick Actions ──
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 24, 20, 0),
                child: Row(
                  children: [
                    _QuickAction(
                      icon: Icons.add_circle_outline,
                      label: 'Post a Job',
                      color: AppColors.primary,
                      onTap: () => context.push('/create-listing'),
                    ),
                    const SizedBox(width: 12),
                    _QuickAction(
                      icon: Icons.home_work_outlined,
                      label: 'Find Housing',
                      color: AppColors.secondary,
                      onTap: () => context.push('/category/rental-apartment',
                          extra: 'Rental Apartments'),
                    ),
                    const SizedBox(width: 12),
                    _QuickAction(
                      icon: Icons.engineering_outlined,
                      label: 'Hire Pro',
                      color: AppColors.info,
                      onTap: () => context.go('/categories'),
                    ),
                  ],
                ),
              ),
            ),

            // ── Categories Section ──
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 28, 20, 12),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Categories',
                      style: Theme.of(context)
                          .textTheme
                          .titleMedium
                          ?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    TextButton(
                      onPressed: () => context.go('/categories'),
                      child: const Text('See all'),
                    ),
                  ],
                ),
              ),
            ),
            SliverToBoxAdapter(
              child: SizedBox(
                height: 100,
                child: BlocBuilder<CategoriesBloc, CategoriesState>(
                  builder: (context, state) {
                    if (state is CategoriesLoaded) {
                      return ListView.separated(
                        padding: const EdgeInsets.symmetric(horizontal: 20),
                        scrollDirection: Axis.horizontal,
                        itemCount: state.categories.length.clamp(0, 8),
                        separatorBuilder: (_, __) => const SizedBox(width: 12),
                        itemBuilder: (context, index) {
                          final cat = state.categories[index];
                          return _CategoryChip(
                            category: cat,
                            onTap: () => context.push(
                              '/category/${cat.slug}',
                              extra: cat.name,
                            ),
                          );
                        },
                      );
                    }
                    return const Center(child: CircularProgressIndicator());
                  },
                ),
              ),
            ),

            // ── Recent Listings ──
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 24, 20, 12),
                child: Text(
                  'Recent Listings',
                  style: Theme.of(context)
                      .textTheme
                      .titleMedium
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
              ),
            ),
            BlocBuilder<ListingsBloc, ListingsState>(
              builder: (context, state) {
                if (state is ListingsLoaded) {
                  if (state.listings.isEmpty) {
                    return const SliverToBoxAdapter(
                      child: Padding(
                        padding: EdgeInsets.all(40),
                        child: Column(
                          children: [
                            Icon(Icons.inbox_outlined, size: 48, color: AppColors.textTertiary),
                            SizedBox(height: 12),
                            Text('No listings yet', style: TextStyle(color: AppColors.textSecondary)),
                          ],
                        ),
                      ),
                    );
                  }
                  return SliverPadding(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    sliver: SliverList.separated(
                      itemCount: state.listings.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 12),
                      itemBuilder: (context, index) {
                        return ListingCard(
                          listing: state.listings[index],
                          onTap: () => context.push('/listing/${state.listings[index].id}'),
                        );
                      },
                    ),
                  );
                }
                if (state is ListingsError) {
                  return SliverToBoxAdapter(
                    child: Center(
                      child: Padding(
                        padding: const EdgeInsets.all(40),
                        child: Text(state.message, style: const TextStyle(color: AppColors.error)),
                      ),
                    ),
                  );
                }
                return const SliverToBoxAdapter(
                  child: Center(
                    child: Padding(
                      padding: EdgeInsets.all(40),
                      child: CircularProgressIndicator(),
                    ),
                  ),
                );
              },
            ),

            const SliverToBoxAdapter(child: SizedBox(height: 20)),
          ],
        ),
      ),
    );
  }
}

class _QuickAction extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _QuickAction({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            children: [
              Icon(icon, color: color, size: 28),
              const SizedBox(height: 8),
              Text(
                label,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: color,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _CategoryChip extends StatelessWidget {
  final ServiceCategory category;
  final VoidCallback onTap;

  const _CategoryChip({required this.category, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: SizedBox(
        width: 80,
        child: Column(
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: AppColors.surfaceVariant,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Center(
                child: Text(
                  category.emoji,
                  style: const TextStyle(fontSize: 28),
                ),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              category.name,
              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w500),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
}

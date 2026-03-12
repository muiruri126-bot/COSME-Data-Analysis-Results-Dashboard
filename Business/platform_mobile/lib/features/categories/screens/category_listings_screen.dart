import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:platform_mobile/config/theme/app_theme.dart';
import 'package:platform_mobile/core/di/service_locator.dart';
import 'package:platform_mobile/features/listings/bloc/listings_bloc.dart';
import 'package:platform_mobile/features/listings/repository/listings_repository.dart';
import 'package:platform_mobile/shared/widgets/listing_card.dart';

class CategoryListingsScreen extends StatelessWidget {
  final String slug;
  final String categoryName;

  const CategoryListingsScreen({
    super.key,
    required this.slug,
    required this.categoryName,
  });

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => ListingsBloc(sl<ListingsRepository>())
        ..add(SearchListings(categorySlug: slug)),
      child: _CategoryListingsView(slug: slug, categoryName: categoryName),
    );
  }
}

class _CategoryListingsView extends StatelessWidget {
  final String slug;
  final String categoryName;

  const _CategoryListingsView({required this.slug, required this.categoryName});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(categoryName),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: BlocBuilder<ListingsBloc, ListingsState>(
        builder: (context, state) {
          if (state is ListingsLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          if (state is ListingsError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(state.message, style: const TextStyle(color: AppColors.error)),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () => context.read<ListingsBloc>().add(
                          SearchListings(categorySlug: slug),
                        ),
                    child: const Text('Retry'),
                  ),
                ],
              ),
            );
          }
          if (state is ListingsLoaded) {
            if (state.listings.isEmpty) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.inbox_outlined, size: 64, color: AppColors.textTertiary),
                    const SizedBox(height: 16),
                    Text(
                      'No listings in $categoryName yet',
                      style: TextStyle(color: AppColors.textSecondary, fontSize: 16),
                    ),
                  ],
                ),
              );
            }
            return NotificationListener<ScrollNotification>(
              onNotification: (notification) {
                if (notification is ScrollEndNotification &&
                    notification.metrics.extentAfter < 200 &&
                    state.hasMore &&
                    !state.isLoadingMore) {
                  context.read<ListingsBloc>().add(LoadMoreListings());
                }
                return false;
              },
              child: ListView.separated(
                padding: const EdgeInsets.all(20),
                itemCount: state.listings.length + (state.isLoadingMore ? 1 : 0),
                separatorBuilder: (_, __) => const SizedBox(height: 12),
                itemBuilder: (context, index) {
                  if (index >= state.listings.length) {
                    return const Center(
                      child: Padding(
                        padding: EdgeInsets.all(16),
                        child: CircularProgressIndicator(),
                      ),
                    );
                  }
                  final listing = state.listings[index];
                  return ListingCard(
                    listing: listing,
                    onTap: () => context.push('/listing/${listing.id}'),
                  );
                },
              ),
            );
          }
          return const SizedBox.shrink();
        },
      ),
    );
  }
}

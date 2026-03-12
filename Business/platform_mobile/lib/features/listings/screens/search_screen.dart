import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:platform_mobile/config/theme/app_theme.dart';
import 'package:platform_mobile/core/di/service_locator.dart';
import 'package:platform_mobile/features/listings/bloc/listings_bloc.dart';
import 'package:platform_mobile/features/listings/repository/listings_repository.dart';
import 'package:platform_mobile/shared/widgets/listing_card.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final _searchController = TextEditingController();
  late final ListingsBloc _listingsBloc;

  @override
  void initState() {
    super.initState();
    _listingsBloc = ListingsBloc(sl<ListingsRepository>());
  }

  @override
  void dispose() {
    _searchController.dispose();
    _listingsBloc.close();
    super.dispose();
  }

  void _onSearch() {
    final query = _searchController.text.trim();
    if (query.isEmpty) return;
    _listingsBloc.add(SearchListings(query: query));
  }

  @override
  Widget build(BuildContext context) {
    return BlocProvider.value(
      value: _listingsBloc,
      child: Scaffold(
        appBar: AppBar(
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            onPressed: () => context.pop(),
          ),
          title: TextField(
            controller: _searchController,
            autofocus: true,
            textInputAction: TextInputAction.search,
            onSubmitted: (_) => _onSearch(),
            decoration: InputDecoration(
              hintText: 'Search services, housing...',
              border: InputBorder.none,
              hintStyle: TextStyle(color: AppColors.textTertiary),
            ),
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.search),
              onPressed: _onSearch,
            ),
          ],
        ),
        body: BlocBuilder<ListingsBloc, ListingsState>(
          builder: (context, state) {
            if (state is ListingsInitial) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.search, size: 64, color: AppColors.textTertiary),
                    const SizedBox(height: 16),
                    Text(
                      'Search for services and listings',
                      style: TextStyle(color: AppColors.textSecondary),
                    ),
                  ],
                ),
              );
            }
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
                    ElevatedButton(onPressed: _onSearch, child: const Text('Retry')),
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
                      const Icon(Icons.search_off, size: 64, color: AppColors.textTertiary),
                      const SizedBox(height: 16),
                      Text(
                        'No results found',
                        style: TextStyle(color: AppColors.textSecondary, fontSize: 16),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Try different keywords',
                        style: TextStyle(color: AppColors.textTertiary),
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
                    _listingsBloc.add(LoadMoreListings());
                  }
                  return false;
                },
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.fromLTRB(20, 12, 20, 8),
                      child: Text(
                        '${state.total} results found',
                        style: TextStyle(color: AppColors.textSecondary, fontSize: 13),
                      ),
                    ),
                    Expanded(
                      child: ListView.separated(
                        padding: const EdgeInsets.symmetric(horizontal: 20),
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

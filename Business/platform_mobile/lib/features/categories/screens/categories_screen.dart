import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:platform_mobile/config/theme/app_theme.dart';
import 'package:platform_mobile/core/di/service_locator.dart';
import 'package:platform_mobile/features/categories/bloc/categories_bloc.dart';
import 'package:platform_mobile/shared/models/category_model.dart';

class CategoriesScreen extends StatelessWidget {
  const CategoriesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => sl<CategoriesBloc>()..add(LoadCategories()),
      child: const _CategoriesView(),
    );
  }
}

class _CategoriesView extends StatelessWidget {
  const _CategoriesView();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Categories')),
      body: BlocBuilder<CategoriesBloc, CategoriesState>(
        builder: (context, state) {
          if (state is CategoriesLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          if (state is CategoriesError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(state.message, style: const TextStyle(color: AppColors.error)),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () => context.read<CategoriesBloc>().add(LoadCategories()),
                    child: const Text('Retry'),
                  ),
                ],
              ),
            );
          }
          if (state is CategoriesLoaded) {
            final grouped = state.grouped;
            return ListView.builder(
              padding: const EdgeInsets.all(20),
              itemCount: grouped.length,
              itemBuilder: (context, index) {
                final group = grouped.keys.elementAt(index);
                final categories = grouped[group]!;
                return _CategoryGroup(group: group, categories: categories);
              },
            );
          }
          return const SizedBox.shrink();
        },
      ),
    );
  }
}

class _CategoryGroup extends StatelessWidget {
  final String group;
  final List<ServiceCategory> categories;

  const _CategoryGroup({required this.group, required this.categories});

  String get _groupTitle {
    // Convert snake_case or lowercase to title case
    return group
        .replaceAll('_', ' ')
        .split(' ')
        .map((w) => w.isNotEmpty ? '${w[0].toUpperCase()}${w.substring(1)}' : '')
        .join(' ');
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 12),
          child: Text(
            _groupTitle,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
        ),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 3,
            childAspectRatio: 0.9,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
          ),
          itemCount: categories.length,
          itemBuilder: (context, index) {
            final cat = categories[index];
            return _CategoryTile(category: cat);
          },
        ),
        const SizedBox(height: 16),
      ],
    );
  }
}

class _CategoryTile extends StatelessWidget {
  final ServiceCategory category;

  const _CategoryTile({required this.category});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => context.push('/category/${category.slug}', extra: category.name),
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.surfaceVariant,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(category.emoji, style: const TextStyle(fontSize: 32)),
            const SizedBox(height: 8),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8),
              child: Text(
                category.name,
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            if (category.listingCount != null) ...[
              const SizedBox(height: 2),
              Text(
                '${category.listingCount} listings',
                style: TextStyle(fontSize: 10, color: AppColors.textTertiary),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

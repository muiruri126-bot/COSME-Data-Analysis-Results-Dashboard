import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:platform_mobile/config/theme/app_theme.dart';
import 'package:platform_mobile/core/di/service_locator.dart';
import 'package:platform_mobile/features/categories/bloc/categories_bloc.dart';
import 'package:platform_mobile/features/categories/repository/categories_repository.dart';
import 'package:platform_mobile/features/listings/repository/listings_repository.dart';
import 'package:platform_mobile/shared/models/category_model.dart';

class CreateListingScreen extends StatefulWidget {
  const CreateListingScreen({super.key});

  @override
  State<CreateListingScreen> createState() => _CreateListingScreenState();
}

class _CreateListingScreenState extends State<CreateListingScreen> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _budgetMinController = TextEditingController();
  final _budgetMaxController = TextEditingController();
  final _countyController = TextEditingController();

  String _listingType = 'job';
  String? _selectedCategoryId;
  String _engagementType = 'one_time';
  String _budgetPeriod = 'monthly';
  bool _isSubmitting = false;

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    _budgetMinController.dispose();
    _budgetMaxController.dispose();
    _countyController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedCategoryId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select a category'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    setState(() => _isSubmitting = true);

    final data = <String, dynamic>{
      'title': _titleController.text.trim(),
      'description': _descriptionController.text.trim(),
      'categoryId': _selectedCategoryId,
      'listingType': _listingType,
      'engagementType': _engagementType,
    };

    final budgetMin = double.tryParse(_budgetMinController.text.trim());
    final budgetMax = double.tryParse(_budgetMaxController.text.trim());
    if (budgetMin != null) data['budgetMin'] = budgetMin;
    if (budgetMax != null) data['budgetMax'] = budgetMax;
    if (budgetMin != null || budgetMax != null) data['budgetPeriod'] = _budgetPeriod;

    final county = _countyController.text.trim();
    if (county.isNotEmpty) {
      data['location'] = {
        'county': county,
        'latitude': 0,
        'longitude': 0,
      };
    }

    try {
      await sl<ListingsRepository>().create(data);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Listing created!'),
            backgroundColor: AppColors.success,
          ),
        );
        context.pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('$e'), backgroundColor: AppColors.error),
        );
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => CategoriesBloc(sl<CategoriesRepository>())..add(LoadCategories()),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Create Listing'),
          leading: IconButton(
            icon: const Icon(Icons.close),
            onPressed: () => context.pop(),
          ),
        ),
        body: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Listing Type
                  Text('What do you need?',
                      style: Theme.of(context)
                          .textTheme
                          .titleSmall
                          ?.copyWith(fontWeight: FontWeight.w600)),
                  const SizedBox(height: 8),
                  SegmentedButton<String>(
                    segments: const [
                      ButtonSegment(
                        value: 'job',
                        label: Text('Hire Someone'),
                        icon: Icon(Icons.person_search),
                      ),
                      ButtonSegment(
                        value: 'service_request',
                        label: Text('Request Service'),
                        icon: Icon(Icons.handshake),
                      ),
                    ],
                    selected: {_listingType},
                    onSelectionChanged: (v) => setState(() => _listingType = v.first),
                  ),
                  const SizedBox(height: 24),

                  // Title
                  TextFormField(
                    controller: _titleController,
                    textCapitalization: TextCapitalization.sentences,
                    decoration: const InputDecoration(
                      labelText: 'Title *',
                      hintText: 'e.g., Looking for a reliable house help',
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) return 'Title is required';
                      if (value.trim().length < 10) return 'At least 10 characters';
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),

                  // Category
                  BlocBuilder<CategoriesBloc, CategoriesState>(
                    builder: (context, state) {
                      List<ServiceCategory> categories = [];
                      if (state is CategoriesLoaded) categories = state.categories;
                      return DropdownButtonFormField<String>(
                        value: _selectedCategoryId,
                        decoration: const InputDecoration(
                          labelText: 'Category *',
                          prefixIcon: Icon(Icons.category_outlined),
                        ),
                        items: categories
                            .map((c) => DropdownMenuItem(value: c.id, child: Text(c.name)))
                            .toList(),
                        onChanged: (value) => setState(() => _selectedCategoryId = value),
                        validator: (v) => v == null ? 'Select a category' : null,
                      );
                    },
                  ),
                  const SizedBox(height: 16),

                  // Description
                  TextFormField(
                    controller: _descriptionController,
                    maxLines: 4,
                    maxLength: 1000,
                    textCapitalization: TextCapitalization.sentences,
                    decoration: const InputDecoration(
                      labelText: 'Description *',
                      hintText: 'Describe what you need in detail...',
                      alignLabelWithHint: true,
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) return 'Description is required';
                      if (value.trim().length < 20) return 'At least 20 characters';
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),

                  // Engagement Type
                  DropdownButtonFormField<String>(
                    value: _engagementType,
                    decoration: const InputDecoration(
                      labelText: 'Engagement Type',
                      prefixIcon: Icon(Icons.schedule_outlined),
                    ),
                    items: const [
                      DropdownMenuItem(value: 'one_time', child: Text('One Time')),
                      DropdownMenuItem(value: 'part_time', child: Text('Part Time')),
                      DropdownMenuItem(value: 'full_time', child: Text('Full Time')),
                      DropdownMenuItem(value: 'contract', child: Text('Contract')),
                    ],
                    onChanged: (value) {
                      if (value != null) setState(() => _engagementType = value);
                    },
                  ),
                  const SizedBox(height: 24),

                  // Budget
                  Text('Budget',
                      style: Theme.of(context)
                          .textTheme
                          .titleSmall
                          ?.copyWith(fontWeight: FontWeight.w600)),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(
                        child: TextFormField(
                          controller: _budgetMinController,
                          keyboardType: TextInputType.number,
                          decoration: const InputDecoration(
                            labelText: 'Min (KES)',
                            hintText: '0',
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: TextFormField(
                          controller: _budgetMaxController,
                          keyboardType: TextInputType.number,
                          decoration: const InputDecoration(
                            labelText: 'Max (KES)',
                            hintText: '0',
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: _budgetPeriod,
                    decoration: const InputDecoration(labelText: 'Budget Period'),
                    items: const [
                      DropdownMenuItem(value: 'hourly', child: Text('Per Hour')),
                      DropdownMenuItem(value: 'daily', child: Text('Per Day')),
                      DropdownMenuItem(value: 'monthly', child: Text('Per Month')),
                      DropdownMenuItem(value: 'fixed', child: Text('Fixed Price')),
                      DropdownMenuItem(value: 'negotiable', child: Text('Negotiable')),
                    ],
                    onChanged: (v) {
                      if (v != null) setState(() => _budgetPeriod = v);
                    },
                  ),
                  const SizedBox(height: 24),

                  // Location
                  TextFormField(
                    controller: _countyController,
                    decoration: const InputDecoration(
                      labelText: 'County',
                      hintText: 'e.g., Nairobi',
                      prefixIcon: Icon(Icons.location_on_outlined),
                    ),
                  ),
                  const SizedBox(height: 32),

                  // Submit
                  ElevatedButton(
                    onPressed: _isSubmitting ? null : _submit,
                    child: _isSubmitting
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                        : const Text('Post Listing'),
                  ),
                  const SizedBox(height: 24),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

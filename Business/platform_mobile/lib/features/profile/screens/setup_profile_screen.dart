import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:platform_mobile/config/theme/app_theme.dart';
import 'package:platform_mobile/core/di/service_locator.dart';
import 'package:platform_mobile/features/auth/bloc/auth_bloc.dart';
import 'package:platform_mobile/features/profile/bloc/profile_bloc.dart';
import 'package:platform_mobile/features/profile/repository/profile_repository.dart';

class SetupProfileScreen extends StatefulWidget {
  const SetupProfileScreen({super.key});

  @override
  State<SetupProfileScreen> createState() => _SetupProfileScreenState();
}

class _SetupProfileScreenState extends State<SetupProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _displayNameController = TextEditingController();
  final _bioController = TextEditingController();
  String? _selectedGender;
  String _selectedCounty = 'Nairobi';

  final _counties = [
    'Nairobi',
    'Mombasa',
    'Kisumu',
    'Nakuru',
    'Eldoret',
    'Thika',
    'Machakos',
    'Nyeri',
    'Meru',
    'Kiambu',
    'Kajiado',
    'Kilifi',
    'Kwale',
    'Lamu',
    'Garissa',
  ];

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _displayNameController.dispose();
    _bioController.dispose();
    super.dispose();
  }

  void _submit(BuildContext blocContext) {
    if (!_formKey.currentState!.validate()) return;

    final data = <String, dynamic>{
      'firstName': _firstNameController.text.trim(),
      'lastName': _lastNameController.text.trim(),
      'location': {
        'county': _selectedCounty,
        'latitude': 0,
        'longitude': 0,
      },
      'roles': <Map<String, dynamic>>[],
    };

    final displayName = _displayNameController.text.trim();
    if (displayName.isNotEmpty) data['displayName'] = displayName;

    final bio = _bioController.text.trim();
    if (bio.isNotEmpty) data['bio'] = bio;

    if (_selectedGender != null) data['gender'] = _selectedGender;

    blocContext.read<ProfileBloc>().add(CreateProfile(data));
  }

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => ProfileBloc(sl<ProfileRepository>()),
      child: BlocListener<ProfileBloc, ProfileState>(
        listener: (context, state) {
          if (state is ProfileCreated) {
            context.read<AuthBloc>().add(AuthCheckRequested());
          } else if (state is ProfileError) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(state.message),
                backgroundColor: AppColors.error,
              ),
            );
          }
        },
        child: Scaffold(
          appBar: AppBar(
            title: const Text('Set Up Your Profile'),
            automaticallyImplyLeading: false,
            actions: [
              TextButton(
                onPressed: () {
                  context.read<AuthBloc>().add(AuthLogoutRequested());
                  context.go('/onboarding');
                },
                child: const Text('Log out'),
              ),
            ],
          ),
          body: SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Tell us about yourself',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'This helps others know who they\'re connecting with.',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: AppColors.textSecondary,
                          ),
                    ),
                    const SizedBox(height: 32),

                    // First Name
                    TextFormField(
                      controller: _firstNameController,
                      textCapitalization: TextCapitalization.words,
                      decoration: const InputDecoration(
                        labelText: 'First Name *',
                        hintText: 'Enter your first name',
                        prefixIcon: Icon(Icons.person_outline),
                      ),
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'First name is required';
                        }
                        if (value.trim().length < 2) {
                          return 'Must be at least 2 characters';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),

                    // Last Name
                    TextFormField(
                      controller: _lastNameController,
                      textCapitalization: TextCapitalization.words,
                      decoration: const InputDecoration(
                        labelText: 'Last Name *',
                        hintText: 'Enter your last name',
                        prefixIcon: Icon(Icons.person_outline),
                      ),
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'Last name is required';
                        }
                        if (value.trim().length < 2) {
                          return 'Must be at least 2 characters';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),

                    // Display Name (optional)
                    TextFormField(
                      controller: _displayNameController,
                      textCapitalization: TextCapitalization.words,
                      decoration: const InputDecoration(
                        labelText: 'Display Name (optional)',
                        hintText: 'How you want others to see you',
                        prefixIcon: Icon(Icons.badge_outlined),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Gender
                    DropdownButtonFormField<String>(
                      value: _selectedGender,
                      decoration: const InputDecoration(
                        labelText: 'Gender (optional)',
                        prefixIcon: Icon(Icons.wc_outlined),
                      ),
                      items: const [
                        DropdownMenuItem(value: 'male', child: Text('Male')),
                        DropdownMenuItem(value: 'female', child: Text('Female')),
                        DropdownMenuItem(value: 'other', child: Text('Other')),
                      ],
                      onChanged: (value) => setState(() => _selectedGender = value),
                    ),
                    const SizedBox(height: 16),

                    // County
                    DropdownButtonFormField<String>(
                      value: _selectedCounty,
                      decoration: const InputDecoration(
                        labelText: 'County *',
                        prefixIcon: Icon(Icons.location_on_outlined),
                      ),
                      items: _counties
                          .map((c) => DropdownMenuItem(value: c, child: Text(c)))
                          .toList(),
                      onChanged: (value) {
                        if (value != null) setState(() => _selectedCounty = value);
                      },
                    ),
                    const SizedBox(height: 16),

                    // Bio
                    TextFormField(
                      controller: _bioController,
                      maxLines: 3,
                      maxLength: 300,
                      textCapitalization: TextCapitalization.sentences,
                      decoration: const InputDecoration(
                        labelText: 'Bio (optional)',
                        hintText: 'Tell people a bit about yourself...',
                        alignLabelWithHint: true,
                        prefixIcon: Padding(
                          padding: EdgeInsets.only(bottom: 48),
                          child: Icon(Icons.edit_note_outlined),
                        ),
                      ),
                    ),
                    const SizedBox(height: 32),

                    // Submit button
                    BlocBuilder<ProfileBloc, ProfileState>(
                      builder: (context, state) {
                        return ElevatedButton(
                          onPressed: state is ProfileLoading ? null : () => _submit(context),
                          child: state is ProfileLoading
                              ? const SizedBox(
                                  height: 20,
                                  width: 20,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    color: Colors.white,
                                  ),
                                )
                              : const Text('Complete Setup'),
                        );
                      },
                    ),
                    const SizedBox(height: 24),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:platform_mobile/core/network/api_client.dart';
import 'package:platform_mobile/features/auth/bloc/auth_bloc.dart';
import 'package:platform_mobile/features/auth/repository/auth_repository.dart';
import 'package:platform_mobile/features/categories/repository/categories_repository.dart';
import 'package:platform_mobile/features/categories/bloc/categories_bloc.dart';
import 'package:platform_mobile/features/listings/repository/listings_repository.dart';
import 'package:platform_mobile/features/listings/bloc/listings_bloc.dart';
import 'package:platform_mobile/features/profile/repository/profile_repository.dart';
import 'package:platform_mobile/features/profile/bloc/profile_bloc.dart';
import 'package:platform_mobile/features/applications/repository/applications_repository.dart';
import 'package:platform_mobile/features/chat/repository/chat_repository.dart';
import 'package:platform_mobile/features/notifications/repository/notifications_repository.dart';

// Simple service locator
final Map<Type, dynamic> _instances = {};

T sl<T>() => _instances[T] as T;

void _register<T>(T instance) {
  _instances[T] = instance;
}

Future<void> setupServiceLocator() async {
  // Core
  const storage = FlutterSecureStorage();
  _register<FlutterSecureStorage>(storage);

  final apiClient = ApiClient(storage);
  _register<ApiClient>(apiClient);

  // Repositories
  _register(AuthRepository(apiClient, storage));
  _register(CategoriesRepository(apiClient));
  _register(ListingsRepository(apiClient));
  _register(ProfileRepository(apiClient));
  _register(ApplicationsRepository(apiClient));
  _register(ChatRepository(apiClient));
  _register(NotificationsRepository(apiClient));

  // BLoCs
  _register(AuthBloc(sl<AuthRepository>()));
  _register(CategoriesBloc(sl<CategoriesRepository>()));
  _register(ProfileBloc(sl<ProfileRepository>()));
}

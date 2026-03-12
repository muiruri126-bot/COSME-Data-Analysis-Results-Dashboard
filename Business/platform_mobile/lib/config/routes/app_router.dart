import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:platform_mobile/features/auth/bloc/auth_bloc.dart';
import 'package:platform_mobile/features/auth/screens/phone_entry_screen.dart';
import 'package:platform_mobile/features/auth/screens/otp_screen.dart';
import 'package:platform_mobile/features/auth/screens/onboarding_screen.dart';
import 'package:platform_mobile/features/home/screens/home_shell.dart';
import 'package:platform_mobile/features/home/screens/home_screen.dart';
import 'package:platform_mobile/features/categories/screens/categories_screen.dart';
import 'package:platform_mobile/features/categories/screens/category_listings_screen.dart';
import 'package:platform_mobile/features/listings/screens/listing_detail_screen.dart';
import 'package:platform_mobile/features/listings/screens/create_listing_screen.dart';
import 'package:platform_mobile/features/listings/screens/search_screen.dart';
import 'package:platform_mobile/features/applications/screens/applications_screen.dart';
import 'package:platform_mobile/features/chat/screens/conversations_screen.dart';
import 'package:platform_mobile/features/chat/screens/chat_screen.dart';
import 'package:platform_mobile/features/profile/screens/profile_screen.dart';
import 'package:platform_mobile/features/profile/screens/edit_profile_screen.dart';
import 'package:platform_mobile/features/profile/screens/public_profile_screen.dart';
import 'package:platform_mobile/features/profile/screens/setup_profile_screen.dart';
import 'package:platform_mobile/features/notifications/screens/notifications_screen.dart';

final _rootNavigatorKey = GlobalKey<NavigatorState>();
final _shellNavigatorKey = GlobalKey<NavigatorState>();

GoRouter buildRouter(AuthBloc authBloc) => GoRouter(
  navigatorKey: _rootNavigatorKey,
  initialLocation: '/',
  redirect: (context, state) {
    final authState = authBloc.state;
    final isAuthRoute = state.matchedLocation == '/login' ||
        state.matchedLocation == '/otp' ||
        state.matchedLocation == '/onboarding' ||
        state.matchedLocation == '/setup-profile';

    // Don't redirect while auth check is in progress
    if (authState is AuthInitial || authState is AuthLoading) {
      return null;
    }

    if (authState is AuthUnauthenticated && !isAuthRoute) {
      return '/onboarding';
    }
    if (authState is AuthNeedsProfile &&
        state.matchedLocation != '/setup-profile') {
      return '/setup-profile';
    }
    if (authState is AuthAuthenticated && isAuthRoute) {
      return '/';
    }
    return null;
  },
  routes: [
    // ── Onboarding & Auth ──
    GoRoute(
      path: '/onboarding',
      builder: (context, state) => const OnboardingScreen(),
    ),
    GoRoute(
      path: '/login',
      builder: (context, state) => const PhoneEntryScreen(),
    ),
    GoRoute(
      path: '/otp',
      builder: (context, state) {
        final phone = state.extra as String? ?? '';
        if (phone.isEmpty) {
          return const PhoneEntryScreen();
        }
        return OtpScreen(phone: phone);
      },
    ),
    GoRoute(
      path: '/setup-profile',
      builder: (context, state) => const SetupProfileScreen(),
    ),

    // ── Main App Shell ──
    ShellRoute(
      navigatorKey: _shellNavigatorKey,
      builder: (context, state, child) => HomeShell(child: child),
      routes: [
        GoRoute(
          path: '/',
          pageBuilder: (context, state) => const NoTransitionPage(
            child: HomeScreen(),
          ),
        ),
        GoRoute(
          path: '/categories',
          pageBuilder: (context, state) => const NoTransitionPage(
            child: CategoriesScreen(),
          ),
        ),
        GoRoute(
          path: '/applications',
          pageBuilder: (context, state) => const NoTransitionPage(
            child: ApplicationsScreen(),
          ),
        ),
        GoRoute(
          path: '/messages',
          pageBuilder: (context, state) => const NoTransitionPage(
            child: ConversationsScreen(),
          ),
        ),
        GoRoute(
          path: '/profile',
          pageBuilder: (context, state) => const NoTransitionPage(
            child: ProfileScreen(),
          ),
        ),
      ],
    ),

    // ── Detail Routes (outside shell) ──
    GoRoute(
      path: '/category/:slug',
      parentNavigatorKey: _rootNavigatorKey,
      builder: (context, state) => CategoryListingsScreen(
        slug: state.pathParameters['slug']!,
        categoryName: state.extra as String? ?? '',
      ),
    ),
    GoRoute(
      path: '/listing/:id',
      parentNavigatorKey: _rootNavigatorKey,
      builder: (context, state) => ListingDetailScreen(
        listingId: state.pathParameters['id']!,
      ),
    ),
    GoRoute(
      path: '/create-listing',
      parentNavigatorKey: _rootNavigatorKey,
      builder: (context, state) => const CreateListingScreen(),
    ),
    GoRoute(
      path: '/search',
      parentNavigatorKey: _rootNavigatorKey,
      builder: (context, state) => const SearchScreen(),
    ),
    GoRoute(
      path: '/chat/:conversationId',
      parentNavigatorKey: _rootNavigatorKey,
      builder: (context, state) => ChatScreen(
        conversationId: state.pathParameters['conversationId']!,
      ),
    ),
    GoRoute(
      path: '/user/:id',
      parentNavigatorKey: _rootNavigatorKey,
      builder: (context, state) => PublicProfileScreen(
        userId: state.pathParameters['id']!,
      ),
    ),
    GoRoute(
      path: '/edit-profile',
      parentNavigatorKey: _rootNavigatorKey,
      builder: (context, state) => const EditProfileScreen(),
    ),
    GoRoute(
      path: '/notifications',
      parentNavigatorKey: _rootNavigatorKey,
      builder: (context, state) => const NotificationsScreen(),
    ),
  ],
);

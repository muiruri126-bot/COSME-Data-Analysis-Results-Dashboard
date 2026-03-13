import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
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
import 'package:platform_mobile/features/notifications/screens/notifications_screen.dart';

final _rootNavigatorKey = GlobalKey<NavigatorState>();

/// GoRouter for the authenticated app only.
/// Auth screens are handled separately by AuthFlowScreen.
GoRouter buildRouter() => GoRouter(
  navigatorKey: _rootNavigatorKey,
  initialLocation: '/',
  routes: [
    // ── Main App Shell ──
    ShellRoute(
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

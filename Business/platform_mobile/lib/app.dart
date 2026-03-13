import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:platform_mobile/config/theme/app_theme.dart';
import 'package:platform_mobile/config/routes/app_router.dart';
import 'package:platform_mobile/core/di/service_locator.dart';
import 'package:platform_mobile/features/auth/bloc/auth_bloc.dart';
import 'package:platform_mobile/features/auth/screens/auth_flow_screen.dart';
import 'package:platform_mobile/features/profile/screens/setup_profile_screen.dart';

class PlatformApp extends StatefulWidget {
  const PlatformApp({super.key});

  @override
  State<PlatformApp> createState() => _PlatformAppState();
}

class _PlatformAppState extends State<PlatformApp> {
  late final AuthBloc _authBloc;
  late final GoRouter _router;

  @override
  void initState() {
    super.initState();
    _authBloc = sl<AuthBloc>()..add(AuthCheckRequested());
    _router = buildRouter();
  }

  @override
  Widget build(BuildContext context) {
    return BlocProvider.value(
      value: _authBloc,
      child: BlocBuilder<AuthBloc, AuthState>(
        buildWhen: (prev, curr) =>
            curr is AuthAuthenticated ||
            curr is AuthUnauthenticated ||
            curr is AuthNeedsProfile,
        builder: (context, state) {
          // Gate pattern: completely separate widget trees per auth state.
          // GoRouter is ONLY used for the authenticated app.
          // Auth screens use simple local state — no route transitions
          // to cause InheritedWidget assertion errors.
          if (state is AuthAuthenticated) {
            return MaterialApp.router(
              key: const ValueKey('authenticated'),
              title: 'Huduma Platform',
              debugShowCheckedModeBanner: false,
              theme: AppTheme.light,
              darkTheme: AppTheme.dark,
              themeMode: ThemeMode.light,
              routerConfig: _router,
            );
          }

          if (state is AuthNeedsProfile) {
            return MaterialApp(
              key: const ValueKey('profile-setup'),
              title: 'Huduma Platform',
              debugShowCheckedModeBanner: false,
              theme: AppTheme.light,
              darkTheme: AppTheme.dark,
              themeMode: ThemeMode.light,
              home: const SetupProfileScreen(),
            );
          }

          // AuthUnauthenticated, AuthInitial, AuthOtpSent, AuthLoading, AuthError
          return MaterialApp(
            key: const ValueKey('auth'),
            title: 'Huduma Platform',
            debugShowCheckedModeBanner: false,
            theme: AppTheme.light,
            darkTheme: AppTheme.dark,
            themeMode: ThemeMode.light,
            home: const AuthFlowScreen(),
          );
        },
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:platform_mobile/config/theme/app_theme.dart';
import 'package:platform_mobile/config/routes/app_router.dart';
import 'package:platform_mobile/core/di/service_locator.dart';
import 'package:platform_mobile/features/auth/bloc/auth_bloc.dart';

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
    _router = buildRouter(_authBloc);
  }

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider.value(value: _authBloc),
      ],
      child: MaterialApp.router(
        title: 'Huduma Platform',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.light,
        darkTheme: AppTheme.dark,
        themeMode: ThemeMode.light,
        routerConfig: _router,
      ),
    );
  }
}

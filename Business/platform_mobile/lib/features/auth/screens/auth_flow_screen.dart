import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:platform_mobile/features/auth/bloc/auth_bloc.dart';
import 'package:platform_mobile/features/auth/screens/onboarding_screen.dart';
import 'package:platform_mobile/features/auth/screens/phone_entry_screen.dart';
import 'package:platform_mobile/features/auth/screens/otp_screen.dart';

enum AuthPage { onboarding, phone, otp }

/// Manages the auth flow locally without GoRouter.
/// Switches between onboarding → phone → otp using simple setState.
class AuthFlowScreen extends StatefulWidget {
  const AuthFlowScreen({super.key});

  @override
  State<AuthFlowScreen> createState() => _AuthFlowScreenState();
}

class _AuthFlowScreenState extends State<AuthFlowScreen> {
  AuthPage _page = AuthPage.onboarding;
  String _phone = '';
  StreamSubscription<AuthState>? _authSub;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _authSub ??= context.read<AuthBloc>().stream.listen((state) {
      if (!mounted) return;
      if (state is AuthOtpSent) {
        setState(() {
          _phone = state.phone;
          _page = AuthPage.otp;
        });
      }
    });
  }

  @override
  void dispose() {
    _authSub?.cancel();
    super.dispose();
  }

  void _goToPhone() => setState(() => _page = AuthPage.phone);

  void _goBack() {
    setState(() {
      if (_page == AuthPage.otp) {
        _page = AuthPage.phone;
      } else {
        _page = AuthPage.onboarding;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 300),
      child: switch (_page) {
        AuthPage.onboarding => OnboardingScreen(
            key: const ValueKey('onboarding'),
            onGetStarted: _goToPhone,
          ),
        AuthPage.phone => PhoneEntryScreen(
            key: const ValueKey('phone'),
            onBack: _goBack,
          ),
        AuthPage.otp => OtpScreen(
            key: const ValueKey('otp'),
            phone: _phone,
            onBack: _goBack,
          ),
      },
    );
  }
}

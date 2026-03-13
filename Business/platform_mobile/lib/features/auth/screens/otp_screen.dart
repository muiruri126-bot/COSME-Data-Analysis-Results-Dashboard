import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pin_code_fields/pin_code_fields.dart';
import 'package:platform_mobile/config/theme/app_theme.dart';
import 'package:platform_mobile/features/auth/bloc/auth_bloc.dart';

class OtpScreen extends StatefulWidget {
  final String phone;
  final VoidCallback onBack;
  const OtpScreen({super.key, required this.phone, required this.onBack});

  @override
  State<OtpScreen> createState() => _OtpScreenState();
}

class _OtpScreenState extends State<OtpScreen> {
  final _otpController = TextEditingController();
  Timer? _timer;
  int _secondsRemaining = 60;
  bool _canResend = false;
  bool _isLoading = false;
  String? _errorMessage;
  StreamSubscription<AuthState>? _authSub;

  @override
  void initState() {
    super.initState();
    _startTimer();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _authSub ??= context.read<AuthBloc>().stream.listen((state) {
      if (!mounted) return;
      if (state is AuthError) {
        setState(() {
          _isLoading = false;
          _errorMessage = state.message;
        });
        _otpController.clear();
      } else if (state is AuthLoading) {
        setState(() => _isLoading = true);
      }
    });
  }

  @override
  void dispose() {
    _authSub?.cancel();
    _timer?.cancel();
    _timer = null;
    _otpController.dispose();
    super.dispose();
  }

  void _startTimer() {
    _secondsRemaining = 60;
    _canResend = false;
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (!mounted) {
        timer.cancel();
        return;
      }
      setState(() {
        if (_secondsRemaining > 0) {
          _secondsRemaining--;
        } else {
          _canResend = true;
          timer.cancel();
        }
      });
    });
  }

  void _resendOtp() {
    context.read<AuthBloc>().add(AuthOtpRequested(widget.phone));
    _startTimer();
  }

  void _verifyOtp(String otp) {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });
    context.read<AuthBloc>().add(
          AuthOtpSubmitted(phone: widget.phone, otp: otp),
        );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: widget.onBack,
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Verification Code',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 8),
              Text(
                'Enter the 6-digit code sent to\n${widget.phone}',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: AppColors.textSecondary,
                    ),
              ),
              const SizedBox(height: 40),

              // OTP Input
              PinCodeTextField(
                appContext: context,
                length: 6,
                controller: _otpController,
                keyboardType: TextInputType.number,
                animationType: AnimationType.scale,
                pinTheme: PinTheme(
                  shape: PinCodeFieldShape.box,
                  borderRadius: BorderRadius.circular(12),
                  fieldHeight: 56,
                  fieldWidth: 48,
                  activeFillColor: AppColors.surface,
                  inactiveFillColor: AppColors.surfaceVariant,
                  selectedFillColor: AppColors.surface,
                  activeColor: AppColors.primary,
                  inactiveColor: AppColors.border,
                  selectedColor: AppColors.primary,
                ),
                enableActiveFill: true,
                onCompleted: _verifyOtp,
                onChanged: (_) {},
              ),

              const SizedBox(height: 24),

              // Resend timer
              Center(
                child: _canResend
                    ? TextButton(
                        onPressed: _resendOtp,
                        child: const Text('Resend Code'),
                      )
                    : Text(
                        'Resend code in ${_secondsRemaining}s',
                        style: TextStyle(color: AppColors.textSecondary),
                      ),
              ),

              const Spacer(),

              if (_errorMessage != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: Text(
                    _errorMessage!,
                    style: TextStyle(color: AppColors.error),
                    textAlign: TextAlign.center,
                  ),
                ),

              if (_isLoading)
                const Center(child: CircularProgressIndicator()),
            ],
          ),
        ),
      ),
    );
  }
}

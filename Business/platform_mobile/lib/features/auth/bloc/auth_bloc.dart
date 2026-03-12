import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:platform_mobile/features/auth/repository/auth_repository.dart';
import 'package:platform_mobile/shared/models/user_model.dart';

// ── Events ──
abstract class AuthEvent extends Equatable {
  @override
  List<Object?> get props => [];
}

class AuthCheckRequested extends AuthEvent {}

class AuthOtpRequested extends AuthEvent {
  final String phone;
  AuthOtpRequested(this.phone);
  @override
  List<Object?> get props => [phone];
}

class AuthOtpSubmitted extends AuthEvent {
  final String phone;
  final String otp;
  AuthOtpSubmitted({required this.phone, required this.otp});
  @override
  List<Object?> get props => [phone, otp];
}

class AuthLogoutRequested extends AuthEvent {}

// ── States ──
abstract class AuthState extends Equatable {
  @override
  List<Object?> get props => [];
}

class AuthInitial extends AuthState {}

class AuthLoading extends AuthState {}

class AuthOtpSent extends AuthState {
  final String phone;
  AuthOtpSent(this.phone);
  @override
  List<Object?> get props => [phone];
}

class AuthAuthenticated extends AuthState {
  final User user;
  AuthAuthenticated(this.user);
  @override
  List<Object?> get props => [user];
}

class AuthNeedsProfile extends AuthState {
  final User user;
  AuthNeedsProfile(this.user);
  @override
  List<Object?> get props => [user];
}

class AuthUnauthenticated extends AuthState {}

class AuthError extends AuthState {
  final String message;
  AuthError(this.message);
  @override
  List<Object?> get props => [message];
}

// ── BLoC ──
class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AuthRepository _repository;

  AuthBloc(this._repository) : super(AuthInitial()) {
    on<AuthCheckRequested>(_onCheckRequested);
    on<AuthOtpRequested>(_onOtpRequested);
    on<AuthOtpSubmitted>(_onOtpSubmitted);
    on<AuthLogoutRequested>(_onLogoutRequested);
  }

  Future<void> _onCheckRequested(
    AuthCheckRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    try {
      final user = await _repository.getCurrentUser();
      if (user == null) {
        emit(AuthUnauthenticated());
      } else if (user.status == 'pending_profile' || !user.hasProfile) {
        emit(AuthNeedsProfile(user));
      } else {
        emit(AuthAuthenticated(user));
      }
    } catch (_) {
      emit(AuthUnauthenticated());
    }
  }

  Future<void> _onOtpRequested(
    AuthOtpRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    try {
      await _repository.requestOtp(event.phone);
      emit(AuthOtpSent(event.phone));
    } catch (e) {
      emit(AuthError(e.toString()));
    }
  }

  Future<void> _onOtpSubmitted(
    AuthOtpSubmitted event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    try {
      final user = await _repository.verifyOtp(event.phone, event.otp);
      if (user.status == 'pending_profile' || !user.hasProfile) {
        emit(AuthNeedsProfile(user));
      } else {
        emit(AuthAuthenticated(user));
      }
    } catch (e) {
      emit(AuthError(e.toString()));
    }
  }

  Future<void> _onLogoutRequested(
    AuthLogoutRequested event,
    Emitter<AuthState> emit,
  ) async {
    await _repository.logout();
    emit(AuthUnauthenticated());
  }
}

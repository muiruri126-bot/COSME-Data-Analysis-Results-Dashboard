import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:platform_mobile/features/profile/repository/profile_repository.dart';
import 'package:platform_mobile/shared/models/user_model.dart';

// ── Events ──
abstract class ProfileEvent extends Equatable {
  @override
  List<Object?> get props => [];
}

class LoadProfile extends ProfileEvent {}

class CreateProfile extends ProfileEvent {
  final Map<String, dynamic> data;
  CreateProfile(this.data);
  @override
  List<Object?> get props => [data];
}

class UpdateProfile extends ProfileEvent {
  final Map<String, dynamic> data;
  UpdateProfile(this.data);
  @override
  List<Object?> get props => [data];
}

class LoadPublicProfile extends ProfileEvent {
  final String userId;
  LoadPublicProfile(this.userId);
  @override
  List<Object?> get props => [userId];
}

// ── States ──
abstract class ProfileState extends Equatable {
  @override
  List<Object?> get props => [];
}

class ProfileInitial extends ProfileState {}

class ProfileLoading extends ProfileState {}

class ProfileLoaded extends ProfileState {
  final User user;
  ProfileLoaded(this.user);
  @override
  List<Object?> get props => [user];
}

class ProfileCreated extends ProfileState {
  final Profile profile;
  ProfileCreated(this.profile);
  @override
  List<Object?> get props => [profile];
}

class ProfileUpdated extends ProfileState {
  final Profile profile;
  ProfileUpdated(this.profile);
  @override
  List<Object?> get props => [profile];
}

class PublicProfileLoaded extends ProfileState {
  final User user;
  PublicProfileLoaded(this.user);
  @override
  List<Object?> get props => [user];
}

class ProfileError extends ProfileState {
  final String message;
  ProfileError(this.message);
  @override
  List<Object?> get props => [message];
}

// ── BLoC ──
class ProfileBloc extends Bloc<ProfileEvent, ProfileState> {
  final ProfileRepository _repository;

  ProfileBloc(this._repository) : super(ProfileInitial()) {
    on<LoadProfile>(_onLoadProfile);
    on<CreateProfile>(_onCreateProfile);
    on<UpdateProfile>(_onUpdateProfile);
    on<LoadPublicProfile>(_onLoadPublicProfile);
  }

  Future<void> _onLoadProfile(
    LoadProfile event,
    Emitter<ProfileState> emit,
  ) async {
    emit(ProfileLoading());
    try {
      final user = await _repository.getMyProfile();
      emit(ProfileLoaded(user));
    } catch (e) {
      emit(ProfileError(e.toString()));
    }
  }

  Future<void> _onCreateProfile(
    CreateProfile event,
    Emitter<ProfileState> emit,
  ) async {
    emit(ProfileLoading());
    try {
      final profile = await _repository.createProfile(event.data);
      emit(ProfileCreated(profile));
    } catch (e) {
      emit(ProfileError(e.toString()));
    }
  }

  Future<void> _onUpdateProfile(
    UpdateProfile event,
    Emitter<ProfileState> emit,
  ) async {
    emit(ProfileLoading());
    try {
      final profile = await _repository.updateProfile(event.data);
      emit(ProfileUpdated(profile));
    } catch (e) {
      emit(ProfileError(e.toString()));
    }
  }

  Future<void> _onLoadPublicProfile(
    LoadPublicProfile event,
    Emitter<ProfileState> emit,
  ) async {
    emit(ProfileLoading());
    try {
      final user = await _repository.getPublicProfile(event.userId);
      emit(PublicProfileLoaded(user));
    } catch (e) {
      emit(ProfileError(e.toString()));
    }
  }
}

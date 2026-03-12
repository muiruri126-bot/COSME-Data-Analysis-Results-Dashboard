import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:platform_mobile/features/categories/repository/categories_repository.dart';
import 'package:platform_mobile/shared/models/category_model.dart';

// Events
abstract class CategoriesEvent extends Equatable {
  @override
  List<Object?> get props => [];
}

class LoadCategories extends CategoriesEvent {}

// States
abstract class CategoriesState extends Equatable {
  @override
  List<Object?> get props => [];
}

class CategoriesInitial extends CategoriesState {}
class CategoriesLoading extends CategoriesState {}

class CategoriesLoaded extends CategoriesState {
  final List<ServiceCategory> categories;
  CategoriesLoaded(this.categories);
  @override
  List<Object?> get props => [categories];

  Map<String, List<ServiceCategory>> get grouped {
    final map = <String, List<ServiceCategory>>{};
    for (final cat in categories) {
      map.putIfAbsent(cat.parentGroup, () => []).add(cat);
    }
    return map;
  }
}

class CategoriesError extends CategoriesState {
  final String message;
  CategoriesError(this.message);
  @override
  List<Object?> get props => [message];
}

// BLoC
class CategoriesBloc extends Bloc<CategoriesEvent, CategoriesState> {
  final CategoriesRepository _repository;

  CategoriesBloc(this._repository) : super(CategoriesInitial()) {
    on<LoadCategories>(_onLoad);
  }

  Future<void> _onLoad(LoadCategories event, Emitter<CategoriesState> emit) async {
    emit(CategoriesLoading());
    try {
      final categories = await _repository.getAll();
      emit(CategoriesLoaded(categories));
    } catch (e) {
      emit(CategoriesError(e.toString()));
    }
  }
}

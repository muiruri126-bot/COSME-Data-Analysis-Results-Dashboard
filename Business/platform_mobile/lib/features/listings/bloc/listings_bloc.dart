import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:platform_mobile/features/listings/repository/listings_repository.dart';
import 'package:platform_mobile/shared/models/listing_model.dart';

// Events
abstract class ListingsEvent extends Equatable {
  @override
  List<Object?> get props => [];
}

class LoadRecentListings extends ListingsEvent {}

class SearchListings extends ListingsEvent {
  final String? categorySlug;
  final String? query;
  final double? lat;
  final double? lng;
  final double? radiusKm;
  final String? county;
  final String? sortBy;
  final int page;

  SearchListings({
    this.categorySlug,
    this.query,
    this.lat,
    this.lng,
    this.radiusKm,
    this.county,
    this.sortBy,
    this.page = 1,
  });

  @override
  List<Object?> get props => [categorySlug, query, lat, lng, radiusKm, county, sortBy, page];
}

class LoadMoreListings extends ListingsEvent {}

// States
abstract class ListingsState extends Equatable {
  @override
  List<Object?> get props => [];
}

class ListingsInitial extends ListingsState {}
class ListingsLoading extends ListingsState {}

class ListingsLoaded extends ListingsState {
  final List<Listing> listings;
  final int total;
  final int currentPage;
  final int totalPages;
  final bool isLoadingMore;

  ListingsLoaded({
    required this.listings,
    required this.total,
    required this.currentPage,
    required this.totalPages,
    this.isLoadingMore = false,
  });

  bool get hasMore => currentPage < totalPages;

  @override
  List<Object?> get props => [listings, total, currentPage, totalPages, isLoadingMore];

  ListingsLoaded copyWith({
    List<Listing>? listings,
    int? total,
    int? currentPage,
    int? totalPages,
    bool? isLoadingMore,
  }) {
    return ListingsLoaded(
      listings: listings ?? this.listings,
      total: total ?? this.total,
      currentPage: currentPage ?? this.currentPage,
      totalPages: totalPages ?? this.totalPages,
      isLoadingMore: isLoadingMore ?? this.isLoadingMore,
    );
  }
}

class ListingsError extends ListingsState {
  final String message;
  ListingsError(this.message);
  @override
  List<Object?> get props => [message];
}

// BLoC
class ListingsBloc extends Bloc<ListingsEvent, ListingsState> {
  final ListingsRepository _repository;
  String? _lastCategorySlug;
  String? _lastQuery;

  ListingsBloc(this._repository) : super(ListingsInitial()) {
    on<LoadRecentListings>(_onLoadRecent);
    on<SearchListings>(_onSearch);
    on<LoadMoreListings>(_onLoadMore);
  }

  Future<void> _onLoadRecent(LoadRecentListings event, Emitter<ListingsState> emit) async {
    emit(ListingsLoading());
    try {
      final result = await _repository.search(sortBy: 'recent', limit: 20);
      emit(ListingsLoaded(
        listings: result['listings'] as List<Listing>,
        total: result['total'] as int,
        currentPage: result['page'] as int,
        totalPages: result['totalPages'] as int,
      ));
    } catch (e) {
      emit(ListingsError(e.toString()));
    }
  }

  Future<void> _onSearch(SearchListings event, Emitter<ListingsState> emit) async {
    emit(ListingsLoading());
    _lastCategorySlug = event.categorySlug;
    _lastQuery = event.query;
    try {
      final result = await _repository.search(
        categorySlug: event.categorySlug,
        query: event.query,
        lat: event.lat,
        lng: event.lng,
        radiusKm: event.radiusKm,
        county: event.county,
        sortBy: event.sortBy,
        page: event.page,
      );
      emit(ListingsLoaded(
        listings: result['listings'] as List<Listing>,
        total: result['total'] as int,
        currentPage: result['page'] as int,
        totalPages: result['totalPages'] as int,
      ));
    } catch (e) {
      emit(ListingsError(e.toString()));
    }
  }

  Future<void> _onLoadMore(LoadMoreListings event, Emitter<ListingsState> emit) async {
    final currentState = state;
    if (currentState is! ListingsLoaded || !currentState.hasMore || currentState.isLoadingMore) {
      return;
    }

    emit(currentState.copyWith(isLoadingMore: true));
    try {
      final result = await _repository.search(
        categorySlug: _lastCategorySlug,
        query: _lastQuery,
        page: currentState.currentPage + 1,
      );
      final newListings = result['listings'] as List<Listing>;
      emit(ListingsLoaded(
        listings: [...currentState.listings, ...newListings],
        total: result['total'] as int,
        currentPage: result['page'] as int,
        totalPages: result['totalPages'] as int,
      ));
    } catch (e) {
      emit(currentState.copyWith(isLoadingMore: false));
    }
  }
}

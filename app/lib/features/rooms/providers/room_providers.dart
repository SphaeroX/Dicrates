import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client_provider.dart';
import '../../questions/data/question.dart';
import '../data/room.dart';

/// The caller's rooms; `ref.invalidate(roomsProvider)` reloads.
final roomsProvider = FutureProvider.autoDispose<List<Room>>(
  (ref) => ref.watch(apiClientProvider).listRooms(),
  retry: (retryCount, error) => null,
);

final roomProvider = FutureProvider.autoDispose.family<Room, String>(
  (ref, roomId) => ref.watch(apiClientProvider).getRoom(roomId),
  retry: (retryCount, error) => null,
);

/// Approved questions in a language, optionally of one topic area.
final questionsProvider = FutureProvider.autoDispose
    .family<List<Question>, ({String language, String? topicArea})>(
      (ref, filter) => ref
          .watch(apiClientProvider)
          .listQuestions(
            language: filter.language,
            topicArea: filter.topicArea,
          ),
      retry: (retryCount, error) => null,
    );

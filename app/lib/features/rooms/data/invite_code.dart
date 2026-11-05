/// Same alphabet as the backend (`dicrates/rooms/invite_codes.py`): no 0/O,
/// 1/I/L or 5/S.
const inviteAlphabet = 'ABCDEFGHJKMNPQRTUVWXYZ2346789';
const inviteCodeLength = 6;

/// Custom scheme registered on Android and iOS (also used for OAuth).
const appLinkScheme = 'io.github.sphaerox.dicrates';

final _separators = RegExp(r'[\s\-_]');

/// Upper-case and strip spaces/dashes; `null` if it cannot be a code.
String? normalizeInviteCode(String typed) {
  final code = typed.trim().toUpperCase().replaceAll(_separators, '');
  if (code.length != inviteCodeLength) return null;
  if (!code.split('').every(inviteAlphabet.contains)) return null;
  return code;
}

/// Invite link. The path carries the code because Flutter hands only the path
/// of a custom-scheme link to the router (App/Universal Links: Task 26).
Uri inviteLink(String code) => Uri.parse('$appLinkScheme://open/join/$code');

/// App route for an incoming link, or `null` if it is not ours.
String? routeForDeepLink(Uri uri) {
  if (uri.scheme != appLinkScheme) return null;
  final segments = uri.pathSegments;
  if (segments.length == 2 && segments.first == 'join') {
    return Uri(
      path: '/rooms/join',
      queryParameters: {'code': segments[1]},
    ).toString();
  }
  return null;
}

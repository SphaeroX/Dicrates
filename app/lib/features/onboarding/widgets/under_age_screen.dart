import 'package:flutter/material.dart';

import '../../../core/widgets/form_page.dart';
import '../../../l10n/app_localizations.dart';
import 'sign_out_action.dart';

class UnderAgeScreen extends StatelessWidget {
  const UnderAgeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return FormPage(
      title: l10n.underAgeTitle,
      children: [
        Text(
          l10n.underAgeBody,
          style: Theme.of(context).textTheme.bodyLarge,
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 24),
        const SignOutButton(),
      ],
    );
  }
}

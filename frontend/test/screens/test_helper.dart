import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart' hide FormField;
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:clakettes/l10n/app_localizations.dart';
import 'package:clakettes/services/auth_service.dart';
import 'package:clakettes/models/form_definition_model.dart';

Map<String, dynamic> _cachedStrings = {};

Map<String, dynamic> loadTestLocalizations() {
  if (_cachedStrings.isNotEmpty) return _cachedStrings;
  final file = File('assets/l10n/app_en.arb');
  final content = file.readAsStringSync();
  _cachedStrings = json.decode(content) as Map<String, dynamic>;
  return _cachedStrings;
}

class TestLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  final Map<String, dynamic> strings;
  const TestLocalizationsDelegate(this.strings);

  @override
  bool isSupported(Locale locale) => ['en'].contains(locale.languageCode);

  @override
  Future<AppLocalizations> load(Locale locale) async =>
      AppLocalizations.test(locale, strings);

  @override
  bool shouldReload(_) => false;
}

Widget wrapWithLocalization(Widget child) {
  final strings = loadTestLocalizations();
  return MaterialApp(
    localizationsDelegates: [
      TestLocalizationsDelegate(strings),
      GlobalMaterialLocalizations.delegate,
      GlobalWidgetsLocalizations.delegate,
    ],
    supportedLocales: const [Locale('en')],
    locale: const Locale('en'),
    home: Scaffold(body: child),
  );
}

Future<void> setupApiTest() async {
  SharedPreferences.setMockInitialValues({});
  final auth = AuthService();
  await auth.clear();
  SharedPreferences.setMockInitialValues({});
}

FormDefinition sampleForm({
  int id = 1,
  String title = 'Festival Registration',
  String formType = FormType.festivalRegistration,
  bool isActive = true,
  int pageCount = 1,
}) {
  return FormDefinition(
    id: id,
    title: title,
    formType: formType,
    isActive: isActive,
    isPublic: true,
    sortOrder: 0,
    pages: List.generate(pageCount, (i) => FormPage(
      id: i + 1,
      formId: id,
      title: 'Page ${i + 1}',
      sortOrder: i,
      fields: i == 0
          ? [
              FormField(
                id: 1,
                pageId: 1,
                fieldType: FormFieldType.string,
                label: 'Full Name',
                isRequired: true,
                sortOrder: 0,
              ),
              FormField(
                id: 2,
                pageId: 1,
                fieldType: FormFieldType.email,
                label: 'Email',
                isRequired: true,
                sortOrder: 1,
              ),
            ]
          : [],
    )),
  );
}

FormPage samplePage({int formId = 1, int pageId = 1}) {
  return FormPage(
    id: pageId,
    formId: formId,
    title: 'Personal Info',
    sortOrder: 0,
    fields: [
      FormField(
        id: 1,
        pageId: pageId,
        fieldType: FormFieldType.string,
        label: 'Full Name',
        isRequired: true,
        sortOrder: 0,
      ),
      FormField(
        id: 2,
        pageId: pageId,
        fieldType: FormFieldType.email,
        label: 'Email',
        isRequired: true,
        sortOrder: 1,
      ),
    ],
  );
}

FormField sampleField({int id = 1, int pageId = 1, String label = 'Full Name'}) {
  return FormField(
    id: id,
    pageId: pageId,
    fieldType: FormFieldType.string,
    label: label,
    isRequired: true,
    sortOrder: 0,
  );
}

FormResponse sampleResponse({int id = 1, int formId = 1}) {
  return FormResponse(
    id: id,
    formId: formId,
    status: SubmissionStatus.submitted,
    fieldResponses: [
      FormFieldResponse(responseId: id, fieldId: 1, value: 'John Doe'),
      FormFieldResponse(responseId: id, fieldId: 2, value: 'john@example.com'),
    ],
  );
}

/// Produces the full JSON map as returned by the API (contrast with [FormDefinition.toJson],
/// which omits server-generated fields like `id`, `form_id`, `created_at`, `updated_at`).
Map<String, dynamic> formToApiJson(FormDefinition f) => {
  'id': f.id,
  'title': f.title,
  'description': f.description,
  'form_type': f.formType,
  'festival_id': f.festivalId,
  'is_active': f.isActive,
  'is_public': f.isPublic,
  'starts_at': f.startsAt?.toIso8601String(),
  'ends_at': f.endsAt?.toIso8601String(),
  'max_submissions': f.maxSubmissions,
  'require_auth': f.requireAuth,
  'requires_approval': f.requiresApproval,
  'success_message': f.successMessage,
  'submit_button_text': f.submitButtonText,
  'created_by': f.createdBy,
  'settings': f.settings,
  'sort_order': f.sortOrder,
  'created_at': f.createdAt?.toIso8601String(),
  'updated_at': f.updatedAt?.toIso8601String(),
  'pages': f.pages.map(pageToApiJson).toList(),
};

Map<String, dynamic> pageToApiJson(FormPage p) => {
  'id': p.id,
  'form_id': p.formId,
  'title': p.title,
  'description': p.description,
  'sort_order': p.sortOrder,
  'is_repeatable': p.isRepeatable,
  'created_at': p.createdAt?.toIso8601String(),
  'updated_at': p.updatedAt?.toIso8601String(),
  'fields': p.fields.map(fieldToApiJson).toList(),
};

Map<String, dynamic> responseToApiJson(FormResponse r) => {
  'id': r.id,
  'form_id': r.formId,
  'user_id': r.userId,
  'festival_id': r.festivalId,
  'status': r.status,
  'submitted_at': r.submittedAt?.toIso8601String(),
  'reviewer_id': r.reviewerId,
  'reviewed_at': r.reviewedAt?.toIso8601String(),
  'review_notes': r.reviewNotes,
  'link_token': r.linkToken,
  'field_responses': r.fieldResponses.map(fieldResponseToApiJson).toList(),
  'created_at': r.createdAt?.toIso8601String(),
  'updated_at': r.updatedAt?.toIso8601String(),
};

Map<String, dynamic> fieldResponseToApiJson(FormFieldResponse fr) => {
  'id': fr.id,
  'response_id': fr.responseId,
  'field_id': fr.fieldId,
  'value': fr.value,
  'file_url': fr.fileUrl,
  'created_at': fr.createdAt?.toIso8601String(),
  'updated_at': fr.updatedAt?.toIso8601String(),
};

Map<String, dynamic> fieldToApiJson(FormField f) => {
  'id': f.id,
  'page_id': f.pageId,
  'field_type': f.fieldType,
  'label': f.label,
  'help_text': f.helpText,
  'placeholder': f.placeholder,
  'is_required': f.isRequired,
  'is_visible': f.isVisible,
  'is_read_only': f.isReadOnly,
  'sort_order': f.sortOrder,
  'default_value': f.defaultValue,
  'min_length': f.minLength,
  'max_length': f.maxLength,
  'min_value': f.minValue,
  'max_value': f.maxValue,
  'regex_pattern': f.regexPattern,
  'error_message': f.errorMessage,
  'allowed_values': f.allowedValues,
  'depends_on_field_id': f.dependsOnFieldId,
  'depends_on_value': f.dependsOnValue,
  'role_filter': f.roleFilter,
  'settings': f.settings,
  'width_class': f.widthClass,
  'options': f.options.map((o) => o.toJson()).toList(),
  'created_at': f.createdAt?.toIso8601String(),
  'updated_at': f.updatedAt?.toIso8601String(),
};

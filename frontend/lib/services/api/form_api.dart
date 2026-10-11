part of '../api_service.dart';

extension FormApi on ApiService {
  Future<PaginatedResult<RegistrationForm>> getRegistrationForms(int festivalId,
      {int page = 1, int size = 20}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    final data =
        await _get('/festivals/$festivalId/registration-forms/', params);
    return _paginated(data, RegistrationForm.fromJson);
  }

  Future<RegistrationForm> createRegistrationForm(
      int festivalId, RegistrationForm f) async {
    final data =
        await create('/festivals/$festivalId/registration-forms/', f.toJson());
    return RegistrationForm.fromJson(data);
  }

  Future<RegistrationForm> createRegistrationFormWithSections(
    int festivalId,
    RegistrationForm f,
    List<RegistrationFormSection> sections,
  ) async {
    final body = {
      ...f.toJson(),
      'sections': sections.map((s) => s.toJson()).toList(),
    };
    final data = await create(
        '/festivals/$festivalId/registration-forms/', body);
    return RegistrationForm.fromJson(data);
  }

  Future<RegistrationForm> getRegistrationForm(int formId) async {
    final data = await request('GET', '/registration-forms/$formId');
    return RegistrationForm.fromJson(data);
  }

  Future<RegistrationForm> updateRegistrationForm(
      int formId, Map<String, dynamic> fields) async {
    final data = await _put('/registration-forms/$formId', fields);
    return RegistrationForm.fromJson(data);
  }

  Future<void> deleteRegistrationForm(int formId) async {
    await request('DELETE', '/registration-forms/$formId');
  }

  Future<PaginatedResult<FestivalRegistration>> getFestivalRegistrations(
      int formId,
      {int page = 1,
      int size = 20,
      String? status}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (status != null) params['status'] = status;
    final data =
        await _get('/registration-forms/$formId/registrations/', params);
    return _paginated(data, FestivalRegistration.fromJson);
  }

  Future<FestivalRegistration> updateFestivalRegistration(
      int registrationId, Map<String, dynamic> fields) async {
    final data = await _put('/registrations/$registrationId', fields);
    return FestivalRegistration.fromJson(data);
  }

  Future<FestivalRegistration> markRegistrationPaid(
    int registrationId, {
    String? method,
    String? transactionId,
  }) async {
    final data = await request(
      'POST',
      '/registrations/$registrationId/payment/mark-paid',
      body: json.encode({'method': method, 'transaction_id': transactionId}),
    );
    return FestivalRegistration.fromJson(data);
  }

  Future<FestivalRegistration> markRegistrationRefunded(
      int registrationId) async {
    final data = await request(
      'POST',
      '/registrations/$registrationId/payment/mark-refunded',
    );
    return FestivalRegistration.fromJson(data);
  }

  Future<RegistrationForm> getPublicRegistrationForm(String token) async {
    final data = await request('GET', '/public/forms/$token', withAuth: false);
    return RegistrationForm.fromJson(data);
  }

  Future<FestivalRegistration> registerViaPublicLink(
    String token,
    int formId,
    List<Map<String, dynamic>> sections,
  ) async {
    final data = await request(
      'POST',
      '/public/forms/$token/register',
      body: json.encode({'form_id': formId, 'sections': sections}),
    );
    return FestivalRegistration.fromJson(data);
  }

  Future<PaginatedResult<RegistrationFormLink>> getRegistrationFormLinks(
      int formId,
      {int page = 1,
      int size = 20}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    final data = await _get('/registration-forms/$formId/links/', params);
    return _paginated(data, RegistrationFormLink.fromJson);
  }

  Future<RegistrationFormLink> createRegistrationFormLink(
      int formId, RegistrationFormLink link) async {
    final data =
        await create('/registration-forms/$formId/links/', link.toJson());
    return RegistrationFormLink.fromJson(data);
  }

  Future<void> deleteRegistrationFormLink(int linkId) async {
    await request('DELETE', '/registration-form-links/$linkId');
  }

  Future<RegistrationFormLink> regenerateFormLinkToken(int linkId) async {
    final data =
        await request('POST', '/registration-form-links/$linkId/regenerate');
    return RegistrationFormLink.fromJson(data);
  }

  Future<PaginatedResult<FormDefinition>> getForms(
      {String? formType,
      int? festivalId,
      bool? isActive,
      int page = 1,
      int size = 20}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (formType != null) params['form_type'] = formType;
    if (festivalId != null) params['festival_id'] = '$festivalId';
    if (isActive != null) params['is_active'] = '$isActive';
    final data = await _get('/forms/', params);
    return _paginated(data, FormDefinition.fromJson);
  }

  Future<FormDefinition> createForm(Map<String, dynamic> data) async {
    final result = await create('/forms/', data);
    return FormDefinition.fromJson(result);
  }

  Future<FormDefinition> getForm(int formId) async {
    final data = await request('GET', '/forms/$formId');
    return FormDefinition.fromJson(data);
  }

  Future<FormDefinition> updateForm(
      int formId, Map<String, dynamic> fields) async {
    final data = await _put('/forms/$formId', fields);
    return FormDefinition.fromJson(data);
  }

  Future<void> deleteForm(int formId) async {
    await request('DELETE', '/forms/$formId');
  }

  Future<FormPage> createPage(int formId, Map<String, dynamic> data) async {
    final result = await create('/forms/$formId/pages/', data);
    return FormPage.fromJson(result);
  }

  Future<FormPage> updatePage(
      int formId, int pageId, Map<String, dynamic> fields) async {
    final data = await _put('/forms/$formId/pages/$pageId', fields);
    return FormPage.fromJson(data);
  }

  Future<void> deletePage(int formId, int pageId) async {
    await request('DELETE', '/forms/$formId/pages/$pageId');
  }

  Future<FormField> createField(
      int formId, int pageId, Map<String, dynamic> data) async {
    final result = await create('/forms/$formId/pages/$pageId/fields/', data);
    return FormField.fromJson(result);
  }

  Future<FormField> updateField(
      int formId, int fieldId, Map<String, dynamic> fields) async {
    final data = await _put('/forms/$formId/fields/$fieldId', fields);
    return FormField.fromJson(data);
  }

  Future<void> deleteField(int formId, int fieldId) async {
    await request('DELETE', '/forms/$formId/fields/$fieldId');
  }

  Future<List<FormLink>> getFormLinks(int formId,
      {int page = 1, int size = 20, bool? isActive}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (isActive != null) params['is_active'] = '$isActive';
    final data = await _get('/forms/$formId/links/', params);
    if (data is List) return data.map((j) => FormLink.fromJson(j)).toList();
    return _extractItems(data).map((j) => FormLink.fromJson(j)).toList();
  }

  Future<FormLink> createFormLink(int formId, Map<String, dynamic> data) async {
    final result = await create('/forms/$formId/links/', data);
    return FormLink.fromJson(result);
  }

  Future<void> deleteFormLink(int formId, int linkId) async {
    await request('DELETE', '/forms/$formId/links/$linkId');
  }

  Future<FormDefinition> getPublicForm(String token) async {
    final data = await request('GET', '/forms/public/$token', withAuth: false);
    return FormDefinition.fromJson(data);
  }

  Future<FormResponse> submitPublicResponse(
      String token, Map<String, dynamic> data) async {
    final result =
        await create('/forms/public/$token/submit', {'field_values': data});
    return FormResponse.fromJson(result);
  }

  Future<String> getFormResponsesCsvUrl(int formId) async {
    return '$rootUrl/api/forms/$formId/responses/export/csv';
  }

  Future<FormDefinition> cloneForm(int formId, {String? title}) async {
    final data = await request('POST', '/forms/$formId/clone',
        body: jsonEncode(title != null ? {'title': title} : {}));
    return FormDefinition.fromJson(data as Map<String, dynamic>);
  }

  Future<PaginatedResult<FormResponse>> getFormResponses(int formId,
      {int page = 1, int size = 20, String? status}) async {
    final params = <String, String>{'page': '$page', 'size': '$size'};
    if (status != null) params['status'] = status;
    final data = await _get('/forms/$formId/responses/', params);
    return _paginated(data, FormResponse.fromJson);
  }

  Future<FormResponse> updateFormResponse(
      int responseId, Map<String, dynamic> fields) async {
    final data = await _put('/forms/responses/$responseId', fields);
    return FormResponse.fromJson(data);
  }

  Future<FormResponse> approveResponse(int responseId) async {
    final data = await request('POST', '/forms/responses/$responseId/approve');
    return FormResponse.fromJson(data);
  }

  Future<FormResponse> rejectResponse(int responseId, {String? reason}) async {
    final path = reason != null
        ? '/forms/responses/$responseId/reject?reason=${Uri.encodeComponent(reason)}'
        : '/forms/responses/$responseId/reject';
    final data = await request('POST', path);
    return FormResponse.fromJson(data);
  }
}

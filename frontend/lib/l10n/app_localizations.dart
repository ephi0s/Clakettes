import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show rootBundle;

/// Clase de localización manual que carga archivos ARB JSON en runtime.
///
/// Soporta 9 locales (en, es, fr, de, it, ca, eu, gl, oc) con recurso
/// automático al inglés cuando el idioma del dispositivo no está disponible.
class AppLocalizations {
  final Locale locale;
  late Map<String, dynamic> _localizedStrings;

  AppLocalizations(this.locale);

  /// Construye una instancia de test con cadenas predefinidas.
  AppLocalizations.test(this.locale, Map<String, dynamic> strings)
      : _localizedStrings = strings;

  /// Obtiene la instancia de [AppLocalizations] del árbol de widgets.
  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  /// Delegate de localización usado por MaterialApp.
  static const LocalizationsDelegate<AppLocalizations> delegate = _AppLocalizationsDelegate();

  /// Carga el archivo ARB del locale actual (recurre a `app_en.arb`).
  Future<bool> load() async {
    String jsonString;
    try {
      jsonString = await rootBundle.loadString('assets/l10n/app_${locale.languageCode}.arb');
    } catch (e) {
      jsonString = await rootBundle.loadString('assets/l10n/app_en.arb');
    }
    Map<String, dynamic> jsonMap = json.decode(jsonString);
    _localizedStrings = jsonMap;
    return true;
  }

  /// Devuelve la cadena traducida para [key], interpolando opcionalmente los
  /// valores placeholder de [args] (p. ej. `{min}`).
  String translate(String key, {Map<String, dynamic>? args}) {
    String value = _localizedStrings[key] ?? key;
    if (args != null) {
      args.forEach((argKey, argValue) {
        value = value.replaceAll('{$argKey}', argValue.toString());
      });
    }
    return value;
  }

  // Common translations
  String get appTitle => translate('appTitle');
  String get welcome => translate('welcome');
  String get subtitle => translate('subtitle');
  String get festivals => translate('festivals');
  String get users => translate('users');
  String get shortFilms => translate('shortFilms');
  String get chat => translate('chat');
  String get locations => translate('locations');
  String get profile => translate('profile');
  String get userProfile => translate('userProfile');
  String get festivalProfile => translate('festivalProfile');
  String get createUser => translate('createUser');
  String get edit => translate('edit');
  String get save => translate('save');
  String get loading => translate('loading');
  String get noUsers => translate('noUsers');
  String get noFestivals => translate('noFestivals');
  String get noShortFilms => translate('noShortFilms');
  String get noLocations => translate('noLocations');
  String get username => translate('username');
  String get email => translate('email');
  String get fullName => translate('fullName');
  String get role => translate('role');
  String get bio => translate('bio');
  String get password => translate('password');
  String get publicProfile => translate('publicProfile');
  String get active => translate('active');
  String get inactive => translate('inactive');
  String get public => translate('public');
  String get private => translate('private');
  String get description => translate('description');
  String get location => translate('location');
  String get website => translate('website');
  String get coordinates => translate('coordinates');
  String get latitude => translate('latitude');
  String get longitude => translate('longitude');
  String get duration => translate('duration');
  String get minutes => translate('minutes');
  String get sendMessage => translate('sendMessage');
  String get writeMessage => translate('writeMessage');
  String get welcomeChat => translate('welcomeChat');
  String get refresh => translate('refresh');
  String get attachFile => translate('attachFile');
  String get groupChats => translate('groupChats');
  String get add => translate('add');
  String get addLocation => translate('addLocation');
  String get invalidValue => translate('invalidValue');
  String get cancel => translate('cancel');
  String get accept => translate('accept');
  String get error => translate('error');
  String get success => translate('success');
  String get userCreated => translate('userCreated');
  String get profileUpdated => translate('profileUpdated');
  String get confirmDelete => translate('confirmDelete');
  String get delete => translate('delete');
  String get search => translate('search');
  String get filter => translate('filter');
  String get close => translate('close');
  String get openMap => translate('openMap');
  String get viewProfile => translate('viewProfile');
  String get dashboard => translate('dashboard');
  String get totalFestivals => translate('totalFestivals');
  String get totalUsers => translate('totalUsers');
  String get totalShortFilms => translate('totalShortFilms');
  String get featuredFestivals => translate('featuredFestivals');
  String get quickActions => translate('quickActions');
  String get viewAll => translate('viewAll');
  String get welcomeBack => translate('welcomeBack');
  String get optional => translate('optional');
  String get maxCharacters => translate('maxCharacters');
  String get noRole => translate('noRole');
  String get navigateTo => translate('navigateTo');
  String get backendUrl => translate('backendUrl');
  String get backendUrlHint => translate('backendUrlHint');
  String get testConnection => translate('testConnection');
  String get connectionSuccess => translate('connectionSuccess');
  String get connectionFailed => translate('connectionFailed');
  String get configureBackend => translate('configureBackend');
  String get saveAndContinue => translate('saveAndContinue');
  String get loadError => translate('loadError');
  String get login => translate('login');
  String get logout => translate('logout');
  String get loginTitle => translate('loginTitle');
  String get loginError => translate('loginError');
  String get tokenExpired => translate('tokenExpired');
  String get createFestival => translate('createFestival');
  String get createShortFilm => translate('createShortFilm');
  String get editFestival => translate('editFestival');
  String get editShortFilm => translate('editShortFilm');
  String get shortFilmProfile => translate('shortFilmProfile');
  String get noMessages => translate('noMessages');
  String get loginSuccess => translate('loginSuccess');
  String get confirmLogout => translate('confirmLogout');
  String get name => translate('name');
  String get tags => translate('tags');
  String get videoUrl => translate('videoUrl');
  String get thumbnailUrl => translate('thumbnailUrl');
  String get logoUrl => translate('logoUrl');
  String get createdAt => translate('createdAt');
  String get admin => translate('admin');
  String get adminPanel => translate('adminPanel');
  String get databaseStats => translate('databaseStats');
  String get tableCounts => translate('tableCounts');
  String get totalMessages => translate('totalMessages');
  String get activeUsers => translate('activeUsers');
  String get activeFestivals => translate('activeFestivals');
  String get resetDatabase => translate('resetDatabase');
  String get resetDatabaseConfirm => translate('resetDatabaseConfirm');
  String get databaseReset => translate('databaseReset');
  String get devMode => translate('devMode');
  String get privacySettings => translate('privacySettings');
  String get visibleToAll => translate('visibleToAll');
  String get onlyVisibleToYou => translate('onlyVisibleToYou');
  String get showEmail => translate('showEmail');
  String get showBio => translate('showBio');
  String get showLocation => translate('showLocation');
  String get loginRequired => translate('loginRequired');
  String get notifications => translate('notifications');
  String get noNotifications => translate('noNotifications');
  String get noNotificationsSubtitle => translate('noNotificationsSubtitle');
  String get markAllAsRead => translate('markAllAsRead');
  String get offline => translate('offline');
  String get messageQueuedOffline => translate('messageQueuedOffline');
  String get offlineDescription => translate('offlineDescription');
  String get online => translate('online');
  String get syncPending => translate('syncPending');
  String get syncNow => translate('syncNow');
  String get syncLater => translate('syncLater');
  String get syncing => translate('syncing');
  String get syncSuccess => translate('syncSuccess');
  String get syncFailed => translate('syncFailed');
  String get cacheIntegrityError => translate('cacheIntegrityError');
  String get pendingChanges => translate('pendingChanges');
  String get reconnecting => translate('reconnecting');
  String get language => translate('language');
  String get cacheData => translate('cacheData');
  String get camera => translate('camera');
  String get gallery => translate('gallery');
  String get imageSendError => translate('imageSendError');
  String get locationFetchError => translate('locationFetchError');
  String get image => translate('image');
  String get vcard => translate('vcard');
  String get ical => translate('ical');
  String get privateRoom => translate('privateRoom');
  String get communityChannel => translate('communityChannel');
  String get openInMaps => translate('openInMaps');
  String get viewOnMap => translate('viewOnMap');
  String get emoji => translate('emoji');
  String get me => translate('me');
  String get sendContact => translate('sendContact');
  String get phone => translate('phone');
  String get send => translate('send');
  String get sendEvent => translate('sendEvent');
  String get title => translate('title');
  String get startDateHint => translate('startDateHint');
  String get endDateHint => translate('endDateHint');
  String get current => translate('current');
  String get sessionRevoked => translate('sessionRevoked');
  String get failedRevokeSession => translate('failedRevokeSession');
  String get revokeAllSessionsTitle => translate('revokeAllSessionsTitle');
  String get revokeAllConfirm => translate('revokeAllConfirm');
  String get allSessionsRevoked => translate('allSessionsRevoked');
  String get failedRevokeSessions => translate('failedRevokeSessions');
  String get activeSessions => translate('activeSessions');
  String get revokeAll => translate('revokeAll');
  String get noActiveSessions => translate('noActiveSessions');
  String get timeJustNow => translate('timeJustNow');
  String timeMinutesAgo(int count) => translate('timeMinutesAgo', args: {'count': count.toString()});
  String timeHoursAgo(int count) => translate('timeHoursAgo', args: {'count': count.toString()});
  String timeDaysAgo(int count) => translate('timeDaysAgo', args: {'count': count.toString()});
  String get unknownDevice => translate('unknownDevice');
  String lastUsed(String time, String ip) => translate('lastUsed', args: {'time': time, 'ip': ip});
  String get revokeSession => translate('revokeSession');
  String get manageSessions => translate('manageSessions');
  String get userAliases => translate('userAliases');
  String get manageAliases => translate('manageAliases');
  String get sessionsDialogInfo => translate('sessionsDialogInfo');
  String get aliasesDialogInfo => translate('aliasesDialogInfo');
  String get createAlias => translate('createAlias');
  String get editAlias => translate('editAlias');
  String get deleteAlias => translate('deleteAlias');
  String get aliasName => translate('aliasName');
  String get aliasContext => translate('aliasContext');
  String get aliasPublic => translate('aliasPublic');
  String get aliasVisibility => translate('aliasVisibility');
  String get noAliases => translate('noAliases');
  String get aliasCreated => translate('aliasCreated');
  String get aliasUpdated => translate('aliasUpdated');
  String get aliasDeleted => translate('aliasDeleted');
  String get confirmDeleteAlias => translate('confirmDeleteAlias');
  String get ok => translate('ok');
  String get openInOpenStreetMap => translate('openInOpenStreetMap');
  String get listView => translate('listView');
  String get mapView => translate('mapView');
  String get menu => translate('menu');
  String get management => translate('management');
  String get roleGroupsManagement => translate('roleGroupsManagement');
  String get roleGroupsDescription => translate('roleGroupsDescription');
  String get memberDirectory => translate('memberDirectory');
  String get memberDirectoryDescription => translate('memberDirectoryDescription');
  String get typeYesToConfirm => translate('typeYesToConfirm');
  String get createChannel => translate('createChannel');
  String get createFirstChannel => translate('createFirstChannel');
  String get channelLabel => translate('channelLabel');
  String get channelName => translate('channelName');
  String get channelPrivate => translate('channelPrivate');
  String get channelCommunity => translate('channelCommunity');
  String get channelDescriptionOptional => translate('channelDescriptionOptional');
  String get channelType => translate('channelType');
  String get maxMembers => translate('maxMembers');
  String get channelRequired => translate('channelRequired');
  String get errorFormat => translate('errorFormat');
  String errorFormatWith(String error) => translate('errorFormat', args: {'error': error});
  String get registrationForms => translate('registrationForms');
  String get events => translate('events');
  String get committees => translate('committees');
  String get awards => translate('awards');
  String get members => translate('members');
  String get create => translate('create');
  String get all => translate('all');
  String get pending => translate('pending');
  String get approved => translate('approved');
  String get rejected => translate('rejected');
  String get newRegistrationForm => translate('newRegistrationForm');
  String get newEvent => translate('newEvent');
  String get newCommittee => translate('newCommittee');
  String get newAward => translate('newAward');
  String get newRoleGroup => translate('newRoleGroup');
  String get noRegistrationForms => translate('noRegistrationForms');
  String get noEvents => translate('noEvents');
  String get noCommittees => translate('noCommittees');
  String get noAwards => translate('noAwards');
  String get noMembersFound => translate('noMembersFound');
  String get createOneToStart => translate('createOneToStart');
  String get createEventSubtitle => translate('createEventSubtitle');
  String get createCommitteeSubtitle => translate('createCommitteeSubtitle');
  String get createAwardSubtitle => translate('createAwardSubtitle');
  String get open => translate('open');
  String get closed => translate('closed');
  String get winner => translate('winner');
  String get nominee => translate('nominee');
  String get hidden => translate('hidden');
  String get verified => translate('verified');
  String get unverified => translate('unverified');
  String get viewRegistrations => translate('viewRegistrations');
  String get manageMembers => translate('manageMembers');
  String get verify => translate('verify');
  String get createForm => translate('createForm');
  String get createEvent => translate('createEvent');
  String get createCommittee => translate('createCommittee');
  String get createAward => translate('createAward');
  String get createRoleGroup => translate('createRoleGroup');
  String get deleteForm => translate('deleteForm');
  String get deleteEvent => translate('deleteEvent');
  String get deleteCommittee => translate('deleteCommittee');
  String get deleteAward => translate('deleteAward');
  String get deleteRoleGroup => translate('deleteRoleGroup');
  String get titleRequired => translate('titleRequired');
  String get nameRequired => translate('nameRequired');
  String get awardNameRequired => translate('awardNameRequired');
  String get displayNameRequired => translate('displayNameRequired');
  String get tryDifferentSearch => translate('tryDifferentSearch');
  String get capacity => translate('capacity');
  String get category => translate('category');
  String get formTitle => translate('formTitle');
  String get optionalDescription => translate('optionalDescription');
  String get eventTitle => translate('eventTitle');
  String get venueOrLink => translate('venueOrLink');
  String get maxAttendees => translate('maxAttendees');
  String get committeeName => translate('committeeName');
  String get awardName => translate('awardName');
  String get groupName => translate('groupName');
  String get displayName => translate('displayName');
  String get images => translate('images');
  String get noImages => translate('noImages');
  String get addImage => translate('addImage');
  String roleGroupLabel(String name, String description) => translate('roleGroupLabel', args: {'name': name, 'description': description});

  String sectionCount(int count) => translate('sectionCount', args: {'count': count.toString()});
  String memberCount(int count) => translate('memberCount', args: {'count': count.toString()});
  String roleGroupCount(int count) => translate('roleGroupCount', args: {'count': count.toString()});
  String capacityFormat(int? count) => translate('capacityFormat', args: {'count': count?.toString() ?? '∞'});
  String registrationFormCount(int count) => translate('registrationFormCount', args: {'count': count.toString()});
  String userDefaultName(int id) => translate('userDefaultName', args: {'id': id.toString()});
  String deleteFormMessage(String title) => translate('deleteFormMessage', args: {'title': title});
  String deleteEntityMessage(String name) => translate('deleteEntityMessage', args: {'name': name});
  String deleteRoleGroupMessage(String name) => translate('deleteRoleGroupMessage', args: {'name': name});

  // Registration form editor
  String get editForm => translate('editForm');
  String get details => translate('details');
  String get seats => translate('seats');
  String get retry => translate('retry');
  String get generate => translate('generate');
  String get generateSeats => translate('generateSeats');
  String get clear => translate('clear');
  String get sectionsTab => translate('sectionsTab');
  String get linksTab => translate('linksTab');
  String get registrationsTab => translate('registrationsTab');
  String get saved => translate('saved');
  String get formActive => translate('formActive');
  String get formActiveHint => translate('formActiveHint');
  String get requireExisting => translate('requireExisting');
  String get requireExistingHint => translate('requireExistingHint');
  String get allowRoleSelect => translate('allowRoleSelect');
  String get allowRoleSelectHint => translate('allowRoleSelectHint');
  String get allowTagSelect => translate('allowTagSelect');
  String get allowTagSelectHint => translate('allowTagSelectHint');
  String get maxRegistrations => translate('maxRegistrations');
  String get maxRegistrationsHint => translate('maxRegistrationsHint');
  String get startsAt => translate('startsAt');
  String get endsAt => translate('endsAt');
  String get saveChanges => translate('saveChanges');
  String get noSections => translate('noSections');
  String get noSectionsHint => translate('noSectionsHint');
  String get requiredLabel => translate('requiredLabel');
  String get multipleRoles => translate('multipleRoles');
  String get singleRole => translate('singleRole');
  String get linkCreated => translate('linkCreated');
  String get deleteLink => translate('deleteLink');
  String get deleteLinkMessage => translate('deleteLinkMessage');
  String get tokenRegenerated => translate('tokenRegenerated');
  String get createLink => translate('createLink');
  String get noLinks => translate('noLinks');
  String get noLinksHint => translate('noLinksHint');
  String get uses => translate('uses');
  String get unique => translate('unique');
  String get shared => translate('shared');
  String get regenerateToken => translate('regenerateToken');
  String get noRegistrations => translate('noRegistrations');
  String get noRegistrationsHint => translate('noRegistrationsHint');
  String get confirmMarkPaid => translate('confirmMarkPaid');
  String get currency => translate('currency');
  String get markPaid => translate('markPaid');
  String get markRefunded => translate('markRefunded');
  String payInstructions(String fee) => translate('payInstructions', args: {'fee': fee});
  String get paymentMethod => translate('paymentMethod');
  String get paymentPaid => translate('paymentPaid');
  String get paymentPending => translate('paymentPending');
  String get paymentRefunded => translate('paymentRefunded');
  String get paymentRequiredForApproval => translate('paymentRequiredForApproval');
  String get paymentStatus => translate('paymentStatus');
  String get paymentUnpaid => translate('paymentUnpaid');
  String get registrationFee => translate('registrationFee');
  String get registrationFeeHint => translate('registrationFeeHint');
  String get transactionId => translate('transactionId');

  // Exports
  String get exportLabel => translate('export');
  String get exportCsv => translate('exportCsv');
  String get exportPdf => translate('exportPdf');
  String get exportCalendar => translate('exportCalendar');
  String get exportAttendees => translate('exportAttendees');
  String get exporting => translate('exporting');
  String get exportSuccess => translate('exportSuccess');
  String get exportError => translate('exportError');
  String get exportFailed => translate('exportFailed');

  // Shared agenda
  String get agenda => translate('agenda');
  String get allFestivals => translate('allFestivals');
  String get restrictedVisibility => translate('restrictedVisibility');
  String get screenings => translate('screenings');
  String get byVenue => translate('byVenue');

  // Agenda settings (global admin)
  String get calendarSettings => translate('calendarSettings');
  String get calendarSettingsDescription => translate('calendarSettingsDescription');
  String get enableAgenda => translate('enableAgenda');
  String get agendaDisabled => translate('agendaDisabled');
  String get visibleFestivals => translate('visibleFestivals');
  String get showInAgenda => translate('showInAgenda');
  String get hideFromAgenda => translate('hideFromAgenda');
  String get settingsSaved => translate('settingsSaved');

  // CalDAV subscription
  String get davSubscriptionTitle => translate('davSubscriptionTitle');
  String get davSubscriptionIntro => translate('davSubscriptionIntro');
  String get davTokenActive => translate('davTokenActive');
  String get davTokenInactive => translate('davTokenInactive');
  String get davGenerateToken => translate('davGenerateToken');
  String get davRegenerateToken => translate('davRegenerateToken');
  String get davRevokeToken => translate('davRevokeToken');
  String get davRevokeTokenConfirm => translate('davRevokeTokenConfirm');
  String get davTokenWarning => translate('davTokenWarning');
  String get davCollection => translate('davCollection');
  String get davNoCollections => translate('davNoCollections');
  String get davCalDavUrl => translate('davCalDavUrl');
  String get davWebCalUrl => translate('davWebCalUrl');
  String get davCopyUrl => translate('davCopyUrl');
  String get davUrlCopied => translate('davUrlCopied');
  String get davTokenRevoked => translate('davTokenRevoked');
  String get davTokenGenerated => translate('davTokenGenerated');

  // Event visibility
  String get visibility => translate('visibility');
  String get visibilityDescription => translate('visibilityDescription');
  String get visibilityPublic => translate('visibilityPublic');
  String get visibilityFestivalMembers => translate('visibilityFestivalMembers');
  String get visibilityRoles => translate('visibilityRoles');
  String get visibilityAttendeesOnly => translate('visibilityAttendeesOnly');
  String get selectRoles => translate('selectRoles');
  String get noRolesSelected => translate('noRolesSelected');
  String get restrictedEvent => translate('restrictedEvent');

  // Form editor
  String get forms => translate('forms');
  String get formDefinitions => translate('formDefinitions');
  String get formType => translate('formType');
  String get newForm => translate('newForm');
  String get noForms => translate('noForms');
  String get noFormsHint => translate('noFormsHint');
  String get pagesTab => translate('pagesTab');
  String get responsesTab => translate('responsesTab');
  String get addPage => translate('addPage');
  String get addField => translate('addField');
  String get fieldType => translate('fieldType');
  String get isRequired => translate('isRequired');
  String get saveForm => translate('saveForm');
  String get deleteField => translate('deleteField');
  String get deletePage => translate('deletePage');
  String deleteFieldMessage(String msg) => translate('deleteFieldMessage', args: {'msg': msg});
  String fieldsCount(int count) => translate('fieldsCount', args: {'count': count.toString()});
  String get editField => translate('editField');
  String get fieldLabel => translate('fieldLabel');
  String get helpText => translate('helpText');
  String get placeholder => translate('placeholder');
  String get regexPattern => translate('regexPattern');
  String get optionsLabel => translate('optionsLabel');
  String get addOption => translate('addOption');
  String get optionLabel => translate('optionLabel');
  String get optionValue => translate('optionValue');
  String get submitForm => translate('submitForm');
  String get formSubmitted => translate('formSubmitted');
  String get responseApproved => translate('responseApproved');
  String get responseRejected => translate('responseRejected');
  String get approve => translate('approve');
  String get reject => translate('reject');
  String get rejectReason => translate('rejectReason');
  String get reviewNotes => translate('reviewNotes');
  String get isPublic => translate('isPublic');
  String get requireAuth => translate('requireAuth');
  String get requiresApproval => translate('requiresApproval');
  String get maxSubmissions => translate('maxSubmissions');
  String get submitButtonText => translate('submitButtonText');
  String get successMessage => translate('successMessage');
  String get sortOrder => translate('sortOrder');
  String get widthClass => translate('widthClass');
  String get fullWidth => translate('fullWidth');
  String get halfWidth => translate('halfWidth');
  String get thirdWidth => translate('thirdWidth');
  String get isVisible => translate('isVisible');
  String get isReadOnly => translate('isReadOnly');
  String get noResponses => translate('noResponses');
  String get noResponsesHint => translate('noResponsesHint');
  String get selectFieldType => translate('selectFieldType');
  String get stringField => translate('stringField');
  String get emailField => translate('emailField');
  String get phoneField => translate('phoneField');
  String get urlField => translate('urlField');
  String get dateField => translate('dateField');
  String get numberField => translate('numberField');
  String get booleanField => translate('booleanField');
  String get selectField => translate('selectField');
  String get multiselectField => translate('multiselectField');
  String get fileField => translate('fileField');
  String get aliasField => translate('aliasField');
  String get roleSelectorField => translate('roleSelectorField');
  String get tagSelectorField => translate('tagSelectorField');
  String get sectionBreakField => translate('sectionBreakField');
  String get staticTextField => translate('staticTextField');
  String get linkPublic => translate('linkPublic');
  String get linkUnique => translate('linkUnique');
  String get noLinksYet => translate('noLinksYet');
  String get noLinksYetHint => translate('noLinksYetHint');
  String get reorderDone => translate('reorderDone');
  String get expiresAt => translate('expiresAt');
  String get maxUses => translate('maxUses');
  String get assignedUser => translate('assignedUser');
  String get responseDetail => translate('responseDetail');
  String get submittedAt => translate('submittedAt');
  String get reviewedBy => translate('reviewedBy');
  String get backToForms => translate('backToForms');
  String get previewForm => translate('previewForm');
  String get formBuilder => translate('formBuilder');
  String get proposeTag => translate('proposeTag');
  String get proposeTagHint => translate('proposeTagHint');
  String get revokeTag => translate('revokeTag');
  String get addTag => translate('addTag');
  String timeRange(String start, String end) => translate('timeRange', args: {'start': start, 'end': end});
  String get searchLocations => translate('searchLocations');
  String get allBadges => translate('allBadges');
  String get filterByBadge => translate('filterByBadge');
  String get filmLocationsOf => translate('filmLocationsOf');
  String get noLocationsShotHere => translate('noLocationsShotHere');
  String get whereWasItFilmed => translate('whereWasItFilmed');
  String get locationDetail => translate('locationDetail');
  String get addedBy => translate('addedBy');
  String get relatedLocations => translate('relatedLocations');
  String get filmLocations => translate('filmLocations');
  String get badgeSuggested => translate('badgeSuggested');
  String get badgeMandatory => translate('badgeMandatory');
  String get badgeFeatured => translate('badgeFeatured');
  String get addFilmLocation => translate('addFilmLocation');
  String get filmLocationRole => translate('filmLocationRole');
  String get keyframe => translate('keyframe');
  String get startTime => translate('startTime');
  String get endTime => translate('endTime');
  String get locationGallery => translate('locationGallery');
  String get addImageUrl => translate('addImageUrl');
  String get suggestRelations => translate('suggestRelations');
  String get noRelatedLocations => translate('noRelatedLocations');
  String get noFilmLocations => translate('noFilmLocations');
  String get mandatoryLocationRequired => translate('mandatoryLocationRequired');

  String get alreadyHasReservation => translate('alreadyHasReservation');
  String get reservationCreated => translate('reservationCreated');
  String get reservationConfirmed => translate('reservationConfirmed');
  String get reservationCancelled => translate('reservationCancelled');
  String get reservationPending => translate('reservationPending');
  String get sectionLabel => translate('sectionLabel');
  String get sectionHint => translate('sectionHint');
  String get rows => translate('rows');
  String get seatsPerRow => translate('seatsPerRow');
  String get startNumber => translate('startNumber');
  String get type => translate('type');
  String get start => translate('start');
  String get end => translate('end');
  String get venue => translate('venue');
  String get seatMap => translate('seatMap');
  String get yes => translate('yes');
  String get no => translate('no');
  String get ticketTypes => translate('ticketTypes');
  String get noTicketTypes => translate('noTicketTypes');
  String reserveCount(int count) => translate('reserve', args: {'count': count.toString()});
  String get seatMapDisabled => translate('seatMapDisabled');
  String get enableSeatMapHint => translate('enableSeatMapHint');
  String get confirm => translate('confirm');
  String get seatAvailable => translate('seatAvailable');
  String get seatReserved => translate('seatReserved');
  String get seatSold => translate('seatSold');
  String get seatAssigned => translate('seatAssigned');
  String get seatBlocked => translate('seatBlocked');
  String get noSeatsConfigured => translate('noSeatsConfigured');
  String get seat => translate('seat');
  String get seatReservedOrSold => translate('seatReservedOrSold');
  String get seatSelected => translate('seatSelected');
  String get calendar => translate('calendar');
  String get myEvents => translate('myEvents');
  String get noEventsOnDay => translate('noEventsOnDay');
  String get remindersEnabled => translate('remindersEnabled');
  String get eventReminderTitle => translate('eventReminderTitle');
  String eventReminderBody(String title) => translate('eventReminderBody', args: {'title': title});
  String get notificationChannelName => translate('notificationChannelName');
  String get notificationChannelDescription => translate('notificationChannelDescription');
  String rolesCount(int count) => translate('rolesCount', args: {'count': count.toString()});
  String tagsCount(int count) => translate('tagsCount', args: {'count': count.toString()});
  String get systemSender => translate('systemSender');
  String rowCount(int count) => translate('rowCount', args: {'count': count.toString()});
  String get typeFestival => translate('typeFestival');
  String get typeUser => translate('typeUser');
  String get webDeviceName => translate('webDeviceName');
  String bioLengthHint(int max) => translate('bioLengthHint', args: {'max': max.toString()});

  String get export => translate('export');
  String get rulebooks => translate('rulebooks');
  String get rulebookCategory => translate('rulebookCategory');
  String get noRulebooks => translate('noRulebooks');
  String get noRulebooksHint => translate('noRulebooksHint');
  String get newRulebook => translate('newRulebook');
  String get editRulebook => translate('editRulebook');
  String get deleteRulebook => translate('deleteRulebook');
  String get rulebookExternalUrl => translate('rulebookExternalUrl');
  String get rulebookPickPdf => translate('rulebookPickPdf');
  String get rulebookCurrentFile => translate('rulebookCurrentFile');
  String get rulebookDocumentRequired => translate('rulebookDocumentRequired');
  String get openDocument => translate('openDocument');

  /// Devuelve la traducción legible para la categoría de bases [category]
  /// (p. ej. "official_section" -> "Sección oficial").
  String getRulebookCategory(String category) {
    final categories = _localizedStrings['rulebookCategories'] as Map<String, dynamic>?;
    return categories?[category] ?? category;
  }

  /// Devuelve la traducción legible para la clave [role] dada
  /// (p. ej. "admin" -> "Administrador").
  String getRoleTranslation(String role) {
    final roles = _localizedStrings['roles'] as Map<String, dynamic>?;
    return roles?[role] ?? role;
  }

  /// Traduce una insignia de localización al idioma activo.
  ///
  /// Acepta los valores internos (español o código) y devuelve la etiqueta
  /// localizada; si el valor no es reconocido lo devuelve tal cual.
  String getBadgeTranslation(String badge) {
    switch (badge) {
      case 'Sugerido' || 'sugerido':
        return badgeSuggested;
      case 'Obligatorio' || 'obligatorio':
        return badgeMandatory;
      case 'Destacado' || 'destacado':
        return badgeFeatured;
      default:
        return badge;
    }
  }

  /// Traduce el tipo interno de localización heredada al idioma activo.
  String getLocationTypeTranslation(String type) {
    switch (type.toLowerCase()) {
      case 'festival':
        return typeFestival;
      case 'user':
        return typeUser;
      default:
        return type;
    }
  }

  /// Devuelve un mensaje de validación para [key] con interpolación opcional
  /// de parámetros mediante [args].
  String getValidationMessage(String key, {Map<String, dynamic>? args}) {
    final validation = _localizedStrings['validation'] as Map<String, dynamic>?;
    String message = validation?[key] ?? key;
    if (args != null) {
      args.forEach((key, value) {
        message = message.replaceAll('{$key}', value.toString());
      });
    }
    return message;
  }
}

/// Implementación de [LocalizationsDelegate] para [AppLocalizations].
class _AppLocalizationsDelegate extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  /// Indica si el locale está dentro de los idiomas soportados.
  @override
  bool isSupported(Locale locale) {
    return ['en', 'es', 'fr', 'de', 'it', 'ca', 'eu', 'gl', 'oc'].contains(locale.languageCode);
  }

  /// Carga las localizaciones para [locale].
  @override
  Future<AppLocalizations> load(Locale locale) async {
    AppLocalizations localizations = AppLocalizations(locale);
    await localizations.load();
    return localizations;
  }

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

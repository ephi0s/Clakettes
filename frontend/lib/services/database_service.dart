import 'package:hive_flutter/hive_flutter.dart';
import '../models/award_model.dart';
import '../models/channel_model.dart';
import '../models/committee_model.dart';
import '../models/event_model.dart';
import '../models/festival_model.dart';
import '../models/message_model.dart';
import '../models/notification_model.dart';
import '../models/registration_form_model.dart';
import '../models/role_delegation_model.dart';
import '../models/role_group_model.dart';
import '../models/role_transition_model.dart';
import '../models/session_model.dart';
import '../models/shortfilm_model.dart';
import '../models/user_alias_model.dart';
import '../models/user_model.dart';
import '../models/location_model.dart';
import '../models/location_tag_model.dart';
import '../models/location_image_model.dart';
import '../models/film_location_model.dart';
import '../models/form_definition_model.dart';

/// Inicializa la base de datos local Hive.
///
/// Servicio solo estático sin instancia singleton: hay que esperar a [init]
/// una vez al arrancar (desde `main()`) antes de usar cualquier caja o modelo
/// de Hive. Depende de las clases de modelo en `../models/`, cuyos adapters
/// se registran todos aquí.
class DatabaseService {
  /// Inicializa Hive para Flutter y registra todos los adapters de modelo.
  ///
  /// Debe llamarse una vez antes de abrir cajas; lanza una excepción si Hive ya
  /// está inicializado o un adapter se registra dos veces.
  static Future<void> init() async {
    await Hive.initFlutter();

    Hive.registerAdapter(AwardAdapter());
    Hive.registerAdapter(ChannelAdapter());
    Hive.registerAdapter(ChannelMemberAdapter());
    Hive.registerAdapter(CommitteeAdapter());
    Hive.registerAdapter(CommitteeMemberAdapter());
    Hive.registerAdapter(FestivalEventAdapter());
    Hive.registerAdapter(EventTicketTypeAdapter());
    Hive.registerAdapter(EventSeatAdapter());
    Hive.registerAdapter(EventReservationAdapter());
    Hive.registerAdapter(FestivalAdapter());
    Hive.registerAdapter(MessageAdapter());
    Hive.registerAdapter(AppNotificationAdapter());
    Hive.registerAdapter(RegistrationFormAdapter());
    Hive.registerAdapter(RegistrationFormSectionAdapter());
    Hive.registerAdapter(FestivalRegistrationAdapter());
    Hive.registerAdapter(RegistrationFormLinkAdapter());
    Hive.registerAdapter(RoleDelegationAdapter());
    Hive.registerAdapter(RoleGroupAdapter());
    Hive.registerAdapter(RoleGroupMembershipAdapter());
    Hive.registerAdapter(RoleTransitionAdapter());
    Hive.registerAdapter(UserSessionAdapter());
    Hive.registerAdapter(LocationTagAdapter());
    Hive.registerAdapter(LocationImageAdapter());
    Hive.registerAdapter(FilmLocationAdapter());
    Hive.registerAdapter(ShortFilmAdapter());
    Hive.registerAdapter(UserAliasAdapter());
    Hive.registerAdapter(UserAdapter());
    Hive.registerAdapter(LocationAdapter());
    Hive.registerAdapter(FormFieldOptionAdapter());
    Hive.registerAdapter(FormFieldAdapter());
    Hive.registerAdapter(FormPageAdapter());
    Hive.registerAdapter(FormDefinitionAdapter());
    Hive.registerAdapter(FormLinkAdapter());
    Hive.registerAdapter(FormFieldResponseAdapter());
    Hive.registerAdapter(FormResponseAdapter());
    Hive.registerAdapter(FormAccessRuleAdapter());
    await Hive.openBox('festivals');
    await Hive.openBox('users');
    await Hive.openBox('shortfilms');
    await Hive.openBox('messages');
  }
}

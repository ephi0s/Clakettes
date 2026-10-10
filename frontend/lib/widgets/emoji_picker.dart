import 'package:flutter/material.dart';

/// Grupo de emojis con nombre e icono de pestaña representativo.
class EmojiCategory {
  final String icon;

  /// Los emojis que pertenecen a esta categoría.
  final List<String> emojis;
  const EmojiCategory(this.icon, this.emojis);
}

/// Las categorías de emojis ofrecidas por [EmojiPicker], identificadas por icono de pestaña.
const List<EmojiCategory> kEmojiCategories = [
  EmojiCategory('😀', [
    '😀','😃','😄','😁','😆','😅','🤣','😂','🙂','😊',
    '😇','🥰','😍','🤩','😘','😋','😛','😜','🤪','😝',
    '🤗','🤭','🤔','🤐','🤨','😐','😑','😶','😏','😒',
    '🙄','😬','😌','😔','😴','😷','🤒','🤕','🤮','🥴',
    '😵','🤯','🤠','🥳','😎','🤓','🥺','😢','😭','😤',
    '😠','😡','💀','☠️','💩','🤡','👻','👽','🤖','😺',
    '😸','😹','😻','🙈','🙉','🙊','👶','👦','👧','👨',
    '👩','🧔','👴','👵','👮','🕵️','💂','👷','🤴','👸',
    '👼','🎅','🤶','💆','💇','🚶','🏃','💃','🕺','👯',
    '👭','👫','👬','💏','💑','👪','💪','👂','👃','👀',
    '👅','👄','💋',
  ]),
  EmojiCategory('🐻', [
    '🐶','🐱','🐭','🐹','🐰','🦊','🐻','🐼','🐨','🐯',
    '🦁','🐮','🐷','🐸','🐒','🐔','🐧','🐦','🐤','🦆',
    '🦅','🦉','🦇','🐺','🐴','🦄','🐝','🦋','🐌','🐞',
    '🐜','🦗','🕷️','🦂','🐢','🐍','🦎','🦖','🦕','🐙',
    '🦑','🦐','🦞','🦀','🐡','🐠','🐟','🐬','🐳','🐋',
    '🦈','🐊','🐅','🐆','🦓','🦍','🐘','🦏','🐪','🐫',
    '🦒','🐃','🐂','🐄','🐎','🐖','🐏','🐑','🐐','🦌',
    '🐕','🐩','🐈','🐓','🦃','🦩','🕊️','🐇','🐁','🐀',
    '🦔','🐾','🐉','🐲','🌵','🎄','🌲','🌳','🌴','🌱',
    '🌿','🍀','🍃','🍂','🍁','🍄','🌾','💐','🌷','🌹',
    '🥀','🌺','🌸','🌼','🌻','🌞','🌝','🌛','🌜','🌚',
    '🌕','🌖','🌗','🌘','🌑','🌒','🌓','🌔','🌙','🌎',
    '🌍','🌏','⭐','🌟','✨','⚡','🔥','🌈','☀️','⛅',
    '☁️','🌧️','⛈️','❄️','☔','🌊','🌫️',
  ]),
  EmojiCategory('🍔', [
    '🍏','🍎','🍐','🍊','🍋','🍌','🍉','🍇','🍓','🫐',
    '🍈','🍒','🍑','🥭','🍍','🥥','🥝','🍅','🍆','🥑',
    '🥦','🥬','🥒','🌶️','🌽','🥕','🥔','🍠','🥐','🍞',
    '🥖','🧀','🥚','🍳','🥞','🥓','🥩','🍗','🍖','🌭',
    '🍔','🍟','🍕','🌮','🌯','🥗','🥘','🍝','🍜','🍲',
    '🍛','🍣','🍱','🥟','🍤','🍙','🍚','🍥','🍢','🍡',
    '🍧','🍨','🍦','🥧','🧁','🍰','🎂','🍮','🍭','🍬',
    '🍫','🍿','🍩','🍪','🌰','🥜','🍯','🥛','☕','🍵',
    '🧃','🥤','🧋','🍶','🍺','🍻','🥂','🍷','🍸','🍹',
    '🍾','🥄','🍴','🥢',
  ]),
  EmojiCategory('✈️', [
    '🚗','🚕','🚙','🚌','🚎','🏎️','🚓','🚑','🚒','🚐',
    '🚚','🚛','🚜','🏍️','🛵','🛺','🚲','🛴','🛹','🚏',
    '⛽','🚨','🚥','🚦','🛑','🚧','⚓','⛵','🚤','🚢',
    '✈️','🛩️','🛫','🛬','💺','🚁','🚟','🚠','🚡','🛰️',
    '🚀','🛸','🏕️','🏖️','🏜️','🏝️','🏔️','🌋','🏗️','🏙️',
    '🌄','🌅','🌇','🌆','🏠','🏡','🏢','🏣','🏤','🏥',
    '🏦','🏨','🏩','🏪','🏫','🏬','🏭','🏯','🏰','🗼',
    '🗽','⛪','🕌','🛕','⛩️','⛲','⛺','🌁','🌃','🗾',
    '🎠','🎡','🎢','🎪','🚂','🚃','🚄','🚅','🚆','🚇',
    '🚉','🚊','🚝','🚞','🚋',
  ]),
  EmojiCategory('⚽', [
    '⚽','🏀','🏈','⚾','🎾','🏐','🏉','🎱','🏓','🏸',
    '🏒','🏑','🥍','⛳','🏹','🎣','🥊','🥋','🎽','⛸️',
    '🎿','⛷️','🏂','🏋️','🤼','🤸','🤺','⛹️','🤾','🏌️',
    '🏇','🏄','🏊','🤽','🚣','🧗','🚵','🚴','🎯','🎮',
    '🕹️','🎲','♠️','♥️','♦️','♣️','🃏','🀄','🎴','🎭',
    '🎨','🧵','🧶','🎼','🎤','🎧','🎷','🎸','🎹','🎺',
    '🎻','🥁','🎬','🎥','📺','📻','🎙️','🎯',
  ]),
  EmojiCategory('💡', [
    '💡','🔦','🕯️','🧯','🗑️','💰','💳','💎','⚖️','🧰',
    '🔧','🔨','⚒️','🔩','⚙️','🧲','🔪','🗡️','🛡️','🚬',
    '⚰️','🏺','🔮','📿','🔭','🔬','💊','💉','🩸','🧬',
    '🦠','🧫','🧪','🧹','🧺','🧻','🚽','🚿','🛁','🧼',
    '🧽','🧴','🔑','🗝️','🚪','🪑','🛋️','🛏️','🧸','🖼️',
    '🛍️','🛒','🎁','🎈','🎏','🎀','🎊','🎉','🏮','🎐',
    '✉️','📧','💌','📦','📜','📄','📑','📊','📈','📉',
    '📆','📅','📋','📁','📂','📰','📓','📕','📗','📘',
    '📙','📚','📖','🔖','📎','📐','📏','📌','📍','✂️',
    '🖊️','✒️','📝','✏️','🔍','🔎','🔒','🔓',
  ]),
  EmojiCategory('💬', [
    '❤️','🧡','💛','💚','💙','💜','🖤','🤍','🤎','💔',
    '❣️','💕','💞','💓','💗','💖','💘','💝','☮️','✝️',
    '☪️','☸️','✡️','🔯','☯️','⛎','♈','♉','♊','♋',
    '♌','♍','♎','♏','♐','♑','♒','♓','🆔','⚕️',
    '♿','🆚','🈁','🈂️','🈷️','🈶','🈯','🉐','🈹','🈚',
    '🈲','🉑','🈸','🈴','🈳','㊗️','㊙️','🈺','🈵','🔴',
    '🟠','🟡','🟢','🔵','🟣','🟤','⚫','⚪','⬛','⬜',
    '🔶','🔷','🔸','🔹','🔺','🔻','🔘','🔲','🔳','🏁',
    '🚩','🎌','🏴','🏳️','⬆️','⬇️','➡️','⬅️','🔛','🔝',
    '🔙','🔚','🔜','♻️','💢','💬','💭','🗯️','🕐','🕑',
    '🕒','🕓','🕔','🕕','🕖','🕗','🕘','🕙','🕚','🕛',
    '📳','📴','🔞','☢️','☣️','⚠️','🚸','⛔','🚫',
  ]),
  EmojiCategory('🚩', [
    '🇺🇳','🏳️','🏴','🏁','🚩','🎌','🏳️‍🌈','🏳️‍⚧️',
    '🇦🇫','🇦🇱','🇩🇿','🇦🇸','🇦🇩','🇦🇴','🇦🇷','🇦🇲',
    '🇦🇺','🇦🇹','🇦🇿','🇧🇸','🇧🇭','🇧🇩','🇧🇧','🇧🇾',
    '🇧🇪','🇧🇿','🇧🇯','🇧🇴','🇧🇦','🇧🇼','🇧🇷','🇧🇳',
    '🇧🇬','🇧🇫','🇧🇮','🇰🇭','🇨🇲','🇨🇦','🇨🇻','🇨🇫',
    '🇹🇩','🇨🇱','🇨🇳','🇨🇴','🇰🇲','🇨🇬','🇨🇩','🇨🇷',
    '🇭🇷','🇨🇺','🇨🇾','🇨🇿','🇩🇰','🇩🇯','🇩🇴','🇪🇨',
    '🇪🇬','🇸🇻','🇬🇶','🇪🇷','🇪🇪','🇪🇹','🇪🇺','🇫🇮',
    '🇫🇷','🇬🇦','🇬🇲','🇬🇪','🇩🇪','🇬🇭','🇬🇷','🇬🇹',
    '🇬🇳','🇬🇾','🇭🇹','🇭🇳','🇭🇰','🇭🇺','🇮🇸','🇮🇳',
    '🇮🇩','🇮🇷','🇮🇶','🇮🇪','🇮🇱','🇮🇹','🇨🇮','🇯🇲',
    '🇯🇵','🇯🇴','🇰🇿','🇰🇪','🇰🇮','🇰🇼','🇰🇬','🇱🇦',
    '🇱🇻','🇱🇧','🇱🇸','🇱🇷','🇱🇾','🇱🇮','🇱🇹','🇱🇺',
    '🇲🇴','🇲🇬','🇲🇼','🇲🇾','🇲🇻','🇲🇱','🇲🇹','🇲🇭',
    '🇲🇷','🇲🇺','🇲🇽','🇫🇲','🇲🇩','🇲🇨','🇲🇳','🇲🇪',
    '🇲🇦','🇲🇿','🇲🇲','🇳🇦','🇳🇵','🇳🇱','🇳🇿','🇳🇮',
    '🇳🇪','🇳🇬','🇰🇵','🇲🇰','🇳🇴','🇴🇲','🇵🇰','🇵🇼',
    '🇵🇸','🇵🇦','🇵🇬','🇵🇾','🇵🇪','🇵🇭','🇵🇱','🇵🇹',
    '🇵🇷','🇶🇦','🇷🇴','🇷🇺','🇷🇼','🇰🇳','🇱🇨','🇻🇨',
    '🇼🇸','🇸🇲','🇸🇹','🇸🇦','🇸🇳','🇷🇸','🇸🇨','🇸🇱',
    '🇸🇬','🇸🇰','🇸🇮','🇸🇧','🇸🇴','🇿🇦','🇰🇷','🇸🇸',
    '🇪🇸','🇱🇰','🇸🇩','🇸🇷','🇸🇿','🇸🇪','🇨🇭','🇸🇾',
    '🇹🇼','🇹🇯','🇹🇿','🇹🇭','🇹🇱','🇹🇬','🇹🇴','🇹🇹',
    '🇹🇳','🇹🇷','🇹🇲','🇹🇻','🇺🇬','🇺🇦','🇦🇪','🇬🇧',
    '🇺🇸','🇺🇾','🇺🇿','🇻🇺','🇻🇦','🇻🇪','🇻🇳','🇾🇪',
    '🇿🇲','🇿🇼',
  ]),
];

/// Selector de emojis en estilo bottom sheet con páginas categorizadas y barra de pestañas.
///
/// Úsalo cuando el usuario deba elegir un único emoji. Emite el emoji pulsado
/// a través de [onEmojiSelected]. Diseñado para la altura de un bottom sheet modal.
class EmojiPicker extends StatefulWidget {
  final void Function(String emoji) onEmojiSelected;
  const EmojiPicker({super.key, required this.onEmojiSelected});

  @override
  State<EmojiPicker> createState() => _EmojiPickerState();
}

class _EmojiPickerState extends State<EmojiPicker> {
  int _selectedCategory = 0;
  late final PageController _pageController;

  @override
  void initState() {
    super.initState();
    _pageController = PageController();
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Container(
      height: 370,
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
      ),
      child: Column(
        children: [
          _buildCategoryGrid(cs),
          _buildCategoryTabs(cs),
        ],
      ),
    );
  }

  Widget _buildCategoryGrid(ColorScheme cs) {
    return Expanded(
      child: PageView(
        controller: _pageController,
        onPageChanged: (i) => setState(() => _selectedCategory = i),
        children: kEmojiCategories.map((cat) => GridView.builder(
          padding: const EdgeInsets.fromLTRB(8, 8, 8, 4),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 8,
            childAspectRatio: 1,
          ),
          itemCount: cat.emojis.length,
          itemBuilder: (_, i) => GestureDetector(
            onTap: () => widget.onEmojiSelected(cat.emojis[i]),
            child: Center(child: Text(cat.emojis[i], style: const TextStyle(fontSize: 24))),
          ),
        )).toList(),
      ),
    );
  }

  Widget _buildCategoryTabs(ColorScheme cs) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 4),
      decoration: BoxDecoration(
        color: cs.surfaceContainerHighest.withValues(alpha: 0.3),
        border: Border(top: BorderSide(color: cs.outlineVariant)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: List.generate(kEmojiCategories.length, (i) {
          final isSelected = i == _selectedCategory;
          return Expanded(
            child: GestureDetector(
              onTap: () {
                setState(() => _selectedCategory = i);
                _pageController.animateToPage(
                  i,
                  duration: const Duration(milliseconds: 200),
                  curve: Curves.easeInOut,
                );
              },
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 4),
                decoration: BoxDecoration(
                  border: Border(
                    bottom: BorderSide(
                      color: isSelected ? cs.primary : Colors.transparent,
                      width: 2.5,
                    ),
                  ),
                ),
                child: Text(
                  kEmojiCategories[i].icon,
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 20, color: isSelected ? null : cs.onSurfaceVariant),
                ),
              ),
            ),
          );
        }),
      ),
    );
  }
}

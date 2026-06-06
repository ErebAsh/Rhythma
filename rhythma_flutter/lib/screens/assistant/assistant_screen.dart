import 'dart:ui' show ImageFilter;
import 'package:flutter/material.dart';
import '../../config/theme.dart';
import '../../components/shared.dart';
import '../../services/gemini_service.dart';
import '../../services/local_storage_service.dart';

class AssistantScreen extends StatefulWidget {
  const AssistantScreen({Key? key}) : super(key: key);
  @override
  State<AssistantScreen> createState() => _AssistantScreenState();
}

class _AssistantScreenState extends State<AssistantScreen> {
  final TextEditingController _ctrl = TextEditingController();
  final ScrollController _scroll = ScrollController();
  bool _isLoading = false;

  final _suggested = const [
    'Why are my periods irregular?',
    'What causes severe cramps?',
    'Is a 35-day cycle normal?',
    'Foods that help with PMS',
    'मेरे पीरियड्स अनियमित हैं — क्या यह सामान्य है?',
  ];

  final List<_Msg> _messages = [
    _Msg(
      role: 'ai',
      text: 'Hi Aarya 🌸 I\'m Rhythma, your private health companion. '
          'Ask me anything about your cycle, symptoms, or wellbeing — '
          'in English, Hindi, Marathi, or Tamil.',
    ),
  ];

  Future<void> _send(String text) async {
    final t = text.trim();
    if (t.isEmpty || _isLoading) return;
    setState(() {
      _messages.add(_Msg(role: 'user', text: t));
      _isLoading = true;
    });
    _ctrl.clear();
    _scrollToBottom();

    final history = _messages
        .take(_messages.length - 1)
        .map((m) => {'role': m.role == 'user' ? 'user' : 'model', 'text': m.text})
        .toList();

    final response = await GeminiService.chat(message: t, history: history);

    setState(() {
      _isLoading = false;
      _messages.add(_Msg(role: 'ai', text: response.text, isError: response.isError));
    });
    _scrollToBottom();
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 80), () {
      if (_scroll.hasClients) {
        _scroll.animateTo(
          _scroll.position.maxScrollExtent + 200,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  void dispose() {
    _ctrl.dispose();
    _scroll.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final lang = LocalStorageService.preferredLanguage;
    return Column(
      children: [
        // Header
        Padding(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 0),
          child: Row(
            children: [
              Container(
                width: 40, height: 40,
                decoration: BoxDecoration(gradient: RhythmaGradients.primary, shape: BoxShape.circle),
                child: const Icon(Icons.favorite_rounded, color: Colors.white, size: 20),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  const Text('Rhythma Assistant',
                      style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: RhythmaColors.foreground)),
                  Text(lang == 'hi' ? 'आपकी स्वास्थ्य साथी • निजी और सुरक्षित' : 'Your private health companion',
                      style: TextStyle(fontSize: 12, color: RhythmaColors.mutedFg)),
                ]),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(color: RhythmaColors.primary.withOpacity(0.1), borderRadius: BorderRadius.circular(20)),
                child: Text(lang.toUpperCase(),
                    style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: RhythmaColors.primary)),
              ),
            ],
          ),
        ),
        const SizedBox(height: 8),

        // Chat list
        Expanded(
          child: ListView.builder(
            controller: _scroll,
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
            itemCount: _messages.length + (_isLoading ? 1 : 0),
            itemBuilder: (ctx, i) {
              if (_isLoading && i == _messages.length) return _TypingBubble();
              return _ChatBubble(msg: _messages[i]);
            },
          ),
        ),

        // Suggested chips (only before first user message)
        if (_messages.length == 1)
          SizedBox(
            height: 38,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: _suggested.length,
              separatorBuilder: (_, __) => const SizedBox(width: 8),
              itemBuilder: (_, i) => GestureDetector(
                onTap: () => _send(_suggested[i]),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                  decoration: BoxDecoration(
                    color: RhythmaColors.surfaceMuted,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: RhythmaColors.border),
                  ),
                  child: Text(_suggested[i], style: const TextStyle(fontSize: 12, color: RhythmaColors.foreground)),
                ),
              ),
            ),
          ),
        const SizedBox(height: 8),

        // Input bar
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 0, 16, 90),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(28),
            child: BackdropFilter(
              filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
              child: Container(
                decoration: BoxDecoration(
                  color: RhythmaColors.surface.withOpacity(0.85),
                  borderRadius: BorderRadius.circular(28),
                  border: Border.all(color: RhythmaColors.lavender.withOpacity(0.5)),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _ctrl,
                        style: const TextStyle(fontSize: 14, color: RhythmaColors.foreground),
                        decoration: InputDecoration(
                          hintText: lang == 'hi' ? 'अपना सवाल पूछें...' : 'Ask anything about your health...',
                          border: InputBorder.none,
                          contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                        ),
                        onSubmitted: _send,
                        textInputAction: TextInputAction.send,
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.only(right: 6),
                      child: GestureDetector(
                        onTap: () => _send(_ctrl.text),
                        child: Container(
                          width: 40, height: 40,
                          decoration: BoxDecoration(gradient: RhythmaGradients.primary, shape: BoxShape.circle),
                          child: const Icon(Icons.send_rounded, color: Colors.white, size: 18),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class _Msg {
  final String role;
  final String text;
  final bool isError;
  const _Msg({required this.role, required this.text, this.isError = false});
}

class _ChatBubble extends StatelessWidget {
  final _Msg msg;
  const _ChatBubble({required this.msg});
  @override
  Widget build(BuildContext context) {
    final isUser = msg.role == 'user';
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (!isUser) ...[
            Container(
              width: 28, height: 28,
              decoration: BoxDecoration(gradient: RhythmaGradients.primary, shape: BoxShape.circle),
              child: const Icon(Icons.favorite_rounded, color: Colors.white, size: 14),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                gradient: isUser ? RhythmaGradients.primary : null,
                color: isUser ? null : RhythmaColors.surface.withOpacity(0.85),
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(18),
                  topRight: const Radius.circular(18),
                  bottomLeft: Radius.circular(isUser ? 18 : 4),
                  bottomRight: Radius.circular(isUser ? 4 : 18),
                ),
                border: isUser ? null : Border.all(color: RhythmaColors.lavender.withOpacity(0.4)),
              ),
              child: Text(msg.text,
                  style: TextStyle(fontSize: 14, height: 1.5,
                      color: isUser ? Colors.white : RhythmaColors.foreground)),
            ),
          ),
        ],
      ),
    );
  }
}

class _TypingBubble extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(children: [
        Container(
          width: 28, height: 28,
          decoration: BoxDecoration(gradient: RhythmaGradients.primary, shape: BoxShape.circle),
          child: const Icon(Icons.favorite_rounded, color: Colors.white, size: 14),
        ),
        const SizedBox(width: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          decoration: BoxDecoration(
            color: RhythmaColors.surface.withOpacity(0.85),
            borderRadius: const BorderRadius.only(
              topLeft: Radius.circular(18), topRight: Radius.circular(18),
              bottomRight: Radius.circular(18), bottomLeft: Radius.circular(4),
            ),
            border: Border.all(color: RhythmaColors.lavender.withOpacity(0.4)),
          ),
          child: Row(mainAxisSize: MainAxisSize.min, children: [
            _dot(0), const SizedBox(width: 4),
            _dot(150), const SizedBox(width: 4),
            _dot(300),
          ]),
        ),
      ]),
    );
  }

  Widget _dot(int delay) => _AnimatedDot(delay: delay);
}

class _AnimatedDot extends StatefulWidget {
  final int delay;
  const _AnimatedDot({required this.delay});
  @override
  State<_AnimatedDot> createState() => _AnimatedDotState();
}

class _AnimatedDotState extends State<_AnimatedDot> with SingleTickerProviderStateMixin {
  late final AnimationController _c;
  late final Animation<double> _a;
  @override
  void initState() {
    super.initState();
    _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 600))..repeat(reverse: true);
    _a = CurvedAnimation(parent: _c, curve: Curves.easeInOut);
    Future.delayed(Duration(milliseconds: widget.delay), () { if (mounted) _c.forward(); });
  }
  @override
  void dispose() { _c.dispose(); super.dispose(); }
  @override
  Widget build(BuildContext context) => FadeTransition(
    opacity: _a,
    child: Container(width: 7, height: 7,
        decoration: const BoxDecoration(color: RhythmaColors.primary, shape: BoxShape.circle)),
  );
}

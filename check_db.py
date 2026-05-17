import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
django.setup()

from apps.users.models import User
from apps.clients.models import Client
from apps.chats.models import Chat
from apps.messaging.models import Message
from apps.prompts.models import Prompt

print('===== DATABASE =====')
print('Users:', User.objects.count())
print('Clients:', Client.objects.count())
print('Chats:', Chat.objects.count())
print('Messages total:', Message.objects.count())
print('  inbound:', Message.objects.filter(direction='inbound').count())
print('  outbound:', Message.objects.filter(direction='outbound').count())
print('  AI generated:', Message.objects.filter(is_ai_generated=True).count())
print('Prompts:', Prompt.objects.count(), '| active:', Prompt.objects.filter(is_active=True).count())

print()
print('===== CLIENTS =====')
for c in Client.objects.all().order_by('-last_seen'):
    st = 'BLOCKED' if c.is_blocked else 'active'
    print(f'  {c.decrypted_phone} | {c.name} | {st} | tags: {c.tags}')

print()
print('===== CHATS =====')
for ch in Chat.objects.all().order_by('-last_message_at'):
    print(f'  Chat {ch.id} | {ch.client.decrypted_phone} | {ch.status} | unread: {ch.unread_count}')

print()
print('===== LAST 5 AI REPLIES =====')
for m in Message.objects.filter(is_ai_generated=True).order_by('-created_at')[:5]:
    preview = m.decrypted_content[:100].replace('\n', ' ')
    print(f'  >> {preview}')

print()
print('===== ACTIVE PROMPT =====')
p = Prompt.objects.filter(is_active=True).first()
if p:
    print(f'  Name: {p.name}')
    print(f'  Scenario: {p.scenario}')
    print(f'  Content preview: {p.content[:150]}')
else:
    print('  NO ACTIVE PROMPT!')

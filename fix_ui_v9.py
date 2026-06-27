import re

file_path = 'money-maker-ui/index.html'
with open(file_path, 'r') as f:
    content = f.read()

# 1. Update Terminal Container to include a status overlay
content = content.replace('<div id="terminal-chat-container" class="flex-1 glass rounded-[2.5rem] overflow-hidden p-4 relative"><div class="absolute top-4 right-6 text-[10px] font-black uppercase tracking-widest text-emerald-500/40 z-10">Direct Agent Link</div></div>',
                          '''<div id="terminal-chat-container" class="flex-1 glass rounded-[2.5rem] overflow-hidden p-4 relative">
                    <div id="terminal-overlay" class="absolute inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm z-20 transition-opacity duration-500">
                        <div class="text-center space-y-4">
                            <div class="animate-spin w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full mx-auto"></div>
                            <p class="text-emerald-500 font-black uppercase tracking-widest text-[10px]">Establishing Secure Link...</p>
                        </div>
                    </div>
                    <div class="absolute top-4 right-6 text-[10px] font-black uppercase tracking-widest text-emerald-500/40 z-10">Direct Agent Link</div>
                    <button onclick="focusTerminal()" class="absolute bottom-6 right-6 lg:hidden p-4 emerald-btn text-white rounded-full shadow-2xl z-30"><i data-lucide="message-square" class="w-6 h-6"></i></button>
                </div>''')

# 2. Update JS to handle overlay and auto-focus
js_updates = """
        function focusTerminal() {
            if (mainTerm) {
                mainTerm.focus();
                // On some mobiles, we need a small delay or a dummy input to force keyboard
                const dummy = document.createElement('input');
                dummy.style.position = 'absolute'; dummy.style.opacity = '0';
                document.body.appendChild(dummy); dummy.focus();
                setTimeout(() => { mainTerm.focus(); document.body.removeChild(dummy); }, 50);
            }
        }

        function initTerminals() {
            const isMobile = window.innerWidth < 640;
            const container = document.getElementById('terminal-chat-container');
            const overlay = document.getElementById('terminal-overlay');

            mainTerm = new Terminal({ theme: { background: '#05050500', foreground: '#fff', cursor: '#10a37f' }, fontSize: isMobile ? 12 : 16, cursorBlink: true, fontFamily: 'Geist Mono', scrollback: 1000 });
            const fit = new FitAddon.FitAddon();
            mainTerm.loadAddon(fit);
            mainTerm.open(container);
            fit.fit();

            function connect() {
                const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
                const ws = new WebSocket(`${protocol}//${location.host}/api/pty?token=${token}`);

                ws.onopen = () => {
                    overlay.classList.add('opacity-0');
                    setTimeout(() => overlay.classList.add('hidden'), 500);
                    mainTerm.write('\\r\\n\\x1b[32m[CONNECTED TO MONEY MAKER 🤑]\\x1b[0m\\r\\n');
                    mainTerm.focus();
                };

                ws.onmessage = async (e) => {
                    const data = e.data instanceof Blob ? new Uint8Array(await e.data.arrayBuffer()) : e.data;
                    mainTerm.write(data);
                };

                ws.onclose = () => {
                    overlay.classList.remove('hidden');
                    overlay.classList.remove('opacity-0');
                    setTimeout(connect, 3000); // Retry loop
                };

                mainTerm.onData(d => { if(ws.readyState === WebSocket.OPEN) ws.send(d); });
            }

            container.addEventListener('click', () => mainTerm.focus());
            connect();

            logTerm = new Terminal({ theme: { background: '#00000000', foreground: '#10b981' }, fontSize: 12, fontFamily: 'Geist Mono' });
            logTerm.open(document.getElementById('terminal-container'));

            setInterval(async () => {
                if (currentPage !== 'logs') return;
                try {
                    const s = await apiFetch('/api/status');
                    const d = await apiFetch(`/api/fs/read-text?path=${encodeURIComponent(s.hermes_home+'/agent.log')}`);
                    if (d.text) { logTerm.clear(); logTerm.write(d.text.split('\\n').slice(-150).join('\\r\\n')); }
                } catch(e){}
            }, 5000);
            window.addEventListener('resize', () => { fit.fit(); });
        }
"""

content = re.sub(r'function initTerminals\(\) \{.*?window\.addEventListener\(\'resize\'.*?\);.*?\}', js_updates.strip(), content, flags=re.DOTALL)
# Add focusTerminal to global scope
content = content.replace("let currentPage = 'chat', mainTerm, logTerm;", "let currentPage = 'chat', mainTerm, logTerm;\n\n        function focusTerminal() { if(mainTerm) mainTerm.focus(); }")

with open(file_path, 'w') as f:
    f.write(content)

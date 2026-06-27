import re

file_path = 'money-maker-ui/index.html'
with open(file_path, 'r') as f:
    content = f.read()

# 1. Update Terminal Container
new_container = '''<div id="terminal-chat-container" class="flex-1 glass rounded-[2.5rem] overflow-hidden p-4 relative">
                    <div id="terminal-overlay" class="absolute inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm z-20 transition-opacity duration-500">
                        <div class="text-center space-y-4">
                            <div class="animate-spin w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full mx-auto"></div>
                            <p class="text-emerald-500 font-black uppercase tracking-widest text-[10px]">Establishing Secure Link...</p>
                        </div>
                    </div>
                    <div class="absolute top-4 right-6 text-[10px] font-black uppercase tracking-widest text-emerald-500/40 z-10">Direct Agent Link</div>
                    <button onclick="focusTerminal()" class="absolute bottom-6 right-6 lg:hidden p-4 emerald-btn text-white rounded-full shadow-2xl z-30"><i data-lucide="message-square" class="w-6 h-6"></i></button>
                </div>'''

content = re.sub(r'<div id="terminal-chat-container".*?</div>', new_container, content, flags=re.DOTALL)

# 2. Complete Script Override to avoid regex escape issues
new_script = r"""
    <script>
        lucide.createIcons();
        const token = window.__HERMES_SESSION_TOKEN__ || '';
        let currentPage = 'chat', mainTerm, logTerm;

        function focusTerminal() {
            if (mainTerm) {
                mainTerm.focus();
                const dummy = document.createElement('input');
                dummy.style.position = 'absolute'; dummy.style.opacity = '0';
                document.body.appendChild(dummy); dummy.focus();
                setTimeout(() => { mainTerm.focus(); document.body.removeChild(dummy); }, 50);
            }
        }

        async function apiFetch(path, opts = {}) {
            const h = { ...opts.headers, 'X-Hermes-Session-Token': token };
            try {
                const r = await fetch(path, { ...opts, headers: h });
                if (r.status === 401) return { status: 'restricted', model: 'Gemini 2.0 Flash' };
                if (!r.ok) throw new Error(r.status);
                return r.json();
            } catch (e) {
                if (path.includes('/api/status')) return { status: 'offline', model: 'Gemini 2.0 Flash' };
                throw e;
            }
        }

        async function init() {
            try {
                document.getElementById('status-model').innerText = 'Gemini 2.0 Flash';
                const s = await apiFetch('/api/status');
                if (s.model) document.getElementById('status-model').innerText = s.model;
                document.getElementById('welcome-view').classList.add('hidden');
                document.getElementById('active-chat').classList.remove('hidden');
            } catch (e) {
                document.getElementById('welcome-view').classList.add('hidden');
                document.getElementById('active-chat').classList.remove('hidden');
            }
            initTerminals();
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
                    if(overlay) {
                        overlay.classList.add('opacity-0');
                        setTimeout(() => overlay.classList.add('hidden'), 500);
                    }
                    mainTerm.write('\r\n\x1b[32m[CONNECTED TO MONEY MAKER 🤑]\x1b[0m\r\n');
                    mainTerm.focus();
                };

                ws.onmessage = async (e) => {
                    const data = e.data instanceof Blob ? new Uint8Array(await e.data.arrayBuffer()) : e.data;
                    mainTerm.write(data);
                };

                ws.onclose = () => {
                    if(overlay) {
                        overlay.classList.remove('hidden');
                        overlay.classList.remove('opacity-0');
                    }
                    setTimeout(connect, 3000);
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
                    if (d.text) { logTerm.clear(); logTerm.write(d.text.split('\n').slice(-150).join('\r\n')); }
                } catch(e){}
            }, 5000);
            window.addEventListener('resize', () => { fit.fit(); });
        }

        function showPage(id) {
            ['chat', 'skills', 'files', 'logs', 'api'].forEach(p => {
                const el = document.getElementById(`page-${p}`);
                if(el) el.classList.add('hidden');
                const n = document.getElementById(`nav-${p}`), m = document.getElementById(`mob-${p}`);
                if(n) n.classList.remove('active');
                if(m) { m.classList.remove('text-emerald-500'); m.classList.add('text-gray-500'); }
            });
            const targetPage = document.getElementById(`page-${id}`);
            if(targetPage) targetPage.classList.remove('hidden');
            const an = document.getElementById(`nav-${id}`), am = document.getElementById(`mob-${id}`);
            if(an) an.classList.add('active');
            if(am) { am.classList.add('text-emerald-500'); am.classList.remove('text-gray-500'); }
            currentPage = id;
            if (id === 'skills') loadSkills();
            if (id === 'files') loadFiles();
            setTimeout(() => window.dispatchEvent(new Event('resize')), 150);
        }

        async function loadSkills() {
            const l = document.getElementById('skills-list');
            l.innerHTML = '<div class="col-span-full py-20 flex justify-center"><div class="animate-spin w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full"></div></div>';
            try {
                const s = await apiFetch('/api/skills');
                l.innerHTML = s.map(sk => `<div class="glass rounded-3xl p-8 space-y-4"><div class="p-3 bg-emerald-500/10 rounded-xl w-fit text-emerald-500"><i data-lucide="zap" class="w-6 h-6"></i></div><h4 class="font-black text-xl text-white tracking-tight">${sk.name}</h4><p class="text-sm text-gray-500">${sk.description || 'Module initialized.'}</p></div>`).join('');
                lucide.createIcons();
            } catch (e) { l.innerHTML = `<p class="text-red-500">${e.message}</p>`; }
        }

        async function loadFiles() {
            const l = document.getElementById('files-list');
            l.innerHTML = 'Loading files...';
            try {
                const s = await apiFetch('/api/status');
                const files = await apiFetch(`/api/fs/list?path=${encodeURIComponent(s.hermes_home)}`);
                l.innerHTML = files.map(f => `<div class="flex items-center gap-2 p-2 hover:bg-white/5 rounded cursor-pointer"><i data-lucide="${f.is_dir ? 'folder' : 'file'}" class="w-4 h-4 opacity-50"></i> <span>${f.name}</span> <span class="ml-auto text-[10px] opacity-30">${f.size || ''}</span></div>`).join('');
                lucide.createIcons();
            } catch (e) { l.innerHTML = `<p class="text-red-500">${e.message}</p>`; }
        }

        async function performInitialSetup() {
            await saveGenericEnv({ 'GROQ_API_KEY': document.getElementById('setup-groq').value, 'DEFAULT_MODEL': document.getElementById('setup-model').value });
            location.reload();
        }

        async function saveEnv() {
            await saveGenericEnv({ 'GROQ_API_KEY': document.getElementById('input-groq').value, 'GOOGLE_API_KEY': document.getElementById('input-google').value, 'HF_TOKEN': document.getElementById('input-hf').value, 'DEFAULT_MODEL': document.getElementById('input-model').value });
        }

        async function saveGenericEnv(keys) {
            try {
                for (const [k, v] of Object.entries(keys)) {
                    if (v && v.trim()) await apiFetch('/api/env', { method: 'PUT', body: JSON.stringify({ key: k, value: v.trim() }), headers: { 'Content-Type': 'application/json' } });
                }
                alert("Matrix Sync Successful.");
                await apiFetch('/api/gateway/restart', { method: 'POST' });
            } catch(e){ alert(e.message); }
        }

        function clearLogs() { if(logTerm) logTerm.clear(); }

        function toggleSidebar() {
            const sidebar = document.querySelector('.desktop-sidebar');
            const icon = document.querySelector('.sidebar-toggle-btn i');
            if(!sidebar) return;
            sidebar.classList.toggle('collapsed');
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebar-collapsed', isCollapsed);
            if (icon) {
                icon.setAttribute('data-lucide', isCollapsed ? 'chevron-right' : 'chevron-left');
                lucide.createIcons();
            }
            setTimeout(() => window.dispatchEvent(new Event('resize')), 305);
        }

        const sidebarState = localStorage.getItem('sidebar-collapsed');
        const desktopSidebar = document.querySelector('.desktop-sidebar');
        const toggleIcon = document.querySelector('.sidebar-toggle-btn i');
        if (desktopSidebar) {
            if (sidebarState === 'false') {
                desktopSidebar.classList.remove('collapsed');
                if (toggleIcon) toggleIcon.setAttribute('data-lucide', 'chevron-left');
            } else {
                desktopSidebar.classList.add('collapsed');
                if (toggleIcon) toggleIcon.setAttribute('data-lucide', 'chevron-right');
                localStorage.setItem('sidebar-collapsed', 'true');
            }
        }
        lucide.createIcons();
        init();
    </script>
"""

content = re.sub(r'<script>.*?</script>', new_script.strip(), content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)

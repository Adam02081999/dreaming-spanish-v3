import pandas as pd
import json

# 讀取剛傳入的 TSV 檔案
df = pd.read_csv('argentino-dreaming spanish v3.tsv', sep='\t')
print("欄位與形狀:", df.shape)
print("欄位列表:", df.columns.tolist())
print(df.head(5))

sentences_all = []
for idx, row in df.iterrows():
    # 動態取得欄位值
    es = str(row['Spanish']).strip() if 'Spanish' in row and pd.notna(row['Spanish']) else ""
    en = str(row['English']).strip() if 'English' in row and pd.notna(row['English']) else ""
    note = str(row['Note']).strip() if 'Note' in row and pd.notna(row['Note']) else ""
    sec = str(row['Section']).strip() if 'Section' in row and pd.notna(row['Section']) else ""
    
    # 取編號，如果沒有就用 idx + 1
    if '#' in row and pd.notna(row['#']):
        try:
            num = int(row['#'])
        except:
            num = idx + 1
    else:
        num = idx + 1
    
    sentences_all.append({
        "id": num,
        "es": es,
        "en": en,
        "note": note,
        "sec": sec
    })

js_sentences_json = json.dumps(sentences_all, ensure_ascii=False, indent=2)

html_template = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🇦🇷 阿根廷西語全句子 - index.html 語音播放器</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen flex flex-col font-sans">

    <!-- 頂部導覽列 -->
    <header class="bg-sky-700 text-white shadow-md sticky top-0 z-50 p-4 text-center font-bold text-lg flex justify-between items-center px-6">
        <span class="flex items-center gap-2">🇦🇷 阿根廷西語 (Rioplatense) 全句子跟讀播放器</span>
        <span id="voiceStatus" class="text-xs bg-sky-800 px-3 py-1 rounded-full font-normal">語音引擎載入中...</span>
    </header>

    <!-- 主要內容區 -->
    <main class="max-w-4xl mx-auto px-4 py-8 flex-grow w-full space-y-6">
        
        <!-- 控制面板 -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
            <div class="flex flex-wrap items-center justify-between gap-4">
                <div>
                    <h1 class="text-2xl font-bold text-slate-900">🇦🇷 阿根廷日常西語隨身聽 (Dreaming Spanish 完整版)</h1>
                    <p class="text-sm text-slate-500 mt-1">含 Vos 變位、拉普拉塔河方言 (Rioplatense) 與英文對照註解</p>
                </div>
                <!-- 語速選擇 -->
                <div class="flex items-center space-x-2">
                    <label class="text-sm font-medium text-slate-600">朗讀語速：</label>
                    <select id="rateSelect" class="border rounded-lg px-3 py-1.5 text-sm bg-slate-50 focus:outline-none focus:ring-2 focus:ring-sky-500">
                        <option value="0.5">0.5x (慢速學習)</option>
                        <option value="0.75" selected>0.75x (推薦跟讀)</option>
                        <option value="1.0">1.0x (正常語速)</option>
                    </select>
                </div>
            </div>

            <!-- 控制按鈕 -->
            <div class="flex flex-wrap gap-3 pt-3 border-t border-slate-100 items-center">
                <button onclick="startAutoplay()" id="btn-play" class="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold shadow-sm transition flex items-center gap-2">
                    ▶ 開始全自動「西語+英文」接續朗讀
                </button>
                <button onclick="pauseAudio()" class="px-4 py-2.5 bg-amber-500 hover:bg-amber-600 text-white rounded-xl font-medium transition">
                    ⏸ 暫停
                </button>
                <button onclick="stopAudio()" class="px-4 py-2.5 bg-rose-50 text-rose-600 hover:bg-rose-100 rounded-xl font-medium transition">
                    ⏹ 停止
                </button>

                <!-- 單句重複切換 -->
                <div class="ml-auto flex items-center space-x-2 text-sm text-slate-600">
                    <label class="flex items-center space-x-1.5 cursor-pointer select-none">
                        <input type="checkbox" id="repeatOneCheck" class="rounded text-sky-600 focus:ring-sky-500 w-4 h-4">
                        <span class="font-medium">單句無限重複</span>
                    </label>
                </div>
            </div>
        </div>

        <!-- 搜尋列 -->
        <div class="flex gap-4">
            <input type="text" id="searchInput" oninput="filterSentences()" placeholder="🔍 搜尋西語、英文或在地用法註解..." class="w-full px-4 py-2.5 border rounded-xl bg-white shadow-sm focus:ring-2 focus:ring-sky-500 outline-none text-sm">
        </div>

        <!-- 句子列表 -->
        <div id="sentenceList" class="space-y-4">
            <!-- 由 JavaScript 自動動態生成句子 -->
        </div>

    </main>

    <!-- 底部固定播放控制列 -->
    <footer class="bg-white border-t border-slate-200 shadow-lg sticky bottom-0 z-40 py-3 px-6">
        <div class="max-w-4xl mx-auto flex items-center justify-between">
            <div class="text-sm truncate pr-4">
                <span class="text-slate-400">目前播放：</span>
                <span id="currentPlayingText" class="font-bold text-sky-700">準備就緒，請點擊上方綠色播放鍵開始</span>
            </div>
            <div class="space-x-2 shrink-0">
                <button onclick="prevSentence()" class="px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-sm font-medium transition">上一句</button>
                <button onclick="nextSentence()" class="px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-sm font-medium transition">下一句</button>
            </div>
        </div>
    </footer>

    <script>
        // 完整的阿根廷西語資料庫
        const rawSentences = __SENTENCES_JSON__;

        let displaySentences = [...rawSentences];
        let currentIdx = 0;
        let isAutoplayActive = false;
        let synth = window.speechSynthesis;

        function initVoices() {
            let voices = synth.getVoices();
            if (voices.length > 0) {
                const esVoice = voices.find(v => v.lang === 'es-AR') || voices.find(v => v.lang.startsWith('es'));
                const statusEl = document.getElementById('voiceStatus');
                if (esVoice) {
                    statusEl.innerText = `語音引擎：${esVoice.name} (${esVoice.lang})`;
                    statusEl.className = "text-xs bg-emerald-700 px-3 py-1 rounded-full font-normal";
                } else {
                    statusEl.innerText = "語音引擎已就緒 (使用系統預設西語)";
                    statusEl.className = "text-xs bg-emerald-700 px-3 py-1 rounded-full font-normal";
                }
            }
        }

        if (speechSynthesis.onvoiceschanged !== undefined) {
            speechSynthesis.onvoiceschanged = initVoices;
        }

        function renderList() {
            const container = document.getElementById('sentenceList');
            container.innerHTML = '';
            
            displaySentences.forEach((item, index) => {
                const card = document.createElement('div');
                card.id = `card-${index}`;
                card.className = `bg-white p-5 rounded-2xl shadow-sm border transition-all ${index === currentIdx ? 'border-sky-500 ring-2 ring-sky-100 bg-sky-50/20' : 'border-slate-100 hover:border-slate-200'}`;
                card.innerHTML = `
                    <div class="flex items-start justify-between gap-3">
                        <div class="space-y-1.5">
                            <div class="flex items-center gap-2">
                                <span class="text-xs font-bold text-sky-700 bg-sky-100/80 px-2.5 py-0.5 rounded-full">#${item.id}</span>
                                ${item.sec ? `<span class="text-xs font-medium text-slate-500">${item.sec}</span>` : ''}
                            </div>
                            <h2 class="text-xl font-bold text-slate-900 pt-0.5">${item.es}</h2>
                            <p class="text-slate-600 text-sm font-medium">${item.en}</p>
                            ${item.note ? `<div class="text-xs italic text-amber-800 bg-amber-50/80 border border-amber-200/50 p-2.5 rounded-xl mt-2">💡 註解：${item.note}</div>` : ''}
                        </div>
                        <button onclick="playSingle(${index})" class="bg-sky-600 hover:bg-sky-700 text-white px-3.5 py-2 rounded-xl text-xs font-bold shadow-sm transition shrink-0 flex items-center gap-1">
                            🔊 單句朗讀
                        </button>
                    </div>
                `;
                container.appendChild(card);
            });
        }

        function scrollToCurrent() {
            const el = document.getElementById(`card-${currentIdx}`);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        function playSingle(index) {
            unlockAudio();
            isAutoplayActive = false;
            currentIdx = index;
            renderList();
            scrollToCurrent();
            playCurrentSentence();
        }

        function startAutoplay() {
            unlockAudio();
            isAutoplayActive = true;
            renderList();
            scrollToCurrent();
            playCurrentSentence();
        }

        function unlockAudio() {
            if (synth.paused) synth.resume();
            let u = new SpeechSynthesisUtterance("");
            synth.speak(u);
        }

        function playCurrentSentence() {
            synth.cancel();

            if (currentIdx >= displaySentences.length) return;

            const item = displaySentences[currentIdx];
            document.getElementById('currentPlayingText').innerText = `#${item.id} - ${item.es} (${item.en})`;

            const rate = parseFloat(document.getElementById('rateSelect').value);
            const isRepeatOne = document.getElementById('repeatOneCheck').checked;

            let voices = synth.getVoices();
            let esVoice = voices.find(v => v.lang === 'es-AR') || 
                          voices.find(v => v.lang.startsWith('es-419')) || 
                          voices.find(v => v.lang.startsWith('es')) || null;
            
            let enVoice = voices.find(v => v.lang === 'en-US') || 
                          voices.find(v => v.lang.startsWith('en')) || null;

            // 1. 先朗讀阿根廷西語
            speakText(item.es, 'es-AR', esVoice, rate, () => {
                // 2. 停頓 0.5 秒後朗讀英文譯文
                setTimeout(() => {
                    speakText(item.en, 'en-US', enVoice, rate, () => {
                        if (isRepeatOne) {
                            setTimeout(playCurrentSentence, 800);
                        } else if (isAutoplayActive) {
                            if (currentIdx < displaySentences.length - 1) {
                                currentIdx++;
                                renderList();
                                scrollToCurrent();
                                setTimeout(playCurrentSentence, 1000);
                            } else {
                                isAutoplayActive = false;
                                document.getElementById('currentPlayingText').innerText = "🎉 恭喜！所有句子全部播放完畢！";
                            }
                        }
                    });
                }, 500);
            });
        }

        function speakText(text, langCode, voiceObj, rate, callback) {
            let utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = langCode;
            if (voiceObj) utterance.voice = voiceObj;
            utterance.rate = rate;
            
            utterance.onend = () => { if (callback) callback(); };
            utterance.onerror = (e) => { 
                console.error("TTS Error:", e);
                if (callback) callback(); 
            };

            synth.speak(utterance);
        }

        function pauseAudio() {
            isAutoplayActive = false;
            synth.cancel();
            document.getElementById('currentPlayingText').innerText = "已暫停播放";
        }

        function stopAudio() {
            isAutoplayActive = false;
            currentIdx = 0;
            synth.cancel();
            renderList();
            document.getElementById('currentPlayingText').innerText = "已停止播放";
        }

        function nextSentence() {
            if (currentIdx < displaySentences.length - 1) {
                currentIdx++;
                renderList();
                scrollToCurrent();
                playCurrentSentence();
            }
        }

        function prevSentence() {
            if (currentIdx > 0) {
                currentIdx--;
                renderList();
                scrollToCurrent();
                playCurrentSentence();
            }
        }

        function filterSentences() {
            const q = document.getElementById('searchInput').value.toLowerCase().trim();
            displaySentences = rawSentences.filter(s => 
                s.es.toLowerCase().includes(q) || 
                s.en.toLowerCase().includes(q) || 
                s.note.toLowerCase().includes(q) ||
                s.sec.toLowerCase().includes(q)
            );
            currentIdx = 0;
            renderList();
        }

        window.onload = () => {
            renderList();
            initVoices();
        };
    </script>
</body>
</html>
"""

full_html = html_template.replace("__SENTENCES_JSON__", js_sentences_json)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print("index.html 成功生成！包含總句子數：", len(sentences_all))
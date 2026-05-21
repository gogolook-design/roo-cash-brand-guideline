#!/usr/bin/env python3
"""Regenerate the personality blocks and legend rows in concepts.html for the 10x10 matrix.

Reads concepts.html, replaces:
- the personality legend row contents
- the style legend row contents
- every <div class="p-block">…</div> with freshly generated markup for P1..P10

Writes back in place. Idempotent — safe to re-run.
"""
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = ROOT / "concepts.html"

STYLES = [
    ("S1", "寫實 3D",      "Hyperrealistic 3D",       "電影級 CGI 渲染、毛髮細節、柔光，最像實體角色。"),
    ("S2", "扁平向量",     "Flat Vector",              "Brand-safe，介面、文宣最容易直接拿來用。"),
    ("S3", "手繪筆觸",     "Brushy Hand-drawn",       "溫暖、有人味、適合敘事與品牌故事。"),
    ("S4", "純線稿",       "Pure Line Art",            "UI、教學圖示最乾淨，最容易做動態。"),
    ("S5", "水彩",         "Soft Watercolor",          "渲染、暈染的質感，柔軟、慢、有故事感。"),
    ("S6", "凹版印刷",     "Risograph",                "2–3 色疊印、輕微錯位、顆粒紋理，獨立雜誌感。"),
    ("S7", "貼紙風",       "Sticker",                  "粗白邊描邊、扁平鮮色、適合通訊軟體貼圖。"),
    ("S8", "黏土動畫",     "Claymation",               "手捏黏土塑形質感，溫暖手作感最強。"),
    ("S9", "動漫風",       "Anime",                    "日系賽璐璐上色、表情清晰、青年向最易共鳴。"),
    ("S10","像素藝術",     "Pixel Art",                "16-bit 復古遊戲精靈，記憶點與懷舊感最強。"),
]

PERSONALITIES = [
    # (id_num, zh_name, en_name, tagline, age, vibe, strength, risk, voice, visual)
    (1, "鄰家學長", "The Helpful Senior",
     "大你三屆的學長，自己剛搞懂理財，很樂意分享筆記。",
     "25–28 人類等價",
     "親切、實在、略帶書卷氣。不會炫耀，但你問他什麼他都查過。",
     "信任感最強，最適合金融場景的嚴肅性。",
     "可能略顯保守、不夠有記憶點。",
     "「我上次算過喔...」「這個我踩過坑，跟你說...」",
     "中性配色，可能戴細框眼鏡或夾本記事本；姿態收斂、肩膀放鬆。"),
    (2, "精明小幫手", "The Sharp Sidekick",
     "永遠在你口袋裡的小搭檔，眼睛很亮，看到好康會先提醒你。",
     "18–22 人類等價",
     "機靈、好奇、反應快。像哆啦A夢但專管錢。",
     "互動感最強，最適合 app 內 micro-moments（通知、提示、找好康）。",
     "太活潑可能稀釋專業感。",
     "「欸欸這家利率變了！」「你有發現嗎？這月多花了 12%」",
     "眼睛大、表情豐富、姿態前傾；可以加放大鏡、小本子之類道具。"),
    (3, "沉穩守護者", "The Calm Guardian",
     "把你的錢當自己家小孩看的那位。話不多，但你知道他在。",
     "30–35 人類等價",
     "穩重、低調、可靠。袋鼠育兒袋的象徵被放到最大。",
     "最契合「財務安全感」這個品牌承諾。最適合 onboarding、保障、客服等信任場景。",
     "可能太成熟，少了 Roo 該有的親切感與輕巧。",
     "「放心，我幫你看著。」「這筆我幫你記下來了。」",
     "姿態挺拔但不僵硬；表情柔和；色調可能偏深、偏 Trust navy。"),
    (4, "樂觀夥伴", "The Cheerful Buddy",
     "你存到第一桶金時最開心的不是你，是他。",
     "22–26 人類等價",
     "溫暖、樂觀、會慶祝你的每個小進步。情緒給得出來。",
     "最適合里程碑、成就、慶祝時刻。情感連結最強。",
     "在嚴肅理財建議場景可能顯得太輕。",
     "「太可以了！這個月你多存了 NT$1,200！」「沒事的，下個月再來。」",
     "嘴角上揚預設、姿態有彈性、肢體語言開放；Pulse mint 出現頻率高。"),
    (5, "聰明顧問", "The Quietly-Clever Advisor",
     "看起來不多話，但每次開口都剛好點到關鍵。",
     "28–32 人類等價",
     "內斂、有想法、有點「AI brain in a friendly body」的氣質。智識感比 P1 更明顯。",
     "最適合 AI 推薦、分析、比較場景。把「AI 但有溫度」這件事具象化。",
     "可能略顯距離感，需要靠視覺暖化。",
     "「依你最近三個月的花費，我建議...」「這兩家差 0.3%，看你重視什麼。」",
     "姿態冷靜，眼神專注；可能配個微光暈或細節（耳機、平板）暗示 AI；表情克制但不冷。"),
    (6, "嬤嬤的智慧", "The Wise Auntie",
     "阿嬤教過你的事，現在剛好用上。",
     "55–65 人類等價（記憶感）",
     "慈祥、有耐心、看得遠。古早味的智慧加上現代的應用。",
     "最有溫度與歷史感，最適合「世代傳承」「人生階段」場景。",
     "對年輕族群可能略顯距離。",
     "「以前阿嬤都說...」「省下來的就是賺到的。」",
     "編織披肩、小錢包、戴老花眼鏡；色調偏暖、姿態溫和。"),
    (7, "夜市好朋友", "The Night Market Friend",
     "帶你穿小巷子找到真正划算的那個朋友。",
     "23–28 人類等價",
     "接地氣、會殺價、講話直爽。台灣味滿滿。",
     "最有在地感與生活感，最適合「省錢」「優惠」「日常」場景。",
     "可能太隨意，不適合嚴肅理財建議。",
     "「這家便宜啦！」「老闆，這個算我便宜一點！」",
     "T 恤＋棒球帽、手拿珍奶或雞排小道具；表情自信微笑、姿態放鬆。"),
    (8, "數據怪才", "The Data Geek",
     "算給你看的人。看似怪，其實對得很精。",
     "26–30 人類等價",
     "古怪、認真、迷戀數字。有點宅但你信他的算式。",
     "最適合「數據比較」「精算」「報表」場景，差異化記憶點強。",
     "對偏感性的使用者可能不夠親近。",
     "「等等，我算一下喔...」「這個年化報酬 4.2%，比那家高 0.8%。」",
     "厚框眼鏡、計算機、頭髮微亂、姿態前傾在看數字；眼神專注。"),
    (9, "文青夥伴", "The Indie Aesthete",
     "把存錢當美感生活一部分，安靜又有想法的朋友。",
     "24–30 人類等價",
     "內斂、有品味、慢生活。把理財變成一種美學選擇。",
     "最適合「生活方式」「儀式感」「永續理財」場景，差異化最明顯。",
     "可能太小眾，不一定是大眾共鳴點。",
     "「不用多，剛剛好就好。」「這份預算我畫過 mind map 了。」",
     "毛帽＋帆布托特包、手繪筆記本、咖啡杯；姿態安靜、表情若有所思。"),
    (10, "冒險家", "The Money Explorer",
     "把世界當教室、把錢當地圖，邊看邊學的那種人。",
     "27–33 人類等價",
     "好奇、開放、樂於試新東西。理財是探索而非責任。",
     "最適合「投資入門」「理財旅程」「新興市場」場景，敘事感最強。",
     "可能讓保守族群覺得太冒險。",
     "「來試試這個？」「等等，這條路通到哪裡？」",
     "探險夾克、小指南針、地圖捲、背包；姿態前傾、眼神發亮。"),
]


def render_p_legend():
    cards = []
    for (i, zh, en, tagline, age, vibe, strength, risk, voice, visual) in PERSONALITIES:
        cards.append(f'''        <div class="legend-card legend-card--p">
          <span class="legend-badge">P{i}</span>
          <div class="legend-name">{zh}</div>
          <div class="legend-sub">{en}</div>
          <div class="legend-trait">{tagline}</div>
          <div class="legend-fields">
            <div class="legend-field"><span class="legend-field-label">Age Feel 年齡感</span><span class="legend-field-value">{age}</span></div>
            <div class="legend-field"><span class="legend-field-label">Vibe 氣質</span><span class="legend-field-value">{vibe}</span></div>
            <div class="legend-field"><span class="legend-field-label">Strength 優勢</span><span class="legend-field-value">{strength}</span></div>
            <div class="legend-field"><span class="legend-field-label">Risk 風險</span><span class="legend-field-value">{risk}</span></div>
            <div class="legend-field"><span class="legend-field-label">Voice Cues 口頭禪</span><span class="legend-field-value">{voice}</span></div>
            <div class="legend-field"><span class="legend-field-label">Visual Implication 視覺暗示</span><span class="legend-field-value">{visual}</span></div>
          </div>
        </div>''')
    return "\n".join(cards)


def render_s_legend():
    cards = []
    for (sid, zh, en, trait) in STYLES:
        cards.append(f'''        <div class="legend-card">
          <span class="legend-badge">{sid}</span>
          <div class="legend-name">{zh}</div>
          <div class="legend-sub">{en}</div>
          <div class="legend-trait">{trait}</div>
        </div>''')
    return "\n".join(cards)


def render_personality_blocks():
    blocks = []
    for (pid, zh, en, tagline, age, vibe, strength, risk, voice, visual) in PERSONALITIES:
        cells = []
        for (sid, szh, _sen, _strait) in STYLES:
            sn = int(sid[1:])
            path = f"assets/mascot/concepts/p{pid}_s{sn}.png"
            chip = f"{sid} · {szh}"
            coord = f"P{pid}·{sid}"
            cells.append(f'''        <div class="cell"><div class="cell-image"><a href="{path}" target="_blank" rel="noopener"><img src="{path}" alt="P{pid} {szh}" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex';"></a><div class="cell-placeholder" style="display:none;">P{pid} · {sid}</div></div><div class="cell-caption"><span class="chip">{chip}</span><span class="coord">{coord}</span></div></div>''')
        cells_html = "\n".join(cells)
        block = f'''    <!-- ── P{pid} ── -->
    <div class="p-block">
      <div class="p-profile">
        <div class="p-profile-lead">
          <div class="row-num">{pid:02d}</div>
          <div class="p-name">{zh}</div>
          <div class="p-en">P{pid} · {en}</div>
          <p class="p-tagline">{tagline}</p>
        </div>
        <div class="p-profile-meta">
          <div class="p-field"><span class="p-field-label">Age Feel 年齡感</span><span class="p-field-value">{age}</span></div>
          <div class="p-field"><span class="p-field-label">Vibe 氣質</span><span class="p-field-value">{vibe}</span></div>
          <div class="p-field"><span class="p-field-label">Strength 優勢</span><span class="p-field-value">{strength}</span></div>
          <div class="p-field"><span class="p-field-label">Risk 風險</span><span class="p-field-value">{risk}</span></div>
          <div class="p-field"><span class="p-field-label">Voice Cues 口頭禪</span><span class="p-field-value">{voice}</span></div>
          <div class="p-field"><span class="p-field-label">Visual Implication 視覺暗示</span><span class="p-field-value">{visual}</span></div>
        </div>
      </div>
      <div class="p-images">
{cells_html}
      </div>
    </div>'''
        blocks.append(block)
    return "\n\n".join(blocks)


def replace_between(html, start_marker, end_marker, new_inner):
    """Replace text between two markers (markers preserved)."""
    a = html.index(start_marker) + len(start_marker)
    b = html.index(end_marker, a)
    return html[:a] + new_inner + html[b:]


def main():
    html = HTML.read_text()

    # --- Personality legend ---
    p_start = '<div class="legend-title">個性方向 / Personality Directions</div>\n      <div class="legend-row">'
    p_end = '</div>\n    </div>\n\n    <div class="legend-block">'
    html = replace_between(html, p_start, p_end, "\n" + render_p_legend() + "\n      ")

    # --- Style legend ---
    s_start = '<div class="legend-title">視覺風格 / Visual Styles</div>\n      <div class="legend-row">'
    s_end = '</div>\n    </div>\n\n  </div>\n</section>'
    html = replace_between(html, s_start, s_end, "\n" + render_s_legend() + "\n      ")

    # --- Matrix title ---
    html = re.sub(
        r'<div class="legend-title" style="margin-bottom: 32px;">25 個方向 / 5 × 5 Concept Matrix</div>',
        '<div class="legend-title" style="margin-bottom: 32px;">100 個方向 / 10 × 10 Concept Matrix</div>',
        html,
    )

    # --- Header note ---
    html = re.sub(
        r'<span class="header-note">5 個性 <span class="x">×</span> 5 風格 <span class="x">=</span> 25 個方向</span>',
        '<span class="header-note">10 個性 <span class="x">×</span> 10 風格 <span class="x">=</span> 100 個方向</span>',
        html,
    )

    # --- Replace all personality matrix blocks ---
    matrix_start_idx = html.index("<!-- ── P1 ── -->")
    # the matrix ends right before "  </div>\n</section>\n\n<!-- ─── FOOTER"
    matrix_end_marker = "\n  </div>\n</section>\n\n<!-- ─── FOOTER"
    matrix_end_idx = html.index(matrix_end_marker, matrix_start_idx)
    new_blocks = render_personality_blocks()
    html = html[:matrix_start_idx] + new_blocks + "\n" + html[matrix_end_idx:]

    HTML.write_text(html)
    print(f"wrote {HTML}")
    print(f"  - {len(PERSONALITIES)} personalities, {len(STYLES)} styles = {len(PERSONALITIES)*len(STYLES)} cells")


if __name__ == "__main__":
    main()

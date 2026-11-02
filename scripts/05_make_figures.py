"""Chapter figures (print, 300 dpi), rebuilt from the shared data only.

Run scripts 01-04 first. Inputs:
  data/coding/bcause_post_codes.csv, data/coding/bcause_group_scores.csv, data/coding/report_rubric_scores.csv,
  outputs/bcause/{edges,timeline_weekly}.csv, outputs/dr/{cards_by_wording,timeline_30s}.csv,
  outputs/survey/tables/{items,scales}.json
Output: outputs/figures/*.png
Figure names follow the Section 5 rewrite (5-A ... 5-G, later numbered Figures 2-8), plus the DR timeline.
"""
import json, os, datetime as dt
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager
from matplotlib.patches import Rectangle

for f in font_manager.findSystemFonts():
    if 'Inter' in f: font_manager.fontManager.addfont(f)
plt.rcParams.update({'font.family': ['Inter', 'DejaVu Sans'], 'font.size': 8, 'axes.titlesize': 9, 'axes.titleweight': 'semibold',
                     'axes.edgecolor': '#a5a49a', 'axes.linewidth': 0.6, 'xtick.color': '#6d6b67', 'ytick.color': '#383835',
                     'xtick.labelsize': 7.5, 'ytick.labelsize': 7.5, 'savefig.dpi': 300, 'figure.dpi': 100})
INK, INK2, MUTED, GRID = '#20201f', '#383835', '#6d6b67', '#e4e3df'
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREY = '#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#c3c2b7'
SEQ = ['#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5', '#256abf', '#184f95', '#0d366b']
DEB = ['Olympics', 'Parking', 'Housing']
OUT = 'outputs/figures'
os.makedirs(OUT, exist_ok=True)

# ---- group table (as records, NaN -> None)
_g = pd.read_csv('data/coding/bcause_group_scores.csv', keep_default_na=True)
B = [{k: (None if (isinstance(v, float) and np.isnan(v)) else v) for k, v in r.items()} for r in _g.to_dict('records')]
for r in B:
    for k in ('B1', 'B2', 'B3', 'B4', 'B6', 'posts', 'to_facilitator', 'to_other', 'to_own', 'top_level'):
        r[k] = int(r[k])
BY = {r['group']: r for r in B}

# ---- debating-group posts with numeric codes
_p = pd.read_csv('data/coding/bcause_post_codes.csv', keep_default_na=False)
_EN = {'None': 0, 'Generic': 1, 'Specific': 2, 'Integrates': 3}
_PR = {'None': 0, 'Direction': 1, 'Concrete': 2, 'Concrete + actors + conflicts': 3}
_RV = {'Explicit role voice': 'E', 'Role-consistent': 'C', 'Not role-identifiable': 'N', 'Out of role': 'O'}
_AD = {'Facilitator question or post': 'facilitator', 'Another group': 'other group', 'Own group': 'own group',
       'Top level (new position)': 'none'}
P = [dict(debate=r.debate, date=r.date, en=_EN[r.engagement], pr=_PR[r.proposal], rv=_RV[r.role_voice],
          addressee_kind=_AD[r.attached_to]) for r in _p.itertuples() if r.role_voice != 'Facilitator']

# ---- report rubric scores
_r = pd.read_csv('data/coding/report_rubric_scores.csv')
REP = {g: {'R': {k: (int(s), None, None) for k, s in zip(d.criterion, d.score)}} for g, d in _r.groupby('group')}


def ink(hexc):
    c = [int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    L = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    lum = 0.2126 * L[0] + 0.7152 * L[1] + 0.0722 * L[2]
    return 'white' if 1.05 / (lum + 0.05) >= 3.6 else INK


def clean(ax, left=False, bottom=False):
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    if not left: ax.spines['left'].set_visible(False)
    if not bottom: ax.spines['bottom'].set_visible(False)


def save(fig, name):
    fig.savefig(f'{OUT}/{name}.png', bbox_inches='tight', pad_inches=0.08, facecolor='white')
    plt.close(fig)


# ============================================================ 5-A  where posts sat + uptake matrices
def fig_a():
    fig = plt.figure(figsize=(6.6, 7.6))
    gs = fig.add_gridspec(2, 3, height_ratios=[2.25, 1], hspace=0.45, wspace=0.35)
    ax = fig.add_subplot(gs[0, :])
    K = [('to_facilitator', "A facilitator's question or post", BLUE), ('to_other', "Another group's post", ORANGE),
         ('to_own', "Own group's post", AQUA), ('top_level', 'Top level (a new position)', GREY)]
    rows, y, ticks, labels = [], 0, [], []
    for d in DEB:
        rs = sorted([r for r in B if r['debate'] == d and r['kind'] == 'Debating group'], key=lambda r: r['group'])
        n = sum(r['posts'] for r in rs); f = sum(r['to_facilitator'] for r in rs)
        ax.text(-0.005, y - 0.15, f'{d}: {f / n:.0%} of {n} posts sat under a facilitator', transform=ax.get_yaxis_transform(),
                ha='right', va='center', fontsize=8, fontweight='semibold', color=INK)
        y += 1
        for r in rs:
            acc = 0
            for k, _, c in K:
                v = r[k]
                if v:
                    ax.barh(y, v / r['posts'], left=acc / r['posts'], height=0.72, color=c, edgecolor='white', linewidth=1.2)
                    if v / r['posts'] > 0.055:
                        ax.text((acc + v / 2) / r['posts'], y, str(v), ha='center', va='center', fontsize=6.8, color=ink(c))
                    acc += v
            ax.text(1.01, y, f"{r['posts']} posts", va='center', fontsize=7, color=MUTED)
            ticks.append(y); labels.append(f"{r['group']}  {r['role']}"); y += 1
        y += 0.6
    ax.set_yticks(ticks); ax.set_yticklabels(labels, fontsize=7.5, color=INK)
    ax.set_ylim(y - 0.4, -0.9); ax.set_xlim(0, 1)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); ax.tick_params(axis='y', length=0)
    ax.set_xticks([0, .25, .5, .75, 1]); ax.tick_params(axis='x', labelsize=7)
    clean(ax, bottom=True)
    hs = [Rectangle((0, 0), 1, 1, color=c) for _, _, c in K]
    ax.legend(hs, [l for _, l, _ in K], ncol=4, loc='lower left', bbox_to_anchor=(-0.42, 1.0), frameon=False, fontsize=7.2,
              handlelength=1, handleheight=1, columnspacing=1.2)
    ax.set_title('a  What each group’s posts were attached to', loc='left', x=-0.42, y=1.06, fontsize=9)
    # ---------- matrices
    E = pd.read_csv('outputs/bcause/edges.csv').to_dict('records')
    agg = {}
    for e in E:
        a = agg.setdefault((e['debate'], e['from_group'], e['to_group']), [0, 0]); a[0] += e['posts']
        if e['type'] == 'integrates': a[1] += e['posts']
    for j, d in enumerate(DEB):
        axm = fig.add_subplot(gs[1, j])
        gs_ = sorted(r['group'] for r in B if r['debate'] == d and r['kind'] == 'Debating group')
        n = len(gs_)
        for i, g in enumerate(gs_):
            for k, h in enumerate(gs_):
                if i == k:
                    axm.plot([k + .2, k + .8], [i + .8, i + .2], color=GRID, lw=0.8); continue
                a = agg.get((d, g, h))
                if a:
                    c = SEQ[min(a[0], 5)]
                    axm.add_patch(Rectangle((k + .05, i + .05), .9, .9, color=c))
                    axm.text(k + .5, i + .52, str(a[0]), ha='center', va='center', fontsize=7, color=ink(c))
                    if a[1]: axm.add_patch(Rectangle((k + .14, i + .14), .72, .72, fill=False, ec=ink(c), lw=1.1))
                else:
                    axm.add_patch(Rectangle((k + .05, i + .05), .9, .9, fill=False, ec=GRID, lw=0.7))
        axm.set_xlim(0, n); axm.set_ylim(n, 0); axm.set_aspect('equal')
        axm.set_xticks([k + .5 for k in range(n)]); axm.set_xticklabels(gs_, fontsize=6.6)
        axm.set_yticks([k + .5 for k in range(n)]); axm.set_yticklabels(gs_, fontsize=6.6)
        axm.xaxis.tick_top(); axm.tick_params(length=0); clean(axm)
        axm.set_title(d, fontsize=8, pad=16)
    fig.text(0.125, 0.355, 'b  Who took up whose argument', fontsize=9, fontweight='semibold', color=INK)
    fig.text(0.125, 0.341, 'Rows: group posting. Columns: group whose specific argument the post takes up. '
                           'Outlined: includes a post that integrates the point.', fontsize=7, color=MUTED)
    save(fig, 'fig5A_threads_and_uptake')


# ============================================================ 5-B  timelines with facilitator activity and AI events
def fig_b():
    T = pd.read_csv('outputs/bcause/timeline_weekly.csv').to_dict('records')
    fig, axs = plt.subplots(3, 1, figsize=(6.6, 5.2), sharex=True, sharey=True, gridspec_kw={'hspace': 0.42})
    ymax = max(r['posts'] for r in T)
    D = lambda s: dt.datetime.fromisoformat(s)
    fac = {'Olympics': ('G01', '2026-04-25'), 'Parking': ('G16', '2026-04-20'), 'Housing': ('G14', '2026-06-02')}
    cd = {'Housing': '2026-05-16', 'Parking': '2026-05-20'}
    for ax, d in zip(axs, DEB):
        rs = [r for r in T if r['debate'] == d]
        x = [D(r['week_start']) + dt.timedelta(days=3.5) for r in rs]
        gp = [r['group_posts'] for r in rs]; fp = [r['facilitator_posts'] for r in rs]
        ax.bar(x, gp, width=5.2, color=GREY, edgecolor='white', linewidth=0.6, label="Debating groups' posts")
        ax.bar(x, fp, width=5.2, bottom=gp, color=BLUE, edgecolor='white', linewidth=0.6, label="Facilitators' posts")
        ax.axvline(D('2026-05-04'), color=INK, lw=1, ls=(0, (4, 2)))
        ax.axvline(D('2026-05-18'), color=MUTED, lw=0.8, ls=(0, (1, 2)))
        g, last = fac[d]
        ax.annotate(f'last {g} post\n{D(last):%-d %b}', xy=(D(last), 0), xytext=(D(last), ymax * {'Olympics': 0.82, 'Parking': 0.5, 'Housing': 0.64}[d]), fontsize=6.6,
                    color=BLUE, ha='center', arrowprops=dict(arrowstyle='-', color=BLUE, lw=0.7))
        if d in cd:
            ax.plot([D(cd[d])], [ymax * 1.02], marker='v', color=ORANGE, ms=5, clip_on=False)
            ax.text(D(cd[d]) + dt.timedelta(days=1.5), ymax * 1.0, f'conflict detection run, {D(cd[d]):%-d %b}', fontsize=6.6, color=ORANGE, va='center')
        if d == 'Parking':
            ax.plot([D('2026-03-30')], [ymax * 1.02], marker='v', color=MAGENTA, ms=5, clip_on=False)
            ax.text(D('2026-03-30') + dt.timedelta(days=1.5), ymax * 1.0, 'AI synopsis last updated, 30 Mar', fontsize=6.6, color='#c24f7d', va='center')
        n_g, n_f = sum(gp), sum(fp)
        ax.set_title(f'{d}  ({n_g} group posts, {n_f} facilitator posts)', loc='left', fontsize=8)
        ax.set_ylim(0, ymax * 1.08); ax.yaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
        clean(ax, bottom=True); ax.tick_params(axis='y', length=0)
    axs[0].text(D('2026-05-04') + dt.timedelta(days=1), ymax * 0.98, 'live session\n4 May', fontsize=6.6, color=INK, va='top')
    axs[0].text(D('2026-05-18') + dt.timedelta(days=1), ymax * 0.98, 'planned close\n18 May', fontsize=6.6, color=MUTED, va='top')
    axs[-1].xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=2))
    axs[-1].xaxis.set_major_formatter(mdates.DateFormatter('%-d %b'))
    axs[-1].set_xlim(D('2026-03-14'), D('2026-06-22'))
    axs[1].set_ylabel('Posts per week', fontsize=7.5, color=MUTED)
    axs[0].legend(loc='upper right', bbox_to_anchor=(1.0, 1.55), ncol=2, frameon=False, fontsize=7, handlelength=1)
    save(fig, 'fig5B_timelines')


# ============================================================ 5-C  reaction cards with how groups read them
_w = pd.read_csv('outputs/dr/cards_by_wording.csv')
CARDS = {}
for t in DEB:
    d = _w[_w.topic == t]
    CARDS[t] = [(dim, a.wording.iloc[0], int(a.cards.iloc[0]), b.wording.iloc[0], int(b.cards.iloc[0]))
                for (k, dim), g in d.groupby(['dimension_no', 'dimension']) for a, b in [(g[g.side == 1], g[g.side == 2])]]
NOTES = {('Olympics', 'Trust', 'R'): 'G06: distrust of official rhetoric is shared across roles → turn to multi-source evidence',
         ('Olympics', 'Resonance', 'L'): 'G11: emotional examples persuade more than statistics → turn to narrative',
         ('Parking', 'Solutions', 'R'): 'G07: support for enforcement.  G16, G17: rejection of solutions (card sat on the side the dashboard labelled negative).  G03: attributed to BCause'}


def fig_c():
    fig, axs = plt.subplots(3, 1, figsize=(6.6, 8.0), gridspec_kw={'hspace': 0.75})
    for ax, d in zip(axs, DEB):
        rows = CARDS[d]; tot = sum(a + b for _, _, a, _, b in rows)
        notes = []
        for i, (cat, l, a, r, b) in enumerate(rows):
            ax.barh(i, -a, color=BLUE, height=0.62); ax.barh(i, b, color=ORANGE, height=0.62)
            ax.text(-a - 2, i, f'{l}  {a}', ha='right', va='center', fontsize=6.8, color=INK)
            ax.text(b + 2, i, f'{b}  {r}', ha='left', va='center', fontsize=6.8, color=INK)
            ax.text(-0.01, i, cat, transform=ax.get_yaxis_transform(), ha='right', va='center', fontsize=6.6, color=MUTED)
            for side in ('L', 'R'):
                note = NOTES.get((d, cat, side))
                if note:
                    notes.append(note); k = len(notes)
                    x0 = -a - 1 if side == 'L' else b + 1
                    ax.text(x0 + (-1 if side == 'L' else 1) * 0, i - 0.42, f'[{k}]', ha='center', va='bottom', fontsize=6.2,
                            color='#b07800', fontweight='bold')
        ax.axvline(0, color=INK, lw=0.8)
        ax.set_xlim(-220, 175); ax.set_ylim(len(rows) - 0.4, -0.8)
        ax.set_yticks([]); ax.set_xticks([]); clean(ax)
        ax.set_title(f'{d}  ({tot} cards)', loc='left', fontsize=8, x=-0.16)
        for k, n in enumerate(notes, 1):
            ax.text(-0.16, -0.06 - 0.13 * (k - 1), f'[{k}] {n}', transform=ax.transAxes, ha='left', va='top',
                    fontsize=6.3, color=INK2, wrap=True)
    axs[0].text(-90, -1.45, 'first card of each pair', ha='center', fontsize=6.8, color=BLUE)
    axs[0].text(85, -1.45, 'second card (shown as negative on the dashboard)', ha='center', fontsize=6.8, color='#c2521f')
    save(fig, 'fig5C_cards_and_readings')


# ============================================================ 5-D  before vs after the live session
def fig_d():
    cut = '2026-05-04'
    IND = [('Takes up another group’s argument', lambda p: p['en'] >= 2), ('Attached to another group’s post', lambda p: p['addressee_kind'] == 'other group'),
           ('Integrates another group’s point', lambda p: p['en'] == 3), ('Concrete proposal', lambda p: p['pr'] >= 2),
           ('Explicit role voice', lambda p: p['rv'] == 'E')]
    fig, axs = plt.subplots(1, 4, figsize=(6.6, 2.9), sharey=True, gridspec_kw={'wspace': 0.12})
    for ax, d in zip(axs, ['All'] + DEB):
        ps = [p for p in P if d == 'All' or p['debate'] == d]
        b = [p for p in ps if p['date'] < cut]; a = [p for p in ps if p['date'] >= cut]
        for i, (lab, f) in enumerate(IND):
            vb = np.mean([f(p) for p in b]); va = np.mean([f(p) for p in a])
            col = BLUE if va > vb + 0.02 else ORANGE if va < vb - 0.02 else MUTED
            ax.plot([vb, va], [i, i], color=col, lw=1.6, solid_capstyle='round', zorder=1)
            ax.scatter([vb], [i], s=26, facecolor='white', edgecolor=INK2, lw=1, zorder=2)
            ax.scatter([va], [i], s=26, color=col, zorder=3)
        ax.set_xlim(-0.03, 1.0); ax.set_xticks([0, .5, 1]); ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
        ax.xaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
        ax.set_title(f'{d}\n{len(b)} before · {len(a)} after', fontsize=7.6)
        clean(ax, bottom=True); ax.tick_params(axis='y', length=0)
    axs[0].set_yticks(range(len(IND))); axs[0].set_yticklabels([l for l, _ in IND], fontsize=7.3, color=INK)
    axs[0].set_ylim(len(IND) - 0.5, -0.6)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker='o', ls='', mfc='white', mec=INK2, label='Before 4 May'),
         Line2D([], [], marker='o', ls='', color=BLUE, label='After, higher'),
         Line2D([], [], marker='o', ls='', color=ORANGE, label='After, lower'),
         Line2D([], [], marker='o', ls='', color=MUTED, label='After, within 2 points')]
    fig.legend(handles=h, loc='lower center', ncol=4, frameon=False, fontsize=7, bbox_to_anchor=(0.55, -0.08))
    save(fig, 'fig5D_before_after')


# ============================================================ 5-E  evidence and proposals by group
def fig_e():
    M = [('evidence_share', 'Facts or cases'), ('sourced_share', 'Names a traceable source'), ('counter_share', 'Answers a counter-view'),
         ('concrete_share', 'Concrete proposal')]
    rs = []
    for d in DEB:
        rs += sorted([r for r in B if r['debate'] == d and r['kind'] == 'Debating group'], key=lambda r: r['group'])
    fig, axs = plt.subplots(1, 4, figsize=(6.6, 4.2), sharey=True, gridspec_kw={'wspace': 0.1})
    ypos, y, last = [], 0, None
    for r in rs:
        if last and r['debate'] != last: y += 0.7
        ypos.append(y); y += 1; last = r['debate']
    cols = {'Olympics': BLUE, 'Parking': ORANGE, 'Housing': AQUA}
    for ax, (k, lab) in zip(axs, M):
        for r, yy in zip(rs, ypos):
            ax.barh(yy, r[k], color=cols[r['debate']], height=0.68)
            ax.text(r[k] + 0.03, yy, f'{r[k]:.0%}', va='center', fontsize=6.4, color=MUTED)
        ax.set_xlim(0, 1.18); ax.set_xticks([0, .5, 1]); ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
        ax.set_title(lab, fontsize=7.6); ax.xaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
        clean(ax, bottom=True); ax.tick_params(axis='y', length=0)
    axs[0].set_yticks(ypos); axs[0].set_yticklabels([f"{r['group']}  {r['role']}  ({r['posts']})" for r in rs], fontsize=7, color=INK)
    axs[0].set_ylim(y - 0.3, -0.7)
    h = [Rectangle((0, 0), 1, 1, color=cols[d]) for d in DEB]
    fig.legend(h, DEB, loc='lower center', ncol=3, frameon=False, fontsize=7, bbox_to_anchor=(0.6, -0.04), handlelength=1)
    save(fig, 'fig5E_evidence_by_group')


# ============================================================ 5-F  reports vs platform
def fig_f():
    rows = []
    for d in DEB:
        rows += sorted([r for r in B if r['debate'] == d], key=lambda r: (r['kind'] != 'Facilitators', r['group']))
    fig = plt.figure(figsize=(6.6, 5.0))
    gs = fig.add_gridspec(1, 3, width_ratios=[6, 6, 4.6], wspace=0.08)
    axr, axp, axt = fig.add_subplot(gs[0]), fig.add_subplot(gs[1]), fig.add_subplot(gs[2])
    SC = [SEQ[0], SEQ[2], SEQ[4], SEQ[6]]
    ylabels = []
    for i, r in enumerate(rows):
        f = r['kind'] == 'Facilitators'
        ylabels.append(f"{r['group']}{'  (F)' if f else ''}")
        for j, c in enumerate('123456'):
            rep = REP.get(r['group'])
            v = rep['R'][f'R{c}'][0] if rep else None
            if v is None:
                axr.add_patch(Rectangle((j + .06, i + .06), .88, .88, fill=False, ec=GRID, lw=0.6))
                if j == 0: axr.text(3, i + .5, 'no report', ha='center', va='center', fontsize=6.5, color=MUTED)
            else:
                axr.add_patch(Rectangle((j + .06, i + .06), .88, .88, color=SC[v])); axr.text(j + .5, i + .55, v, ha='center', va='center', fontsize=6.6, color=ink(SC[v]))
            if c == '5':
                axp.add_patch(Rectangle((j + .06, i + .06), .88, .88, fill=False, ec='#a5a49a', lw=0.6, ls=(0, (2, 2))))
            else:
                v = r['B' + c]
                axp.add_patch(Rectangle((j + .06, i + .06), .88, .88, color=SC[v])); axp.text(j + .5, i + .55, v, ha='center', va='center', fontsize=6.6, color=ink(SC[v]))
    for ax, t in ((axr, 'a  Report rubric'), (axp, 'b  Same rubric applied to posts')):
        ax.set_xlim(0, 6); ax.set_ylim(len(rows), 0); ax.set_xticks([k + .5 for k in range(6)]); ax.set_xticklabels([f'C{k}' for k in range(1, 7)], fontsize=7)
        ax.xaxis.tick_top(); ax.tick_params(length=0); clean(ax); ax.set_title(t, loc='left', fontsize=8, pad=14)
    axr.set_yticks([k + .5 for k in range(len(rows))]); axr.set_yticklabels(ylabels, fontsize=7, color=INK)
    axp.set_yticks([])
    # totals (debating groups with both)
    dg = [r for r in rows if r['kind'] == 'Debating group' and r['R_total'] is not None]
    for i, r in enumerate(rows):
        if r in dg:
            a, b = r['R_total'], r['B_total']
            axt.plot([a, b], [i + .5, i + .5], color='#a5a49a', lw=1.4, zorder=1)
            axt.scatter([a], [i + .5], s=22, facecolor='white', edgecolor=INK2, lw=1, zorder=2)
            axt.scatter([b], [i + .5], s=22, color=BLUE, zorder=3)
    axt.set_ylim(len(rows), 0); axt.set_xlim(5.5, 15.5); axt.set_yticks([]); axt.set_xticks([6, 9, 12, 15])
    axt.xaxis.tick_top(); axt.xaxis.grid(True, color=GRID, lw=0.6); axt.set_axisbelow(True); clean(axt); axt.tick_params(length=0)
    axt.set_title('c  Totals (C1–C4, C6), debating groups', loc='left', fontsize=8, pad=14)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker='o', ls='', mfc='white', mec=INK2, label='Report'), Line2D([], [], marker='o', ls='', color=BLUE, label='Platform')]
    axt.legend(handles=h, loc='upper right', frameon=False, fontsize=6.8, bbox_to_anchor=(1.02, -0.01), ncol=2)
    hs = [Rectangle((0, 0), 1, 1, color=c) for c in SC]
    fig.legend(hs, ['0', '1', '2', '3'], title='Score', title_fontsize=7, loc='lower left', ncol=4, frameon=False, fontsize=7,
               bbox_to_anchor=(0.12, -0.03), handlelength=1)
    fig.text(0.5, 0.005, 'C5 (reflection on the tools) has no equivalent in posts (dashed). (F): facilitator group, scored on the facilitation version of each criterion.',
             fontsize=6.6, color=MUTED, ha='left')
    save(fig, 'fig5F_reports_vs_platform')


# ============================================================ 5-G  survey
def fig_g():
    IT = json.load(open('outputs/survey/tables/items.json')); SC_ = json.load(open('outputs/survey/tables/scales.json'))
    fig = plt.figure(figsize=(6.6, 3.9))
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 1.45], hspace=0.75)
    ax = fig.add_subplot(gs[0])
    TXT = {'OV1': 'The assignment improved my learning in the module', 'OV2': 'Deliberating with the tools changed how I think about planning',
           'OV3': 'I feel more confident with real planning challenges'}
    C5 = ['#b93535', '#f4abab', '#e4e3df', '#9ec5f4', '#256abf']
    rows = [r for r in IT if r['code'] in TXT and r['sample'] == 'Students (latest)']
    for i, r in enumerate(rows):
        n = r['n']; x0 = -(r['d1'] + r['d2'] + r['d3'] / 2) / n
        for k, c in zip(('d1', 'd2', 'd3', 'd4', 'd5'), C5):
            v = r[k] / n
            if v:
                ax.barh(i, v, left=x0, color=c, height=0.62, edgecolor='white', lw=0.8)
                if v > 0.08: ax.text(x0 + v / 2, i, r[k], ha='center', va='center', fontsize=6.6, color=ink(c))
            x0 += v
        ax.text(0.80, i, f"{r['pct_agree']:.0f}% agree", va='center', fontsize=7, color=INK)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([f"{r['code']}  {TXT[r['code']]}" for r in rows], fontsize=7.2, color=INK)
    ax.set_ylim(len(rows) - 0.5, -0.6); ax.set_xlim(-0.6, 0.98); ax.axvline(0, color=INK, lw=0.6)
    ax.set_xticks([-.5, -.25, 0, .25, .5]); ax.set_xticklabels(['50%', '25%', '0', '25%', '50%'])
    clean(ax, bottom=True); ax.tick_params(axis='y', length=0)
    ax.set_title('a  Agreement, each of the 42 students counted once (latest answer)', loc='left', fontsize=8, x=-0.62)
    hs = [Rectangle((0, 0), 1, 1, color=c) for c in C5]
    ax.legend(hs, ['Not at all true', 'Slightly', 'Moderately', 'Mostly', 'Very true'], ncol=5, frameon=False, fontsize=6.6,
              loc='upper left', bbox_to_anchor=(-0.62, -0.28), handlelength=1, columnspacing=1)
    ax2 = fig.add_subplot(gs[1])
    order = ['OV', 'SR', 'CT', 'AC', 'DEEP', 'LG', 'SURF']
    rs = [next(r for r in SC_ if r['scale'] == s) for s in order]
    for i, r in enumerate(rs):
        sig = r['holm_p'] < 0.05
        col = BLUE if sig else '#a5a49a'
        ax2.plot([r['ci_lo'], r['ci_hi']], [i, i], color=col, lw=1.6, solid_capstyle='round')
        ax2.scatter([r['diff']], [i], s=26, color=col, zorder=3)
        ax2.text(1.12, i, f"+{r['diff']:.2f}" if r['diff'] >= 0 else f"{r['diff']:.2f}", va='center', fontsize=6.8, color=INK, ha='right')
        hp = r['holm_p']; ax2.text(1.45, i, ('< .001' if hp < 0.001 else f'{hp:.3f}'.lstrip('0') if hp < .1 else f'{hp:.2f}'.lstrip('0')), va='center', ha='right', fontsize=6.8, color=INK if sig else MUTED)
    ax2.text(1.12, -0.95, 'change', ha='right', fontsize=6.6, color=MUTED); ax2.text(1.45, -0.95, 'Holm p', ha='right', fontsize=6.6, color=MUTED)
    ax2.axvline(0, color=INK, lw=0.6)
    ax2.set_yticks(range(len(rs))); ax2.set_yticklabels([r['label'] for r in rs], fontsize=7.2, color=INK)
    ax2.set_ylim(len(rs) - 0.5, -0.6); ax2.set_xlim(-0.5, 1.5); ax2.set_xticks([-.5, 0, .5, 1])
    ax2.xaxis.grid(True, color=GRID, lw=0.6); ax2.set_axisbelow(True); clean(ax2, bottom=True); ax2.tick_params(axis='y', length=0)
    ax2.set_title('b  Change from May to June among the 13 students who answered twice (mean, 95% CI; 1–5 scale)', loc='left', fontsize=8, x=-0.29)
    save(fig, 'fig5G_survey')


# ============================================================ DR  cards per 30 seconds of video
def fig_dr_timeline():
    T = pd.read_csv('outputs/dr/timeline_30s.csv', index_col=0)
    fig, ax = plt.subplots(figsize=(6.6, 2.6))
    for t, c in zip(['Olympics', 'Housing', 'Parking'], [BLUE, AQUA, ORANGE]):
        ax.plot(T.index / 60, T[t], color=c, lw=1.6, label=f'{t} ({int(T[t].sum())} cards)')
    ax.set_xlabel('Minutes of video', fontsize=7.5, color=MUTED); ax.set_ylabel('Cards per 30 s', fontsize=7.5, color=MUTED)
    ax.yaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True); clean(ax, left=False, bottom=True)
    ax.legend(frameon=False, fontsize=7, loc='upper right')
    save(fig, 'figDR_cards_timeline')


if __name__ == '__main__':
    for f in (fig_a, fig_b, fig_c, fig_d, fig_e, fig_f, fig_g, fig_dr_timeline):
        f(); print('done', f.__name__)

import { generateHTML } from '@tiptap/core'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import { TextStyle } from '@tiptap/extension-text-style'
import { FontFamily } from '@tiptap/extension-font-family'
import { TextAlign } from '@tiptap/extension-text-align'
import { Table } from '@tiptap/extension-table'
import { TableRow } from '@tiptap/extension-table-row'
import { TableCell } from '@tiptap/extension-table-cell'
import { TableHeader } from '@tiptap/extension-table-header'
import { Extension } from '@tiptap/core'

const FontSize = Extension.create({
  name: 'fontSize',
  addOptions() { return { types: ['textStyle'] } },
  addGlobalAttributes() {
    return [{
      types: this.options.types,
      attributes: {
        fontSize: {
          default: null,
          parseHTML: el => el.style.fontSize?.replace('px', '') || null,
          renderHTML: a => a.fontSize ? { style: `font-size:${a.fontSize}px` } : {},
        }
      }
    }]
  },
  addCommands() {
    return {
      setFontSize:   size => ({ chain }) => chain().setMark('textStyle', { fontSize: String(size) }).run(),
      unsetFontSize: ()   => ({ chain }) => chain().setMark('textStyle', { fontSize: null }).removeEmptyTextStyle().run(),
    }
  }
})

const TIPTAP_EXTENSIONS = [
  StarterKit, Underline, TextStyle, FontFamily, FontSize,
  TextAlign.configure({ types: ['heading', 'paragraph'] }),
  Table.configure({ resizable: false }),
  TableRow, TableHeader, TableCell,
]

function tiptapToHtml(raw) {
  if (!raw) return '<p class="empty-note">No content recorded.</p>'
  try {
    const doc = typeof raw === 'string' ? JSON.parse(raw) : raw
    if (!doc || !doc.type) return '<p class="empty-note">No content recorded.</p>'
    return generateHTML(doc, TIPTAP_EXTENSIONS)
  } catch {
    return '<p class="empty-note">Content could not be rendered.</p>'
  }
}

// ── Bengali helpers ────────────────────────────────────────────────────────────

const BN_DIGITS = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯']

function toBn(n) {
  return String(n).replace(/[0-9]/g, d => BN_DIGITS[parseInt(d)])
}

function formatDateBn(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const day   = String(d.getUTCDate()).padStart(2, '0')
  const month = String(d.getUTCMonth() + 1).padStart(2, '0')
  const year  = d.getUTCFullYear()
  return `${toBn(day)}-${toBn(month)}-${toBn(year)}`
}

function councilTypeBn(isAcademic) {
  return isAcademic ? 'একাডেমিক কাউন্সিল' : 'সিন্ডিকেট'
}

// ── Member grouping ────────────────────────────────────────────────────────────

// "অধ্যাপক ডঃ X, প্রধান, কেমিকৌশল বিভাগ" → last segment = "কেমিকৌশল বিভাগ"
function extractGroupKey(content) {
  if (!content) return 'অন্যান্য'
  const parts = content.split(',')
  return parts[parts.length - 1].trim().replace(/।\s*$/, '') || 'অন্যান্য'
}

// Returns { name, designation }
// name        = first comma segment
// designation = middle segments (between first and last) joined — shown on 2nd line
// last segment (dept/institution) is excluded — it's already the section heading
function parseContent(content) {
  if (!content) return { name: '', designation: '' }
  const parts = content.split(',').map(s => s.trim().replace(/।\s*$/, ''))
  if (parts.length <= 1) return { name: parts[0] || '', designation: '' }
  const name = parts[0]
  const designation = parts.slice(1, -1).join(', ')
  return { name, designation }
}

// উপাচার্য / উপ-উপাচার্য type members go at the top, not in dept groups
// ── Member type detection from Bengali content ────────────────────────────────

function isViceChancellor(m) {
  return (
    m.content?.includes('উপাচার্য') &&
    !m.content?.includes('উপ-উপাচার্য')
  )
}

function isProViceChancellor(m) {
  return m.content?.includes('উপ-উপাচার্য')
}

function isDean(m) {
  return m.content?.includes('ডীন')
}

function isHead(m) {
  return (
    m.content?.includes('বিভাগীয় প্রধান') ||
    m.content?.includes('বিভাগের প্রধান') ||
    m.content?.includes('চেয়ারম্যান') ||
    m.content?.includes('প্রধান')
  )
}

// VC / Pro-VC members shown separately
function isAdminMember(m) {
  return isViceChancellor(m) || isProViceChancellor(m)
}

function groupMembers(members, presidentCardId) {
  const president =
    members.find(m => String(m.id) === String(presidentCardId)) || null

  const rest = members.filter(
    m => String(m.id) !== String(presidentCardId)
  )

  // Group members by designation found in Bengali content
  const adminMembers = rest.filter(m => isAdminMember(m))

  const deans = rest.filter(
    m => isDean(m) &&
         !isAdminMember(m)
  )

  const heads = rest.filter(
    m =>
      isHead(m) &&
      !isDean(m) &&
      !isAdminMember(m)
  )

  const regulars = rest.filter(
    m =>
      !isAdminMember(m) &&
      !isDean(m) &&
      !isHead(m)
  )

  // Regular members grouped by department
  const regDeptMap = {}

  regulars.forEach(m => {
    const dName =
      m.department?.name_bangla ||
      extractGroupKey(m.content)

    const fOrder =
      m.department?.faculty?.order ?? 999

    if (!regDeptMap[dName]) {
      regDeptMap[dName] = {
        order: fOrder,
        members: []
      }
    }

    regDeptMap[dName].members.push(m)
  })

  const regularsByDept = Object.entries(regDeptMap)
    .sort((a, b) => a[1].order - b[1].order)

  return {
    president,
    adminMembers,
    deans,
    heads,
    regularsByDept,
  }
}

// ── Members HTML ───────────────────────────────────────────────────────────────

function buildMembersHtml(members, presidentCardId) {
  if (!members || !members.length) {
    return '<p class="empty-note">কোনো সদস্য তালিকাভুক্ত নেই।</p>'
  }

  const { president, adminMembers, deans, heads, regularsByDept } =
    groupMembers(members, presidentCardId)

  let serial = 0
  const rows = []

  // includeLast: for deans/heads, include the last segment (dept/faculty) in designation
  function row(member, roleLabel, { includeLast = false } = {}) {
    serial++
    const parts = (member.content || '').split(',').map(s => s.trim().replace(/।\s*$/, ''))
    const name = parts[0] || ''
    const desigParts = includeLast ? parts.slice(1) : parts.slice(1, -1)
    // Remove any segment that duplicates the role already shown in the right column
    const designation = desigParts.filter(p => p !== roleLabel).join(', ')
    const nameHtml = designation
      ? `${name}<br><span class="desig">${designation}</span>`
      : name
    rows.push(`
      <tr>
        <td class="ser">${toBn(serial)}।</td>
        <td class="mname">${nameHtml}</td>
        <td class="mrole">${roleLabel}</td>
      </tr>`)
  }

  function groupHeading(title) {
    rows.push(`
      <tr class="grp-head">
        <td colspan="3"><span class="grp-title">${title}</span></td>
      </tr>`)
  }

  function deptHeading(title) {
    rows.push(`
      <tr class="dept-head">
        <td colspan="3"><span class="dept-title">${title}</span></td>
      </tr>`)
  }

  // 1. President
  if (president) {
    groupHeading('সভাপতি')
    row(president, 'সভাপতি')
  }

  // 2. উপাচার্য / উপ-উপাচার্য — listed right after president, no section heading
  adminMembers.forEach(m => row(m, 'সদস্য'))

  // 3. All Deans — show "ডীন, [faculty]" under name
  if (deans.length) {
    groupHeading('সকল ডীন')
    deans.forEach(m => row(m, 'সদস্য', { includeLast: true }))
  }

  // 4. All Heads — show "প্রধান, [dept]" under name, no dept sub-headings
  if (heads.length) {
    groupHeading('সকল বিভাগীয় প্রধান')
    heads.forEach(m => row(m, 'সদস্য', { includeLast: true }))
  }

  // 5. Regular members — one dept heading per group, members listed under it
  regularsByDept.forEach(([dName, dData]) => {
    deptHeading(dName)
    dData.members.forEach(m => row(m, 'সদস্য'))
  })

  return `
    <table class="members-tbl">
      <colgroup>
        <col style="width:4%">
        <col style="width:78%">
        <col style="width:18%">
      </colgroup>
      ${rows.join('')}
    </table>`
}

// ── Agenda blocks ──────────────────────────────────────────────────────────────

function agendaBlocks(items, isSuppl) {
  if (!items.length) return '<p class="empty-note">কোনো প্রস্তাব নেই।</p>'
  return items.map((ag, i) => `
    <div class="agenda-block${isSuppl ? ' suppl' : ''}">
      <p class="agenda-label">প্রস্তাব নং ${toBn(i + 1)}${isSuppl ? ' (অতিরিক্ত)' : ''}</p>
      <div class="agenda-body">${tiptapToHtml(ag.body)}</div>
      ${ag.resolution ? `
        <div class="resolution-block">
          <p class="resolution-label">সিদ্ধান্ত ঃ</p>
          <div class="agenda-body">${tiptapToHtml(ag.resolution.body)}</div>
        </div>` : ''}
    </div>
  `).join('')
}

// ── Full page ──────────────────────────────────────────────────────────────────

function buildFullPage({ meeting, members, agendas }) {
  const councilBn     = councilTypeBn(meeting.is_academic)
  const dateBn        = formatDateBn(meeting.meeting_date)
  const serialBn      = toBn(meeting.serial_num)
  const regularAgendas = agendas.filter(a => !a.is_supplementary).sort((a, b) => a.serial - b.serial)
  const supplAgendas   = agendas.filter(a => a.is_supplementary).sort((a, b) => a.serial - b.serial)

  const membersHtml = buildMembersHtml(members, meeting.president_card_id)

  return `<!DOCTYPE html>
<html lang="bn">
<head>
  <meta charset="utf-8">
  <title>${councilBn} — ${serialBn}-তম সভা</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+Bengali:wght@400;600;700;900&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    @page { size: A4; margin: 20mm 22mm 20mm 22mm; }

    body {
      font-family: 'Noto Serif Bengali', 'Kalpurush', 'SolaimanLipi', serif;
      font-size: 11pt;
      color: #000;
      line-height: 1.7;
      background: #fff;
    }

    /* ── University header ── */
    .univ-header {
      text-align: center;
      margin-bottom: 4px;
    }
    .univ-name {
      font-size: 18pt;
      font-weight: 900;
      line-height: 1.3;
    }
    .meeting-subtitle {
      font-size: 12pt;
      font-weight: 700;
      text-decoration: underline;
      margin-top: 6px;
      line-height: 1.5;
    }

    /* ── Divider ── */
    hr.section-rule {
      border: none;
      border-top: 1.5px solid #000;
      margin: 12px 0;
    }

    /* ── Opening paragraph ── */
    .opening-para {
      font-size: 11pt;
      text-align: justify;
      margin-bottom: 14px;
      line-height: 1.8;
    }

    /* ── Members section ── */
    .members-heading {
      font-size: 12pt;
      font-weight: 700;
      text-decoration: underline;
      margin-bottom: 10px;
    }

    .members-tbl {
      width: 100%;
      border-collapse: collapse;
      font-size: 10.5pt;
      margin-bottom: 16px;
    }
    .members-tbl td { padding: 1px 4px; vertical-align: top; }
    .members-tbl .ser   { white-space: nowrap; width: 4%; }
    .members-tbl .mname { width: 78%; }
    .members-tbl .mrole { text-align: right; width: 18%; white-space: nowrap; }

    /* Group / faculty / dept headings */
    .grp-head td {
      padding-top: 10px;
      padding-bottom: 2px;
    }
    .fac-head td {
      padding-top: 14px;
      padding-bottom: 3px;
    }
    .dept-head td {
      padding-top: 6px;
      padding-bottom: 2px;
    }
    .grp-title {
      font-size: 11pt;
      font-weight: 700;
      text-decoration: underline;
    }
    .dept-title {
      font-size: 10.5pt;
      font-weight: 700;
      text-decoration: underline;
      padding-left: 4px;
    }
    .desig {
      font-size: 9.5pt;
      color: #333;
      font-weight: 400;
    }

    /* ── Agenda section ── */
    .agendas-heading {
      font-size: 12pt;
      font-weight: 700;
      text-decoration: underline;
      margin: 18px 0 10px;
    }
    .agenda-block {
      border-left: 3px solid #1e40af;
      padding-left: 12px;
      margin-bottom: 16px;
      page-break-inside: avoid;
    }
    .agenda-block.suppl { border-left-color: #b45309; }

    .agenda-label {
      font-weight: 700;
      font-size: 11pt;
      margin-bottom: 4px;
    }
    .agenda-block.suppl .agenda-label { color: #92400e; }

    .agenda-body { font-size: 10.5pt; }
    .agenda-body p { margin: 0 0 4px; }
    .agenda-body ul, .agenda-body ol { padding-left: 18px; }
    .agenda-body table { border-collapse: collapse; width: 100%; }
    .agenda-body td, .agenda-body th { border: 1px solid #999; padding: 3px 7px; }

    .resolution-block {
      margin-top: 10px;
      padding-left: 10px;
      border-left: 3px solid #065f46;
    }
    .resolution-label {
      font-weight: 700;
      font-size: 10.5pt;
      margin-bottom: 3px;
    }

    .rich-content { font-size: 10.5pt; }
    .rich-content p { margin: 0 0 5px; }
    .rich-content ul, .rich-content ol { padding-left: 18px; }
    .rich-content table { border-collapse: collapse; width: 100%; }
    .rich-content td, .rich-content th { border: 1px solid #999; padding: 3px 7px; }

    .empty-note { color: #888; font-style: italic; }
    .section-gap { margin-top: 18px; }

    @media print {
      body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    }
  </style>
</head>
<body>

  <!-- ══ University header ══ -->
  <div class="univ-header">
    <div class="univ-name">বাংলাদেশ প্রকৌশল বিশ্ববিদ্যালয়, ঢাকা</div>
    <div class="meeting-subtitle">
      ${dateBn} তারিখে অনুষ্ঠিত ${councilBn}ের ${serialBn}-তম জরুরী সভার কার্যবিবরণী।
    </div>
  </div>

  <hr class="section-rule">

  <!-- ══ Opening description ══ -->
  ${meeting.description ? `<div class="opening-para rich-content">${meeting.description}</div>` : ''}

  <!-- ══ Members ══ -->
  <div>
    <div class="members-heading">উপস্থিত সদস্যবৃন্দ ঃ</div>
    ${membersHtml}
  </div>

  <!-- ══ Regular Agendas ══ -->
  ${regularAgendas.length > 0 ? `
  <div class="section-gap">
    <div class="agendas-heading">প্রস্তাবসমূহ</div>
    ${agendaBlocks(regularAgendas, false)}
  </div>` : ''}

  <!-- ══ Supplementary Agendas ══ -->
  ${supplAgendas.length > 0 ? `
  <div class="section-gap">
    <div class="agendas-heading">অতিরিক্ত প্রস্তাবসমূহ</div>
    ${agendaBlocks(supplAgendas, true)}
  </div>` : ''}

  <!-- ══ Conclusion ══ -->
  ${meeting.conclusion ? `
  <div class="section-gap">
    <div class="members-heading">সভার সমাপ্তি</div>
    <div class="rich-content">${meeting.conclusion}</div>
  </div>` : ''}

</body>
</html>`
}

// ── Public export ──────────────────────────────────────────────────────────────

export function generateMeetingPdf({ meeting, members, agendas }) {
  const html = buildFullPage({ meeting, members, agendas })

  const iframe = document.createElement('iframe')
  iframe.style.cssText = 'position:fixed;top:0;left:0;width:0;height:0;border:none;'
  document.body.appendChild(iframe)

  return new Promise((resolve, reject) => {
    iframe.onload = () => {
      try {
        iframe.contentWindow.focus()
        iframe.contentWindow.print()
        resolve()
      } catch (e) {
        reject(e)
      } finally {
        setTimeout(() => document.body.removeChild(iframe), 1000)
      }
    }
    iframe.onerror = reject
    iframe.srcdoc = html
  })
}

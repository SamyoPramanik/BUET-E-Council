import { Extension } from '@tiptap/core'

// ── Custom FontSize extension — shared between the interactive RichTextEditor
// and the print/HTML renderer so both parse the exact same `fontSize` mark
// attribute (a bare numeric string, e.g. "16", not "16px"). Commands are named
// setCustomFontSize / unsetCustomFontSize because @tiptap/extension-text-style
// ships its own built-in `fontSize` command group that would otherwise clash
// at the TS type level.
declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    customFontSize: {
      setCustomFontSize: (size: number) => ReturnType
      unsetCustomFontSize: () => ReturnType
    }
  }
}

export const FontSize = Extension.create({
  name: 'customFontSize',
  addOptions() {
    return { types: ['textStyle'] }
  },
  addGlobalAttributes() {
    return [
      {
        types: this.options.types,
        attributes: {
          fontSize: {
            default: null,
            parseHTML: (el: HTMLElement) => el.style.fontSize?.replace('px', '') || null,
            renderHTML: (a: { fontSize?: string }) => (a.fontSize ? { style: `font-size:${a.fontSize}px` } : {}),
          },
        },
      },
    ]
  },
  addCommands() {
    return {
      setCustomFontSize:
        (size: number) =>
        ({ chain }) =>
          chain().setMark('textStyle', { fontSize: String(size) }).run(),
      unsetCustomFontSize:
        () =>
        ({ chain }) =>
          chain().setMark('textStyle', { fontSize: null }).removeEmptyTextStyle().run(),
    }
  },
})

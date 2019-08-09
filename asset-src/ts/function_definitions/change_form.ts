import { render } from 'katex'
import { debug_printer } from './djangocms_equation'

const update_live_element_font_size = (
  debug = true,
  tex_out: HTMLSpanElement | null,
  font_size_value: HTMLInputElement | null,
  font_size_unit: HTMLSelectElement | null
): void => {
  if (tex_out !== null && font_size_value !== null && font_size_unit !== null) {
    const font_size = font_size_value.value + font_size_unit.value
    debug_printer(debug, 'update_live_element_font_size\nfont-size is: ', font_size)
    tex_out.style.fontSize = font_size
  } else {
    debug_printer(debug, 'update_live_element_font_size\nError getting font-size')
    debug_printer(debug, 'font_size_value is: ', font_size_value)
    debug_printer(debug, 'font_size_unit is: ', font_size_unit)
  }
}

const is_in_text_editor = (debug = false) => {
  const ckeditor_iframe: HTMLIFrameElement | null = window.parent.document.querySelector(
    'iframe.cke_dialog_ui_html'
  )
  debug_printer(
    debug,
    'is_in_text_editor\nchange forms parent is: ',
    ckeditor_iframe
  )
  if (ckeditor_iframe === null) {
    return false
  } else {
    return true
  }
}

const use_displayMode_rendering = (debug = false) => {
  const is_in_ckeditor = is_in_text_editor(debug)
  const inline_checkbox: HTMLInputElement | null = document.querySelector(
    '#id_is_inline'
  )
  debug_printer(
    debug,
    'use_displayMode_rendering\ninline_checkbox is: ',
    inline_checkbox
  )
  if (is_in_ckeditor === false) {
    if (inline_checkbox !== null) {
      inline_checkbox.disabled = true
    }
    return true
  } else {
    if (inline_checkbox !== null && inline_checkbox.checked === true) {
      return false
    } else {
      return true
    }
  }
}

const render_text = (
  tex_in: HTMLTextAreaElement | null,
  tex_out: HTMLSpanElement | null,
  debug = false
): void => {
  if (tex_in !== null && tex_out !== null) {
    const tex_code: string = tex_in.value
    const tex_code_lines: number = tex_code.split(/\r\n|\r|\n/).length
    if (tex_code_lines >= 2) {
      tex_in.setAttribute('rows', `${tex_code_lines}`)
    }
    const displayMode = use_displayMode_rendering(true)
    debug_printer(debug, 'render_text\ntex_code to render: ', tex_code)
    render(tex_code, tex_out, {
      throwOnError: false,
      displayMode: displayMode,
    })
  }
}

export const init_live_editor_render = (debug = true): void => {
  const tex_in: HTMLTextAreaElement | null = document.getElementById(
    'id_tex_code'
  ) as HTMLTextAreaElement
  const tex_out: HTMLSpanElement | null = document.getElementById(
    'katex_live_render_out'
  ) as HTMLSpanElement

  tex_in.oninput = () => {
    render_text(tex_in, tex_out, debug)
  }

  const font_size_value: HTMLInputElement | null = document.getElementById(
    'djangocms_equation_font_size_value'
  ) as HTMLInputElement
  const font_size_unit: HTMLSelectElement | null = document.getElementById(
    'djangocms_equation_font_size_unit'
  ) as HTMLSelectElement
  const inline_checkbox: HTMLInputElement | null = document.querySelector(
    '#id_is_inline'
  ) as HTMLInputElement

  const update_font_size = () => {
    update_live_element_font_size(
      debug,
      tex_out,
      font_size_value,
      font_size_unit
    )
  }

  font_size_value.oninput = update_font_size
  font_size_unit.onchange = update_font_size
  inline_checkbox.onchange = () => {
    render_text(tex_in, tex_out, debug)
  }

  update_font_size()
  render_text(tex_in, tex_out, debug)
}

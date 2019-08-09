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
    debug_printer(
      debug,
      'update_live_element_font_size\nfont-size is: ',
      font_size
    )
    tex_out.style.fontSize = font_size
  } else {
    debug_printer(
      debug,
      'update_live_element_font_size\nError getting font-size'
    )
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

const swap_classes = (
  element: HTMLElement,
  remove_classes: string[],
  add_classes: string[]
) => {
  for (let remove_class of remove_classes) {
    element.classList.remove(remove_class)
  }
  for (let add_class of add_classes) {
    element.classList.add(add_class)
  }
}

const change_orientation = (icon_container: HTMLDivElement, debug = true) => {
  const icon: HTMLElement = document.querySelector(
    '.orientation_selector i'
  ) as HTMLElement
  const form_container = document.querySelector(
    '#equationpluginmodel_form > div'
  ) as HTMLDivElement
  const orientation_state: string = icon_container.getAttribute(
    'data-orientation-setting'
  ) as string
  const icon_title_base = 'Selected orintation mode: '
  debug_printer(
    debug,
    'change_orientation_icon\norientation_state is: ',
    orientation_state
  )
  debug_printer(
    debug,
    'change_orientation_icon\form_container is: ',
    form_container
  )
  if (orientation_state === 'auto') {
    icon_container.setAttribute('data-orientation-setting', 'horizontal')
    icon.setAttribute('title', icon_title_base + 'horizontal')
    swap_classes(icon, ['fa-sync-alt'], ['fa-grip-horizontal'])
    swap_classes(form_container, ['vertical_grid'], ['horizontal_grid'])
  } else if (orientation_state === 'horizontal') {
    icon_container.setAttribute('data-orientation-setting', 'vertical')
    icon.setAttribute('title', icon_title_base + 'vertical')
    swap_classes(icon, ['fa-grip-horizontal'], ['fa-grip-vertical'])
    swap_classes(form_container, ['horizontal_grid'], ['vertical_grid'])
  } else {
    icon_container.setAttribute('data-orientation-setting', 'auto')
    icon.setAttribute('title', icon_title_base + 'auto')
    swap_classes(icon, ['fa-grip-vertical'], ['fa-sync-alt'])
    swap_classes(form_container, ['horizontal_grid', 'vertical_grid'], [])
  }
}

export const init_live_editor_render = (debug = true): void => {
  const tex_in: HTMLTextAreaElement = document.getElementById(
    'id_tex_code'
  ) as HTMLTextAreaElement
  const tex_out: HTMLSpanElement = document.getElementById(
    'katex_live_render_out'
  ) as HTMLSpanElement

  tex_in.oninput = () => {
    render_text(tex_in, tex_out, debug)
  }

  const font_size_value: HTMLInputElement = document.getElementById(
    'djangocms_equation_font_size_value'
  ) as HTMLInputElement
  const font_size_unit: HTMLSelectElement = document.getElementById(
    'djangocms_equation_font_size_unit'
  ) as HTMLSelectElement
  const inline_checkbox: HTMLInputElement = document.querySelector(
    '#id_is_inline'
  ) as HTMLInputElement

  const icon_container: HTMLDivElement = document.querySelector(
    '.orientation_selector'
  ) as HTMLDivElement

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
  icon_container.addEventListener('click', () => {
    change_orientation(icon_container, (debug = true))
  })

  update_font_size()
  render_text(tex_in, tex_out, debug)
}

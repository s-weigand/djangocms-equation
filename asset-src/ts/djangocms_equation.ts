import { render } from 'katex'
import renderMathInElement, {
  RenderMathInElementOptions,
} from 'katex/dist/contrib/auto-render'

export const debug_printer = (debug = true, ...args: any[]): void => {
  if (process.env.NODE_ENV === 'development' && debug) {
    // Or, `process.env.NODE_ENV !== 'production'`
    // Only runs in development and will be stripped from production build.
    console.log(...args)
  }
}

const katex_delimiters_setting: RenderMathInElementOptions = {
  delimiters: [
    { left: '$$', right: '$$', display: true },
    { left: '\\[', right: '\\]', display: true },
    { left: '$', right: '$', display: false },
    { left: '\\(', right: '\\)', display: false },
  ],
}

export const render_full_page = (target = document.body): void => {
  renderMathInElement(target, {
    ...katex_delimiters_setting,
  })
}

const update_live_element_font_size = (
  debug = true,
  tex_out: HTMLSpanElement | null,
  font_size_value: HTMLInputElement | null,
  font_size_unit: HTMLSelectElement | null
): void => {
  if (tex_out !== null && font_size_value !== null && font_size_unit !== null) {
    const font_size = font_size_value.value + font_size_unit.value
    debug_printer(debug, 'updating live render font-size to: ', font_size)
    tex_out.style.fontSize = font_size
  } else {
    debug_printer(debug, 'Error getting font-size')
    debug_printer(debug, 'font_size_value is: ', font_size_value)
    debug_printer(debug, 'font_size_unit is: ', font_size_unit)
  }
}

export const init_render_main_page = (debug = true): void => {
  debug_printer(debug, 'init_render_main_page did run')
  document.addEventListener('DOMContentLoaded', function(event) {
    render_full_page()
    // window needs to be cast to any since the vartiable 'CMS'
    // gets injected to windows by the javascript code of django-cms
    const CMS = (window as any).CMS
    if (CMS !== undefined) {
      CMS.$(window).on('cms-content-refresh', function() {
        render_full_page()
      })
    }

    debug_printer(debug, 'page loaded')
    let cms_btn: HTMLAnchorElement | null = document.querySelector(
      '.cms-toolbar-item-cms-mode-switcher a'
    )
    const render_structure_content_on_show = (): void => {
      let structure_content: HTMLDivElement | null = document.querySelector(
        '.cms-structure-content'
      ) as HTMLDivElement
      if (structure_content !== null) {
        // check if the element is visible
        if (structure_content.offsetParent !== null) {
          debug_printer(debug, 'cms_btn clicked => rendering all')
          renderMathInElement(structure_content, {
            throwOnError: false,
            ...katex_delimiters_setting,
          })
        } else {
          debug_printer(debug, 'need delay')
          setTimeout(render_structure_content_on_show, 200)
        }
      }
    }
    debug_printer(debug, 'cms_btn is:', cms_btn)
    if (cms_btn !== null) {
      // somehow onclick doesn't work, onfocus will be the hotfix for now
      cms_btn.onfocus = render_structure_content_on_show
    }
  })
}

export const init_live_editor_render = (debug = true): void => {
  document.addEventListener('DOMContentLoaded', function(event) {
    let tex_in: HTMLTextAreaElement | null = document.getElementById(
      'id_tex_code'
    ) as HTMLTextAreaElement
    let tex_out: HTMLSpanElement | null = document.getElementById(
      'katex_live_render_out'
    ) as HTMLSpanElement
    const render_text = (): void => {
      if (tex_in !== null && tex_out !== null) {
        let tex_code: string = tex_in.value
        let tex_code_lines: number = tex_code.split(/\r\n|\r|\n/).length
        if(tex_code_lines>=2){
          tex_in.setAttribute("rows", `${tex_code_lines}`)
        }
        debug_printer(debug, 'tex_code to render: ', tex_code)
        render(tex_code, tex_out, {
          throwOnError: false,
        })
      }
    }

    tex_in.oninput = render_text

    const font_size_value: HTMLInputElement | null = document.getElementById(
      'djangocms_equation_font_size_value'
    ) as HTMLInputElement
    const font_size_unit: HTMLSelectElement | null = document.getElementById(
      'djangocms_equation_font_size_unit'
    ) as HTMLSelectElement

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

    update_font_size()
    render_text()
  })
}

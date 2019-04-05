import { render } from 'katex'
import renderMathInElement from 'katex/dist/contrib/auto-render'

const debug_printer = (debug = true, ...args: any[]) => {
  // if (process.env.NODE_ENV === "development" && debug) {
  // Or, `process.env.NODE_ENV !== 'production'`
  // Only runs in development and will be stripped from production build.
  console.log(...args)
  // }
}

const katex_delimiters_setting = {
  delimiters: [
    { left: '$$', right: '$$', display: true },
    { left: '\\[', right: '\\]', display: true },
    { left: '$', right: '$', display: false },
    { left: '\\(', right: '\\)', display: false },
  ],
}

const render_full_page = () => {
  renderMathInElement(document.body, {
    ...katex_delimiters_setting,
  })
}

export const init_render_main_page = (debug = true) => {
  debug_printer(debug, 'init_render_main_page did run')
  document.addEventListener('DOMContentLoaded', function(event) {
    render_full_page()
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
    const render_on_show = () => {
      // TODO:
      // needs to be done for ".model-equationpluginmodel a" aswell
      let structure_side_bar = document.querySelector(
        '.cms-structure-content'
      ) as HTMLDivElement
      // check if the element is visible
      if (structure_side_bar.offsetParent !== null) {
        debug_printer(debug, 'cms_btn clicked => rendering all')
        renderMathInElement(structure_side_bar, {
          throwOnError: false,
          ...katex_delimiters_setting,
        })
      } else {
        debug_printer(debug, 'need delay')
        setTimeout(render_on_show, 200)
      }
    }
    debug_printer(debug, 'cms_btn is:', cms_btn)
    if (cms_btn !== null) {
      // somehow onclick doesn't work, onfocus will be the hotfix for now
      cms_btn.onfocus  = render_on_show
    }
  })
}

export const init_live_editor_render = (debug = false) => {
  document.addEventListener('DOMContentLoaded', function(event) {
    let tex_in = document.getElementById('id_tex_code') as HTMLTextAreaElement
    let tex_out = document.getElementById(
      'katex_live_render_out'
    ) as HTMLSpanElement
    const render_text = () => {
      let tex_code = tex_in.value
      debug_printer(debug, 'tex_code to render: ', tex_code)
      render(tex_code, tex_out, {
        throwOnError: false,
      })
    }

    tex_in.oninput = render_text
    render_text()
  })
}
